USE MarketingIQ;
GO

-- Populate Date Dimension (2020-2030)
DECLARE @StartDate DATE = '2020-01-01';
DECLARE @EndDate DATE = '2030-12-31';
DECLARE @CurrentDate DATE = @StartDate;

WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dw.DimDate (
        DateKey,
        Date,
        Year,
        Quarter,
        Month,
        MonthName,
        Week,
        DayOfWeek,
        DayName,
        IsWeekend,
        FiscalYear,
        FiscalQuarter
    )
    VALUES (
        CAST(FORMAT(@CurrentDate, 'yyyyMMdd') AS INT),
        @CurrentDate,
        YEAR(@CurrentDate),
        DATEPART(QUARTER, @CurrentDate),
        MONTH(@CurrentDate),
        DATENAME(MONTH, @CurrentDate),
        DATEPART(WEEK, @CurrentDate),
        DATEPART(WEEKDAY, @CurrentDate),
        DATENAME(WEEKDAY, @CurrentDate),
        CASE WHEN DATEPART(WEEKDAY, @CurrentDate) IN (1, 7) THEN 1 ELSE 0 END,
        YEAR(@CurrentDate),
        DATEPART(QUARTER, @CurrentDate)
    );

    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- Insert default device types
INSERT INTO dw.DimDevice (DeviceType, DeviceCategory) VALUES
    ('DESKTOP', 'Computer'),
    ('MOBILE', 'Mobile'),
    ('TABLET', 'Mobile'),
    ('TV', 'Connected TV'),
    ('UNKNOWN', 'Unknown');