SELECT
	DISTINCT address
FROM data.advert
WHERE address NOT IN (
	SELECT
		address
	FROM data.geocoded
	);