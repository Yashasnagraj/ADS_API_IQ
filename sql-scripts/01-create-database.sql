-- Create MarketingIQ database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MarketingIQ')
BEGIN
    CREATE DATABASE MarketingIQ;
END
GO

USE MarketingIQ;
GO

-- Create schema for dimensional model
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'dw')
BEGIN
    EXEC('CREATE SCHEMA dw');
END
GO