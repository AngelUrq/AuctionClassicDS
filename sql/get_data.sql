WITH TimesSeenTable AS (
	SELECT AuctionId, COUNT(*) AS TimesSeen
	FROM RecordedAuction
	GROUP BY AuctionId
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
	, YEAR(a.[FirstTimeSeen]) AS FirstTimeSeenYear
	, MONTH(a.[FirstTimeSeen]) AS FirstTimeSeenMonth
	, DAY(a.[FirstTimeSeen]) AS FirstTimeSeenDay
	, DATEPART(HOUR, a.[FirstTimeSeen]) AS FirstTimeSeenHour
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
WHERE DATEDIFF(HOUR, a.[FirstTimeSeen], CURRENT_TIMESTAMP) >= 48