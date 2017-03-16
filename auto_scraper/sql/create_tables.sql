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
INSERT INTO crawl.url (url, domain)
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

