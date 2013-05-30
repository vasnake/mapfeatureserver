--
-- PostgreSQL database dump
--

-- Dumped from database version 9.0.12
-- Dumped by pg_dump version 9.1.2
-- Started on 2013-05-31 01:08:50

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = mfsdata, pg_catalog;

SET default_with_oids = false;

--
-- TOC entry 222 (class 1259 OID 18604)
-- Dependencies: 9 1887
-- Name: patching; Type: TABLE; Schema: mfsdata; Owner: -
--

CREATE TABLE patching (
    gid integer NOT NULL,
    ptchlenght smallint,
    pthcdeptht smallint,
    descr character varying(100),
    regdaterec character varying(50),
    regdaterep character varying(50),
    roadcarpet character varying(50),
    geog public.geography(Point,4326),
    testtimestamp timestamp without time zone
);


--
-- TOC entry 221 (class 1259 OID 18602)
-- Dependencies: 222 9
-- Name: patching_gid_seq; Type: SEQUENCE; Schema: mfsdata; Owner: -
--

CREATE SEQUENCE patching_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3550 (class 0 OID 0)
-- Dependencies: 221
-- Name: patching_gid_seq; Type: SEQUENCE OWNED BY; Schema: mfsdata; Owner: -
--

ALTER SEQUENCE patching_gid_seq OWNED BY patching.gid;


--
-- TOC entry 3551 (class 0 OID 0)
-- Dependencies: 221
-- Name: patching_gid_seq; Type: SEQUENCE SET; Schema: mfsdata; Owner: -
--

SELECT pg_catalog.setval('patching_gid_seq', 11, true);


--
-- TOC entry 3543 (class 2604 OID 18607)
-- Dependencies: 222 221 222
-- Name: gid; Type: DEFAULT; Schema: mfsdata; Owner: -
--

ALTER TABLE patching ALTER COLUMN gid SET DEFAULT nextval('patching_gid_seq'::regclass);


--
-- TOC entry 3547 (class 0 OID 18604)
-- Dependencies: 222
-- Data for Name: patching; Type: TABLE DATA; Schema: mfsdata; Owner: -
--

INSERT INTO patching VALUES (5, 1, 2, '3', '4', '5', 'Асфальт', '0101000020E6100000C02807D4974242406847631A71724A40', NULL);
INSERT INTO patching VALUES (6, 15, 15, 'Ямы', '2012-07-31', NULL, 'Щебень', '0101000020E6100000D04696B5154E4240108AF72D84754A40', NULL);
INSERT INTO patching VALUES (7, 20, 5, 'Ямы', '2012-07-02', NULL, 'Бетон', '0101000020E6100000E0AD96B5B9404240B08D8E048A7D4A40', NULL);
INSERT INTO patching VALUES (9, 35, 5, NULL, NULL, NULL, 'Бетон', '0101000020E6100000E8F095B5175B4240D01873657D754A40', NULL);
INSERT INTO patching VALUES (10, 0, 0, NULL, NULL, NULL, 'Бетон', '0101000020E6100000184B96359F26424080FB85B48C7F4A40', NULL);
INSERT INTO patching VALUES (11, 0, 0, NULL, NULL, NULL, 'Щебень', '0101000020E6100000804296358C1B4240A8B5E07A117E4A40', NULL);
INSERT INTO patching VALUES (1, 3, 5, NULL, '2012.07.23', NULL, 'Асфальт', '0101000020E6100000008CEB08F53F424040E85BE4B3704A40', NULL);
INSERT INTO patching VALUES (2, 5, 5, NULL, '2012.07.23', NULL, 'Асфальт', '0101000020E6100000D8B6AFA37441424030E995A3E1704A40', NULL);
INSERT INTO patching VALUES (3, 20, 10, NULL, '2012.07.23', NULL, 'Бетон', '0101000020E610000030B873EFCE424240B8BCB7910E714A40', NULL);
INSERT INTO patching VALUES (4, 100, 15, NULL, '2012.07.23', NULL, 'Щебень', '0101000020E6100000A0D7C189743F4240B07E5B66476F4A40', NULL);
INSERT INTO patching VALUES (8, 500, 8, 'werwre', '2012/08/02', '2012/09/15', 'Асфальт', '0101000020E610000098A395B5ECE04140204587D4357B4A40', '2013-05-29 18:09:00');


--
-- TOC entry 3546 (class 2606 OID 18612)
-- Dependencies: 222 222
-- Name: patching_pkey; Type: CONSTRAINT; Schema: mfsdata; Owner: -
--

ALTER TABLE ONLY patching
    ADD CONSTRAINT patching_pkey PRIMARY KEY (gid);


--
-- TOC entry 3544 (class 1259 OID 18613)
-- Dependencies: 222 2979
-- Name: patching_geog_gist; Type: INDEX; Schema: mfsdata; Owner: -
--

CREATE INDEX patching_geog_gist ON patching USING gist (geog);


-- Completed on 2013-05-31 01:08:51

--
-- PostgreSQL database dump complete
--

