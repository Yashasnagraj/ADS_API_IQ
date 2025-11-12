"""
Industry Benchmarks API Routes
Provides database-driven industry benchmarks for AI intelligence
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.schemas.metrics import BenchmarkResponse, BenchmarkListResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/benchmarks",
    tags=["benchmarks"]
)


@router.get("/", response_model=BenchmarkListResponse)
async def get_benchmarks(
    industry_vertical: str = Query("general", description="Industry vertical: general, ecommerce, saas, b2b, local"),
    platform: str = Query("google_ads", description="Platform: google_ads, meta_ads, ga4, shopify, unified"),
    metrics: Optional[str] = Query(None, description="Comma-separated list of metrics to filter"),
    country_code: str = Query("ALL", description="Country code filter"),
    db: Session = Depends(get_db)
):
    """
    Get active industry benchmarks for specified industry and platform

    Query Parameters:
    - industry_vertical: Type of business (general, ecommerce, saas, etc.)
    - platform: Marketing platform (google_ads, meta_ads, ga4, etc.)
    - metrics: Optional comma-separated list of specific metrics (ctr,cpc,roas)
    - country_code: Geographic filter (default: ALL)

    Returns:
    - List of active benchmarks with thresholds and confidence scores
    """
    try:
        # Build query
        query = text("""
            SELECT
                benchmark_id,
                industry_vertical,
                industry_sub_vertical,
                platform,
                metric_name,
                metric_category,
                benchmark_value,
                benchmark_unit,
                excellent_threshold,
                good_threshold,
                average_threshold,
                poor_threshold,
                data_source,
                sample_size,
                confidence_score,
                country_code,
                currency,
                valid_from,
                valid_until,
                notes
            FROM industry_benchmarks
            WHERE industry_vertical = :industry_vertical
                AND platform = :platform
                AND (valid_until IS NULL OR valid_until >= DATE('now'))
                AND valid_from <= DATE('now')
                AND country_code IN (:country_code, 'ALL')
            ORDER BY confidence_score DESC, valid_from DESC
        """)

        params = {
            "industry_vertical": industry_vertical,
            "platform": platform,
            "country_code": country_code
        }

        result = db.execute(query, params).fetchall()

        # Convert to dict list
        benchmarks = []
        for row in result:
            benchmark = {
                "benchmark_id": row[0],
                "industry_vertical": row[1],
                "industry_sub_vertical": row[2],
                "platform": row[3],
                "metric_name": row[4],
                "metric_category": row[5],
                "benchmark_value": float(row[6]),
                "benchmark_unit": row[7],
                "excellent_threshold": float(row[8]) if row[8] else None,
                "good_threshold": float(row[9]) if row[9] else None,
                "average_threshold": float(row[10]) if row[10] else None,
                "poor_threshold": float(row[11]) if row[11] else None,
                "data_source": row[12],
                "sample_size": row[13],
                "confidence_score": row[14],
                "country_code": row[15],
                "currency": row[16],
                "valid_from": row[17],
                "valid_until": row[18],
                "notes": row[19]
            }

            # Filter by specific metrics if requested
            if metrics:
                metric_list = [m.strip() for m in metrics.split(",")]
                if benchmark["metric_name"] in metric_list:
                    benchmarks.append(benchmark)
            else:
                benchmarks.append(benchmark)

        return {
            "industry_vertical": industry_vertical,
            "platform": platform,
            "country_code": country_code,
            "benchmarks_count": len(benchmarks),
            "benchmarks": benchmarks
        }

    except Exception as e:
        logger.error(f"Error fetching benchmarks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch benchmarks: {str(e)}")


@router.get("/{metric_name}", response_model=BenchmarkResponse)
async def get_benchmark_by_metric(
    metric_name: str,
    industry_vertical: str = Query("general", description="Industry vertical"),
    platform: str = Query("google_ads", description="Platform"),
    country_code: str = Query("ALL", description="Country code"),
    db: Session = Depends(get_db)
):
    """
    Get benchmark for a specific metric

    Path Parameters:
    - metric_name: The specific metric (ctr, cpc, roas, etc.)

    Query Parameters:
    - industry_vertical: Type of business
    - platform: Marketing platform
    - country_code: Geographic filter

    Returns:
    - Single benchmark with all thresholds and metadata
    """
    try:
        query = text("""
            SELECT
                benchmark_id,
                industry_vertical,
                industry_sub_vertical,
                platform,
                metric_name,
                metric_category,
                benchmark_value,
                benchmark_unit,
                excellent_threshold,
                good_threshold,
                average_threshold,
                poor_threshold,
                data_source,
                sample_size,
                confidence_score,
                country_code,
                currency,
                valid_from,
                valid_until,
                notes
            FROM industry_benchmarks
            WHERE metric_name = :metric_name
                AND industry_vertical = :industry_vertical
                AND platform = :platform
                AND (valid_until IS NULL OR valid_until >= DATE('now'))
                AND valid_from <= DATE('now')
                AND country_code IN (:country_code, 'ALL')
            ORDER BY confidence_score DESC, valid_from DESC
            LIMIT 1
        """)

        params = {
            "metric_name": metric_name,
            "industry_vertical": industry_vertical,
            "platform": platform,
            "country_code": country_code
        }

        result = db.execute(query, params).fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No benchmark found for metric '{metric_name}' in industry '{industry_vertical}' on platform '{platform}'"
            )

        return {
            "benchmark_id": result[0],
            "industry_vertical": result[1],
            "industry_sub_vertical": result[2],
            "platform": result[3],
            "metric_name": result[4],
            "metric_category": result[5],
            "benchmark_value": float(result[6]),
            "benchmark_unit": result[7],
            "excellent_threshold": float(result[8]) if result[8] else None,
            "good_threshold": float(result[9]) if result[9] else None,
            "average_threshold": float(result[10]) if result[10] else None,
            "poor_threshold": float(result[11]) if result[11] else None,
            "data_source": result[12],
            "sample_size": result[13],
            "confidence_score": result[14],
            "country_code": result[15],
            "currency": result[16],
            "valid_from": result[17],
            "valid_until": result[18],
            "notes": result[19]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch benchmark: {str(e)}")


@router.post("/", status_code=201)
async def create_benchmark(
    industry_vertical: str,
    platform: str,
    metric_name: str,
    benchmark_value: float,
    benchmark_unit: str = "ratio",
    metric_category: Optional[str] = None,
    excellent_threshold: Optional[float] = None,
    good_threshold: Optional[float] = None,
    average_threshold: Optional[float] = None,
    poor_threshold: Optional[float] = None,
    data_source: str = "manual",
    confidence_score: int = 80,
    country_code: str = "ALL",
    currency: str = "USD",
    valid_from: str = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new industry benchmark (Admin endpoint)

    This endpoint should be protected with authentication in production
    """
    try:
        from datetime import datetime

        if not valid_from:
            valid_from = datetime.now().strftime("%Y-%m-%d")

        query = text("""
            INSERT INTO industry_benchmarks
            (industry_vertical, platform, metric_name, metric_category, benchmark_value, benchmark_unit,
             excellent_threshold, good_threshold, average_threshold, poor_threshold,
             data_source, confidence_score, country_code, currency, valid_from, notes, created_by)
            VALUES
            (:industry_vertical, :platform, :metric_name, :metric_category, :benchmark_value, :benchmark_unit,
             :excellent_threshold, :good_threshold, :average_threshold, :poor_threshold,
             :data_source, :confidence_score, :country_code, :currency, :valid_from, :notes, 'api')
        """)

        params = {
            "industry_vertical": industry_vertical,
            "platform": platform,
            "metric_name": metric_name,
            "metric_category": metric_category,
            "benchmark_value": benchmark_value,
            "benchmark_unit": benchmark_unit,
            "excellent_threshold": excellent_threshold,
            "good_threshold": good_threshold,
            "average_threshold": average_threshold,
            "poor_threshold": poor_threshold,
            "data_source": data_source,
            "confidence_score": confidence_score,
            "country_code": country_code,
            "currency": currency,
            "valid_from": valid_from,
            "notes": notes
        }

        db.execute(query, params)
        db.commit()

        return {
            "message": "Benchmark created successfully",
            "metric_name": metric_name,
            "industry_vertical": industry_vertical,
            "platform": platform
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create benchmark: {str(e)}")


@router.put("/{benchmark_id}")
async def update_benchmark(
    benchmark_id: int,
    benchmark_value: Optional[float] = None,
    excellent_threshold: Optional[float] = None,
    good_threshold: Optional[float] = None,
    average_threshold: Optional[float] = None,
    poor_threshold: Optional[float] = None,
    confidence_score: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing benchmark (Admin endpoint)

    This endpoint should be protected with authentication in production
    """
    try:
        # Build dynamic UPDATE query
        update_fields = []
        params = {"benchmark_id": benchmark_id}

        if benchmark_value is not None:
            update_fields.append("benchmark_value = :benchmark_value")
            params["benchmark_value"] = benchmark_value

        if excellent_threshold is not None:
            update_fields.append("excellent_threshold = :excellent_threshold")
            params["excellent_threshold"] = excellent_threshold

        if good_threshold is not None:
            update_fields.append("good_threshold = :good_threshold")
            params["good_threshold"] = good_threshold

        if average_threshold is not None:
            update_fields.append("average_threshold = :average_threshold")
            params["average_threshold"] = average_threshold

        if poor_threshold is not None:
            update_fields.append("poor_threshold = :poor_threshold")
            params["poor_threshold"] = poor_threshold

        if confidence_score is not None:
            update_fields.append("confidence_score = :confidence_score")
            params["confidence_score"] = confidence_score

        if notes is not None:
            update_fields.append("notes = :notes")
            params["notes"] = notes

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        query = text(f"""
            UPDATE industry_benchmarks
            SET {", ".join(update_fields)}
            WHERE benchmark_id = :benchmark_id
        """)

        result = db.execute(query, params)
        db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Benchmark with ID {benchmark_id} not found")

        return {"message": "Benchmark updated successfully", "benchmark_id": benchmark_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update benchmark: {str(e)}")
