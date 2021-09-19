WITH TimesSeenTable AS (
	SELECT T.AuctionId
		, YEAR(T.FirstTimeSeen) AS FirstTimeSeenYear
		, MONTH(T.FirstTimeSeen) AS FirstTimeSeenMonth
		, DAY(T.FirstTimeSeen) AS FirstTimeSeenDay
		, DATEPART(HOUR, T.FirstTimeSeen) AS FirstTimeSeenHour
		, T.TimesSeen
	FROM (
		SELECT AuctionId, MIN(RecordedTime) AS FirstTimeSeen, COUNT(*) AS TimesSeen
		FROM RecordedAuction
		GROUP BY AuctionId
	) T
)

SELECT a.[Id]
    , a.[ItemId]
	, a.[BidGold]
	, a.[BidSilver]
	, a.[BuyoutGold]
	, a.[BuyoutSilver]
    , a.[Quantity]
    , a.[TimeLeft]
	, a.[Rand]
	, a.[Seed]
	, tst.[FirstTimeSeenYear]
	, tst.[FirstTimeSeenMonth]
	, tst.[FirstTimeSeenDay]
	, tst.[FirstTimeSeenHour]
	, tst.[TimesSeen]
    , i.[Name] AS ItemName
    , i.[Quality]
    , i.[Level]
    , i.[RequiredLevel]
    , i.[ItemClass]
    , i.[ItemSubClass]
    , i.[PurchasePriceGold]
	, i.[PurchasePriceSilver]
    , i.[SellPriceGold]
	, i.[SellPriceSilver]
    , i.[MaxCount]
	, i.[IsEquippable]
	, i.[IsStackable]
FROM Auction a
	INNER JOIN Item i
		ON a.ItemId = i.Id
	INNER JOIN TimesSeenTable tst
		ON tst.AuctionId = a.Id