INSERT INTO data.poi_distance
	(
		poi_id,
		address_id,
		distance
	)
SELECT
	p.id,
	g.id,
	poi_distance(g.latitude, g.longitude, p.latitude, p.longitude)
FROM data.geocoded g, data.poi p
WHERE NOT EXISTS (
	SELECT 1
	FROM data.poi_distance
	WHERE poi_id = p.id
		AND address_id = g.id
)
