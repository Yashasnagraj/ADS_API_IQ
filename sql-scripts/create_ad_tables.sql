-- Create tables for Ad Creatives and Search Terms data
-- Run this script in your SQL Server database

USE MarketingDW;
GO

-- Create DimAd table for ad creatives
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimAd' AND schema_id = SCHEMA_ID('dw'))
BEGIN
    CREATE TABLE dw.DimAd (
        AdKey INT IDENTITY(1,1) PRIMARY KEY,
        AdID BIGINT NOT NULL,
        AdType VARCHAR(50),
        Headlines NVARCHAR(MAX),
        Descriptions NVARCHAR(MAX),
        FinalURL VARCHAR(2048),
        DisplayURL VARCHAR(255),
        AdGroupID BIGINT,
        AdStatus VARCHAR(50),
        ApprovalStatus VARCHAR(50),
        IsActive BIT DEFAULT 1,
        CreatedDate DATETIME DEFAULT GETDATE(),
        UpdatedDate DATETIME DEFAULT GETDATE(),
        CONSTRAINT UQ_DimAd_AdID UNIQUE(AdID)
    );

    CREATE INDEX IX_DimAd_AdGroupID ON dw.DimAd(AdGroupID);
    CREATE INDEX IX_DimAd_AdStatus ON dw.DimAd(AdStatus);
END
GO

-- Create FactAdPerformance table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactAdPerformance' AND schema_id = SCHEMA_ID('dw'))
BEGIN
    CREATE TABLE dw.FactAdPerformance (
        AdPerformanceKey INT IDENTITY(1,1) PRIMARY KEY,
        DateKey INT NOT NULL,
        AdKey INT,
        AdID BIGINT,
        AdGroupKey INT,
        AdGroupID BIGINT,
        Impressions INT DEFAULT 0,
        Clicks INT DEFAULT 0,
        Cost DECIMAL(18,2) DEFAULT 0,
        Conversions INT DEFAULT 0,
        ConversionValue DECIMAL(18,2) DEFAULT 0,
        AllConversions INT DEFAULT 0,
        CTR AS (CASE WHEN Impressions > 0 THEN CAST(Clicks AS FLOAT) / Impressions * 100 ELSE 0 END),
        CPC AS (CASE WHEN Clicks > 0 THEN Cost / Clicks ELSE 0 END),
        ConversionRate AS (CASE WHEN Clicks > 0 THEN CAST(Conversions AS FLOAT) / Clicks * 100 ELSE 0 END),
        ROAS AS (CASE WHEN Cost > 0 THEN ConversionValue / Cost ELSE 0 END),
        CreatedDate DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_FactAdPerformance_DateKey ON dw.FactAdPerformance(DateKey);
    CREATE INDEX IX_FactAdPerformance_AdKey ON dw.FactAdPerformance(AdKey);
    CREATE INDEX IX_FactAdPerformance_AdGroupKey ON dw.FactAdPerformance(AdGroupKey);
END
GO

-- Create FactSearchTermPerformance table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactSearchTermPerformance' AND schema_id = SCHEMA_ID('dw'))
BEGIN
    CREATE TABLE dw.FactSearchTermPerformance (
        SearchTermKey INT IDENTITY(1,1) PRIMARY KEY,
        DateKey INT NOT NULL,
        Date DATE,
        SearchTerm NVARCHAR(500),
        CampaignID BIGINT,
        AdGroupID BIGINT,
        Status VARCHAR(50),
        TriggeringKeyword NVARCHAR(255),
        MatchType VARCHAR(50),
        Impressions INT DEFAULT 0,
        Clicks INT DEFAULT 0,
        Cost DECIMAL(18,2) DEFAULT 0,
        Conversions INT DEFAULT 0,
        ConversionValue DECIMAL(18,2) DEFAULT 0,
        CTR DECIMAL(10,4) DEFAULT 0,
        AvgCPC DECIMAL(18,2) DEFAULT 0,
        ConversionRate DECIMAL(10,4) DEFAULT 0,
        CreatedDate DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_FactSearchTermPerformance_DateKey ON dw.FactSearchTermPerformance(DateKey);
    CREATE INDEX IX_FactSearchTermPerformance_SearchTerm ON dw.FactSearchTermPerformance(SearchTerm);
    CREATE INDEX IX_FactSearchTermPerformance_CampaignID ON dw.FactSearchTermPerformance(CampaignID);
    CREATE INDEX IX_FactSearchTermPerformance_AdGroupID ON dw.FactSearchTermPerformance(AdGroupID);
    CREATE INDEX IX_FactSearchTermPerformance_Cost ON dw.FactSearchTermPerformance(Cost);
END
GO

-- Create view for ad performance summary
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_AdPerformanceSummary' AND schema_id = SCHEMA_ID('dw'))
    DROP VIEW dw.vw_AdPerformanceSummary;
GO

CREATE VIEW dw.vw_AdPerformanceSummary AS
SELECT
    a.AdID,
    a.AdType,
    a.Headlines,
    a.Descriptions,
    a.FinalURL,
    ag.AdGroupName,
    c.CampaignName,
    SUM(f.Impressions) as TotalImpressions,
    SUM(f.Clicks) as TotalClicks,
    SUM(f.Cost) as TotalCost,
    SUM(f.Conversions) as TotalConversions,
    AVG(f.CTR) as AvgCTR,
    AVG(f.CPC) as AvgCPC,
    AVG(f.ConversionRate) as AvgConversionRate,
    AVG(f.ROAS) as AvgROAS
FROM dw.DimAd a
LEFT JOIN dw.FactAdPerformance f ON a.AdKey = f.AdKey
LEFT JOIN dw.DimAdGroup ag ON a.AdGroupID = ag.AdGroupID
LEFT JOIN dw.DimCampaign c ON ag.CampaignID = c.CampaignID
GROUP BY a.AdID, a.AdType, a.Headlines, a.Descriptions, a.FinalURL, ag.AdGroupName, c.CampaignName;
GO

-- Create view for search term insights
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_SearchTermInsights' AND schema_id = SCHEMA_ID('dw'))
    DROP VIEW dw.vw_SearchTermInsights;
GO

CREATE VIEW dw.vw_SearchTermInsights AS
SELECT
    st.SearchTerm,
    COUNT(DISTINCT st.CampaignID) as CampaignCount,
    COUNT(DISTINCT st.AdGroupID) as AdGroupCount,
    SUM(st.Impressions) as TotalImpressions,
    SUM(st.Clicks) as TotalClicks,
    SUM(st.Cost) as TotalCost,
    SUM(st.Conversions) as TotalConversions,
    AVG(st.CTR) as AvgCTR,
    AVG(st.AvgCPC) as AvgCPC,
    AVG(st.ConversionRate) as AvgConversionRate,
    CASE
        WHEN SUM(st.Cost) > 100 AND SUM(st.Conversions) = 0 THEN 'Add as Negative'
        WHEN AVG(st.ConversionRate) > 5 THEN 'High Performer'
        WHEN AVG(st.CTR) < 1 THEN 'Low Relevance'
        ELSE 'Monitor'
    END as Recommendation
FROM dw.FactSearchTermPerformance st
GROUP BY st.SearchTerm
HAVING SUM(st.Impressions) > 10;
GO

PRINT 'Ad and Search Term tables created successfully!';
GO