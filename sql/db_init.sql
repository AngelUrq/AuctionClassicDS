USE [AuctionClassicDB];

DROP TABLE IF EXISTS [Auction];
DROP TABLE IF EXISTS [RecordedAuction];
DROP TABLE IF EXISTS [Item];

CREATE TABLE [Auction] (
    [Id] BIGINT PRIMARY KEY,
    [ItemId] INT,
    [BidGold] INT,
    [BidSilver] INT,
    [BuyoutGold] INT,
    [BuyoutSilver] INT,
    [Quantity] INT,
    [TimeLeft] VARCHAR(10),
    [Rand] INT,
    [Seed] INT,
    [LastTimeSeen] DATETIME
);

CREATE TABLE [RecordedAuction] (
    [AuctionId] BIGINT,
    [RecordedTime] DATETIME
    CONSTRAINT PK_RecordedAuction PRIMARY KEY NONCLUSTERED ([AuctionId], [RecordedTime])
);

CREATE TABLE [Item] (
    [Id] INT PRIMARY KEY,
    [Name] NVARCHAR(70),
    [Quality] NVARCHAR(40),
    [Level] INT,
    [RequiredLevel] INT,
    [ItemClass] NVARCHAR(40),
    [ItemSubClass] NVARCHAR(40),
    [PurchasePriceGold] INT,
    [PurchasePriceSilver] INT,
    [SellPriceGold] INT,
    [SellPriceSilver] INT,
    [MaxCount] INT,
    [IsEquippable] BIT,
    [IsStackable] BIT
);
