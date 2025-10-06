"""
Monitoring and Health Check API Extensions
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import psutil
import pyodbc
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from loguru import logger
from db_connection import db

def add_monitoring_endpoints(app: FastAPI):
    """Add monitoring endpoints to FastAPI app"""

    @app.get("/health/detailed")
    async def detailed_health():
        """Detailed health check with component status"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "components": {}
        }

        # Database health
        try:
            result = db.execute_query("SELECT @@VERSION as version, DB_NAME() as database")
            health_status["components"]["database"] = {
                "status": "healthy",
                "database": result[0][1] if result else "unknown"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"

        # System resources
        try:
            health_status["components"]["system"] = {
                "status": "healthy",
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }

            # Alert if resources are high
            if health_status["components"]["system"]["cpu_percent"] > 80:
                health_status["components"]["system"]["status"] = "warning"
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["components"]["system"] = {
                "status": "unknown",
                "error": str(e)
            }

        return health_status

    @app.get("/metrics", response_class=PlainTextResponse)
    async def prometheus_metrics():
        """Prometheus-compatible metrics endpoint"""
        metrics = []

        try:
            # Database metrics
            db_metrics = db.execute_query("""
                SELECT
                    COUNT(*) as total_campaigns,
                    SUM(CASE WHEN IsActive = 1 THEN 1 ELSE 0 END) as active_campaigns
                FROM dw.DimCampaign
            """)

            if db_metrics:
                metrics.append(f"marketingiq_campaigns_total {db_metrics[0][0]}")
                metrics.append(f"marketingiq_campaigns_active {db_metrics[0][1]}")

            # Performance metrics
            perf_metrics = db.execute_query("""
                SELECT
                    COUNT(*) as record_count,
                    SUM(Impressions) as total_impressions,
                    SUM(Clicks) as total_clicks,
                    SUM(Cost) as total_cost,
                    SUM(Conversions) as total_conversions
                FROM dw.FactCampaignPerformance
                WHERE DateKey = CAST(CONVERT(varchar(8), GETDATE(), 112) as INT)
            """)

            if perf_metrics and perf_metrics[0][0] > 0:
                metrics.append(f"marketingiq_daily_records {perf_metrics[0][0]}")
                metrics.append(f"marketingiq_daily_impressions {perf_metrics[0][1] or 0}")
                metrics.append(f"marketingiq_daily_clicks {perf_metrics[0][2] or 0}")
                metrics.append(f"marketingiq_daily_cost {perf_metrics[0][3] or 0}")
                metrics.append(f"marketingiq_daily_conversions {perf_metrics[0][4] or 0}")

            # System metrics
            metrics.append(f"marketingiq_cpu_percent {psutil.cpu_percent()}")
            metrics.append(f"marketingiq_memory_percent {psutil.virtual_memory().percent}")
            metrics.append(f"marketingiq_disk_percent {psutil.disk_usage('/').percent}")

        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            metrics.append(f"# Error generating metrics: {e}")

        return "\n".join(metrics)

    @app.get("/monitoring/database-stats")
    async def database_statistics():
        """Get database statistics and performance metrics"""
        try:
            stats = {}

            # Table sizes
            table_sizes = db.execute_query("""
                SELECT
                    s.name + '.' + t.name AS table_name,
                    p.rows AS row_count,
                    SUM(a.total_pages) * 8 / 1024.0 AS size_mb
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                INNER JOIN sys.indexes i ON t.object_id = i.object_id
                INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                WHERE s.name = 'dw'
                GROUP BY s.name, t.name, p.rows
                ORDER BY size_mb DESC
            """)

            stats["table_sizes"] = [
                {
                    "table": row[0],
                    "rows": row[1],
                    "size_mb": float(row[2]) if row[2] else 0
                }
                for row in table_sizes
            ]

            # Connection info
            conn_info = db.execute_query("""
                SELECT
                    COUNT(*) as connection_count,
                    DB_NAME() as database_name,
                    @@SERVERNAME as server_name
                FROM sys.dm_exec_connections
                WHERE database_id = DB_ID()
            """)

            if conn_info:
                stats["connections"] = {
                    "count": conn_info[0][0],
                    "database": conn_info[0][1],
                    "server": conn_info[0][2]
                }

            # Query statistics
            query_stats = db.execute_query("""
                SELECT TOP 10
                    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1,
                        ((CASE qs.statement_end_offset
                            WHEN -1 THEN DATALENGTH(qt.text)
                            ELSE qs.statement_end_offset
                        END - qs.statement_start_offset)/2)+1) AS query_text,
                    qs.execution_count,
                    qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
                    qs.total_elapsed_time / qs.execution_count / 1000000.0 AS avg_elapsed_time_sec
                FROM sys.dm_exec_query_stats qs
                CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
                WHERE qt.dbid = DB_ID()
                ORDER BY qs.total_elapsed_time DESC
            """)

            stats["top_queries"] = [
                {
                    "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                    "execution_count": row[1],
                    "avg_logical_reads": row[2],
                    "avg_elapsed_time_sec": float(row[3]) if row[3] else 0
                }
                for row in query_stats
            ] if query_stats else []

            return stats

        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/monitoring/etl-status")
    async def etl_status():
        """Get ETL pipeline status and last run information"""
        try:
            # Check last data load
            last_load = db.execute_query("""
                SELECT
                    MAX(CreatedDate) as last_load_time,
                    COUNT(DISTINCT CAST(CreatedDate as DATE)) as load_days,
                    COUNT(*) as total_records
                FROM dw.FactCampaignPerformance
                WHERE CreatedDate >= DATEADD(DAY, -7, GETDATE())
            """)

            # Data freshness
            freshness = db.execute_query("""
                SELECT
                    MAX(d.Date) as latest_data_date,
                    DATEDIFF(HOUR, MAX(d.Date), GETDATE()) as hours_behind
                FROM dw.FactCampaignPerformance f
                JOIN dw.DimDate d ON f.DateKey = d.DateKey
            """)

            status = {
                "last_load": last_load[0][0].isoformat() if last_load and last_load[0][0] else None,
                "load_days_past_week": last_load[0][1] if last_load else 0,
                "records_past_week": last_load[0][2] if last_load else 0,
                "latest_data_date": freshness[0][0].isoformat() if freshness and freshness[0][0] else None,
                "hours_behind": freshness[0][1] if freshness and freshness[0][1] else None,
                "status": "healthy" if freshness and freshness[0][1] and freshness[0][1] < 48 else "stale"
            }

            return status

        except Exception as e:
            logger.error(f"Error getting ETL status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    return app