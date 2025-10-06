USE MarketingIQ;
GO

-- Date Dimension
IF OBJECT_ID('dw.DimDate', 'U') IS NOT NULL DROP TABLE dw.DimDate;
CREATE TABLE dw.DimDate (
    DateKey INT PRIMARY KEY,
    Date DATE NOT NULL UNIQUE,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Month INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    Week INT NOT NULL,
    DayOfWeek INT NOT NULL,
    DayName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL,
    FiscalYear INT,
    FiscalQuarter INT
);

-- Campaign Dimension
IF OBJECT_ID('dw.DimCampaign', 'U') IS NOT NULL DROP TABLE dw.DimCampaign;
CREATE TABLE dw.DimCampaign (
    CampaignKey INT IDENTITY(1,1) PRIMARY KEY,
    CampaignID BIGINT NOT NULL,
    CampaignName VARCHAR(255) NOT NULL,
    CampaignStatus VARCHAR(50),
    CampaignType VARCHAR(50),
    AdvertisingChannelType VARCHAR(50),
    StartDate DATE,
    EndDate DATE,
    BudgetAmount DECIMAL(15,2),
    BiddingStrategy VARCHAR(100),
    TargetCPA DECIMAL(15,2),
    TargetROAS DECIMAL(5,2),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);

-- Ad Group Dimension
IF OBJECT_ID('dw.DimAdGroup', 'U') IS NOT NULL DROP TABLE dw.DimAdGroup;
CREATE TABLE dw.DimAdGroup (
    AdGroupKey INT IDENTITY(1,1) PRIMARY KEY,
    AdGroupID BIGINT NOT NULL,
    AdGroupName VARCHAR(255) NOT NULL,
    CampaignID BIGINT NOT NULL,
    AdGroupStatus VARCHAR(50),
    AdGroupType VARCHAR(50),
    MaxCPC DECIMAL(15,2),
    MaxCPM DECIMAL(15,2),
    TargetCPA DECIMAL(15,2),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);

-- Keyword Dimension
IF OBJECT_ID('dw.DimKeyword', 'U') IS NOT NULL DROP TABLE dw.DimKeyword;
CREATE TABLE dw.DimKeyword (
    KeywordKey INT IDENTITY(1,1) PRIMARY KEY,
    KeywordID VARCHAR(255) NOT NULL,
    Keyword VARCHAR(500) NOT NULL,
    AdGroupID BIGINT NOT NULL,
    MatchType VARCHAR(50),
    Status VARCHAR(50),
    MaxCPC DECIMAL(15,2),
    QualityScore INT,
    FirstPageBid DECIMAL(15,2),
    TopOfPageBid DECIMAL(15,2),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);

-- Ad Dimension
IF OBJECT_ID('dw.DimAd', 'U') IS NOT NULL DROP TABLE dw.DimAd;
CREATE TABLE dw.DimAd (
    AdKey INT IDENTITY(1,1) PRIMARY KEY,
    AdID VARCHAR(255) NOT NULL,
    AdGroupID BIGINT NOT NULL,
    Headline1 VARCHAR(500),
    Headline2 VARCHAR(500),
    Headline3 VARCHAR(500),
    Description1 TEXT,
    Description2 TEXT,
    FinalURL VARCHAR(2048),
    DisplayURL VARCHAR(500),
    AdType VARCHAR(50),
    Status VARCHAR(50),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
);

-- Device Dimension
IF OBJECT_ID('dw.DimDevice', 'U') IS NOT NULL DROP TABLE dw.DimDevice;
CREATE TABLE dw.DimDevice (
    DeviceKey INT IDENTITY(1,1) PRIMARY KEY,
    DeviceType VARCHAR(50) NOT NULL UNIQUE,
    DeviceCategory VARCHAR(50),
    CreatedDate DATETIME DEFAULT GETDATE()
);

-- Geography Dimension
IF OBJECT_ID('dw.DimGeography', 'U') IS NOT NULL DROP TABLE dw.DimGeography;
CREATE TABLE dw.DimGeography (
    GeographyKey INT IDENTITY(1,1) PRIMARY KEY,
    Country VARCHAR(100),
    Region VARCHAR(100),
    City VARCHAR(100),
    PostalCode VARCHAR(20),
    MetroArea VARCHAR(100),
    CreatedDate DATETIME DEFAULT GETDATE()
);

-- Create indexes for better performance
CREATE INDEX IX_DimCampaign_CampaignID ON dw.DimCampaign(CampaignID);
CREATE INDEX IX_DimAdGroup_AdGroupID ON dw.DimAdGroup(AdGroupID);
CREATE INDEX IX_DimAdGroup_CampaignID ON dw.DimAdGroup(CampaignID);
CREATE INDEX IX_DimKeyword_AdGroupID ON dw.DimKeyword(AdGroupID);
CREATE INDEX IX_DimAd_AdGroupID ON dw.DimAd(AdGroupID);