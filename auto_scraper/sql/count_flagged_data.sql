SELECT domain, count(*)
FROM data.advert
WHERE to_be_deleted = true
GROUP BY domain