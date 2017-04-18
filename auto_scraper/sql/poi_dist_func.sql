CREATE OR REPLACE FUNCTION  poi_distance(lat1 float, lon1 float, lat2 float, lon2 float)
RETURNS float AS $$
        DECLARE
        p CONSTANT float := 0.017453292519943295;
        a float;
        BEGIN
        a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2;
        RETURN 12742 * asin(|/ a);
        END;
$$ LANGUAGE plpgsql