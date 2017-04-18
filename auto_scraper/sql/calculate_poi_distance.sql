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
FROM data.geocoded g, data.poi p;