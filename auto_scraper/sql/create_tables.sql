CREATE ROLE rw_user WITH LOGIN;

CREATE SCHEMA crawl;
GRANT USAGE ON SCHEMA crawl TO rw_user;

CREATE TABLE crawl.url
(
  id serial NOT NULL,
  start_url character varying NOT NULL,
  request_headers character varying,
  request_body character varying,
  domain character varying NOT NULL
);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE crawl.url TO rw_user;
INSERT INTO crawl.url (start_url, domain)
VALUES ('http://www.piata-az.ro/anunturi/apartamente-de-inchiriat-1031', 'piata-az');

CREATE SCHEMA data;
GRANT USAGE ON SCHEMA data TO rw_user;

CREATE TABLE data.advert
(
  url character varying NOT NULL,
  title character varying,
  address character varying,
  price character varying,
  type character varying,
  date date,
  extra character varying,
  to_be_deleted boolean DEFAULT false,
  domain character varying DEFAULT (NOT NULL::boolean),
  CONSTRAINT advert_pkey PRIMARY KEY (url)
);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data.advert TO rw_user;

CREATE TABLE crawl.proxy (id SERIAL, ip varchar, port int, protocol varchar, available boolean default true);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE crawl.proxy TO rw_user;

INSERT INTO crawl.proxy (ip, port, protocol) SELECT '85.204.229.47', 81, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '85.204.229.47', 81, 'https';

INSERT INTO crawl.proxy (ip, port, protocol) SELECT '86.107.110.218', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '86.107.110.218', 80, 'https';

INSERT INTO crawl.proxy (ip, port, protocol) SELECT '91.194.42.51', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '91.194.42.51', 80, 'https';

INSERT INTO crawl.proxy (ip, port, protocol) SELECT '188.213.175.227', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '188.213.175.227', 80, 'https';

ALTER DATABASE auto_scraper SET datestyle TO "dmy";

CREATE TABLE data.geocoded
(
	id SERIAL,
	address character varying NOT NULL,
	latitude float NOT NULL,
	longitude float NOT NULL,
	CONSTRAINT geocoded_pkey PRIMARY KEY (address)
);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data.geocoded TO rw_user;

CREATE TABLE data.poi
(
	id SERIAL,
	name character varying,
	address character varying,
	latitude float,
	longitude float,
	rating float,
	type character varying
);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data.poi TO rw_user;

CREATE TABLE data.poi_distance
(
	id SERIAL,
	poi_id integer,
	address_id integer,
	distance float,
	instructions varchar
);
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data.poi_distance TO rw_user;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA data TO rw_user;