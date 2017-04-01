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

INSERT INTO crawl.proxy (ip, port, protocol) SELECT '193.189.225.106', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '31.3.145.189', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '149.202.217.218', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '188.195.242.239', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '83.169.17.225', 80, 'http';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '138.201.63.123', 31288, 'https';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '46.235.155.156', 8080, 'https';
INSERT INTO crawl.proxy (ip, port, protocol) SELECT '89.163.246.150', 8080, 'https';

ALTER DATABASE auto_scraper SET datestyle TO "dmy";
