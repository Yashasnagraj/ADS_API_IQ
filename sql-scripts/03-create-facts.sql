USE MarketingIQ;
GO

-- Campaign Performance Fact Table
IF OBJECT_ID('dw.FactCampaignPerformance', 'U') IS NOT NULL DROP TABLE dw.FactCampaignPerformance;
CREATE TABLE dw.FactCampaignPerformance (
    PerformanceKey INT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    CampaignKey INT NOT NULL,
    Impressions BIGINT DEFAULT 0,
    Clicks BIGINT DEFAULT 0,
    Cost DECIMAL(15,2) DEFAULT 0,
    Conversions INT DEFAULT 0,
    ConversionValue DECIMAL(15,2) DEFAULT 0,
    CTR AS (CASE WHEN Impressions > 0 THEN CAST(Clicks AS FLOAT) / Impressions ELSE 0 END) PERSISTED,
    CPC AS (CASE WHEN Clicks > 0 THEN Cost / Clicks ELSE 0 END) PERSISTED,
    CPM AS (CASE WHEN Impressions > 0 THEN (Cost * 1000) / Impressions ELSE 0 END) PERSISTED,
    ConversionRate AS (CASE WHEN Clicks > 0 THEN CAST(Conversions AS FLOAT) / Clicks ELSE 0 END) PERSISTED,
    CostPerConversion AS (CASE WHEN Conversions > 0 THEN Cost / Conversions ELSE 0 END) PERSISTED,
    ROAS AS (CASE WHEN Cost > 0 THEN ConversionValue / Cost ELSE 0 END) PERSISTED,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DateKey) REFERENCES dw.DimDate(DateKey),
    FOREIGN KEY (CampaignKey) REFERENCES dw.DimCampaign(CampaignKey)
);

-- Ad Group Performance Fact Table
IF OBJECT_ID('dw.FactAdGroupPerformance', 'U') IS NOT NULL DROP TABLE dw.FactAdGroupPerformance;
CREATE TABLE dw.FactAdGroupPerformance (
    PerformanceKey INT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    AdGroupKey INT NOT NULL,
    CampaignKey INT NOT NULL,
    Impressions BIGINT DEFAULT 0,
    Clicks BIGINT DEFAULT 0,
    Cost DECIMAL(15,2) DEFAULT 0,
    Conversions INT DEFAULT 0,
    ConversionValue DECIMAL(15,2) DEFAULT 0,
    AvgPosition DECIMAL(3,1),
    CTR AS (CASE WHEN Impressions > 0 THEN CAST(Clicks AS FLOAT) / Impressions ELSE 0 END) PERSISTED,
    CPC AS (CASE WHEN Clicks > 0 THEN Cost / Clicks ELSE 0 END) PERSISTED,
    CPM AS (CASE WHEN Impressions > 0 THEN (Cost * 1000) / Impressions ELSE 0 END) PERSISTED,
    ConversionRate AS (CASE WHEN Clicks > 0 THEN CAST(Conversions AS FLOAT) / Clicks ELSE 0 END) PERSISTED,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DateKey) REFERENCES dw.DimDate(DateKey),
    FOREIGN KEY (AdGroupKey) REFERENCES dw.DimAdGroup(AdGroupKey),
    FOREIGN KEY (CampaignKey) REFERENCES dw.DimCampaign(CampaignKey)
);

-- Keyword Performance Fact Table
IF OBJECT_ID('dw.FactKeywordPerformance', 'U') IS NOT NULL DROP TABLE dw.FactKeywordPerformance;
CREATE TABLE dw.FactKeywordPerformance (
    PerformanceKey INT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    KeywordKey INT NOT NULL,
    AdGroupKey INT NOT NULL,
    CampaignKey INT NOT NULL,
    Impressions BIGINT DEFAULT 0,
    Clicks BIGINT DEFAULT 0,
    Cost DECIMAL(15,2) DEFAULT 0,
    Conversions INT DEFAULT 0,
    ConversionValue DECIMAL(15,2) DEFAULT 0,
    AvgPosition DECIMAL(3,1),
    QualityScore INT,
    CTR AS (CASE WHEN Impressions > 0 THEN CAST(Clicks AS FLOAT) / Impressions ELSE 0 END) PERSISTED,
    CPC AS (CASE WHEN Clicks > 0 THEN Cost / Clicks ELSE 0 END) PERSISTED,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DateKey) REFERENCES dw.DimDate(DateKey),
    FOREIGN KEY (KeywordKey) REFERENCES dw.DimKeyword(KeywordKey),
    FOREIGN KEY (AdGroupKey) REFERENCES dw.DimAdGroup(AdGroupKey),
    FOREIGN KEY (CampaignKey) REFERENCES dw.DimCampaign(CampaignKey)
);

-- Ad Performance Fact Table
IF OBJECT_ID('dw.FactAdPerformance', 'U') IS NOT NULL DROP TABLE dw.FactAdPerformance;
CREATE TABLE dw.FactAdPerformance (
    PerformanceKey INT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    AdKey INT NOT NULL,
    AdGroupKey INT NOT NULL,
    CampaignKey INT NOT NULL,
    DeviceKey INT,
    GeographyKey INT,
    Impressions BIGINT DEFAULT 0,
    Clicks BIGINT DEFAULT 0,
    Cost DECIMAL(15,2) DEFAULT 0,
    Conversions INT DEFAULT 0,
    ConversionValue DECIMAL(15,2) DEFAULT 0,
    VideoViews INT DEFAULT 0,
    VideoQuartile25 INT DEFAULT 0,
    VideoQuartile50 INT DEFAULT 0,
    VideoQuartile75 INT DEFAULT 0,
    VideoQuartile100 INT DEFAULT 0,
    CTR AS (CASE WHEN Impressions > 0 THEN CAST(Clicks AS FLOAT) / Impressions ELSE 0 END) PERSISTED,
    CPC AS (CASE WHEN Clicks > 0 THEN Cost / Clicks ELSE 0 END) PERSISTED,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DateKey) REFERENCES dw.DimDate(DateKey),
    FOREIGN KEY (AdKey) REFERENCES dw.DimAd(AdKey),
    FOREIGN KEY (AdGroupKey) REFERENCES dw.DimAdGroup(AdGroupKey),
    FOREIGN KEY (CampaignKey) REFERENCES dw.DimCampaign(CampaignKey),
    FOREIGN KEY (DeviceKey) REFERENCES dw.DimDevice(DeviceKey),
    FOREIGN KEY (GeographyKey) REFERENCES dw.DimGeography(GeographyKey)
);

-- Create indexes for better query performance
CREATE INDEX IX_FactCampaignPerformance_DateKey ON dw.FactCampaignPerformance(DateKey);
CREATE INDEX IX_FactCampaignPerformance_CampaignKey ON dw.FactCampaignPerformance(CampaignKey);

CREATE INDEX IX_FactAdGroupPerformance_DateKey ON dw.FactAdGroupPerformance(DateKey);
CREATE INDEX IX_FactAdGroupPerformance_AdGroupKey ON dw.FactAdGroupPerformance(AdGroupKey);

CREATE INDEX IX_FactKeywordPerformance_DateKey ON dw.FactKeywordPerformance(DateKey);
CREATE INDEX IX_FactKeywordPerformance_KeywordKey ON dw.FactKeywordPerformance(KeywordKey);

CREATE INDEX IX_FactAdPerformance_DateKey ON dw.FactAdPerformance(DateKey);
CREATE INDEX IX_FactAdPerformance_AdKey ON dw.FactAdPerformance(AdKey);