--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: app_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE app_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_id_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: app; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE app (
    id integer DEFAULT nextval('app_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    descript character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.app OWNER TO postgres;

--
-- Name: app_relation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE app_relation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_relation_id_seq OWNER TO postgres;

--
-- Name: app_relation; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE app_relation (
    id integer DEFAULT nextval('app_relation_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.app_relation OWNER TO postgres;

--
-- Name: building_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE building_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.building_id_seq OWNER TO postgres;

--
-- Name: building; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE building (
    id integer DEFAULT nextval('building_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    name_short character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying,
    CONSTRAINT name_short_shorter_than_name CHECK ((length((name_short)::text) <= length((name)::text)))
);


ALTER TABLE public.building OWNER TO postgres;

--
-- Name: customer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE customer (
    id integer NOT NULL,
    name character varying(99)
);


ALTER TABLE public.customer OWNER TO postgres;

--
-- Name: device_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_id_seq OWNER TO postgres;

--
-- Name: device; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE device (
    id integer DEFAULT nextval('device_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    domain integer NOT NULL,
    rack integer NOT NULL,
    rack_pos integer,
    hardware integer NOT NULL,
    serial_no character varying(510) DEFAULT NULL::character varying,
    asset_no character varying(510) DEFAULT NULL::character varying,
    purchased character(10) DEFAULT NULL::bpchar,
    os integer NOT NULL,
    os_version character varying(510) DEFAULT NULL::character varying,
    os_licence_key character varying(510) DEFAULT NULL::character varying,
    customer integer NOT NULL,
    service integer NOT NULL,
    role integer NOT NULL,
    monitored integer DEFAULT 0 NOT NULL,
    in_service integer DEFAULT 0 NOT NULL,
    primary_mac character varying(510) DEFAULT NULL::character varying,
    install_build character varying(510) DEFAULT NULL::character varying,
    custom_info text,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.device OWNER TO postgres;

--
-- Name: device_app_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE device_app_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_app_id_seq OWNER TO postgres;

--
-- Name: device_app; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE device_app (
    id integer DEFAULT nextval('device_app_id_seq'::regclass) NOT NULL,
    app integer NOT NULL,
    device integer NOT NULL,
    relation integer NOT NULL,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.device_app OWNER TO postgres;

--
-- Name: domain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_id_seq OWNER TO postgres;

--
-- Name: domain; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE domain (
    id integer DEFAULT nextval('domain_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    descript character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.domain OWNER TO postgres;

--
-- Name: hardware_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE hardware_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hardware_id_seq OWNER TO postgres;

--
-- Name: hardware; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE hardware (
    id integer DEFAULT nextval('hardware_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    manufacturer integer NOT NULL,
    size integer NOT NULL,
    image character varying(510) DEFAULT NULL::character varying,
    support_url character varying(510) DEFAULT NULL::character varying,
    spec_url character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.hardware OWNER TO postgres;

--
-- Name: logging_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE logging_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.logging_id_seq OWNER TO postgres;

--
-- Name: logging; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE logging (
    id integer DEFAULT nextval('logging_id_seq'::regclass) NOT NULL,
    table_changed character varying(510) NOT NULL,
    id_changed integer NOT NULL,
    name_changed character varying(510) DEFAULT NULL::character varying,
    change_type character varying(510) DEFAULT NULL::character varying,
    descript character varying(510) DEFAULT NULL::character varying,
    update_time character varying(510) DEFAULT NULL::character varying,
    update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.logging OWNER TO postgres;

--
-- Name: org_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE org_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.org_id_seq OWNER TO postgres;

--
-- Name: org; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE org (
    id integer DEFAULT nextval('org_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    account_no character varying(510) DEFAULT NULL::character varying,
    customer integer NOT NULL,
    software integer NOT NULL,
    hardware integer NOT NULL,
    descript character varying(510) DEFAULT NULL::character varying,
    home_page character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying,
    CONSTRAINT org_type_specified CHECK ((((customer + software) + hardware) > 0))
);


ALTER TABLE public.org OWNER TO postgres;

--
-- Name: os_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE os_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.os_id_seq OWNER TO postgres;

--
-- Name: os; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE os (
    id integer DEFAULT nextval('os_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    manufacturer integer NOT NULL,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.os OWNER TO postgres;

--
-- Name: rack_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rack_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rack_id_seq OWNER TO postgres;

--
-- Name: rack; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rack (
    id integer DEFAULT nextval('rack_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    "row" integer NOT NULL,
    row_pos integer NOT NULL,
    hidden_rack integer DEFAULT 0 NOT NULL,
    size integer NOT NULL,
    numbering_direction integer DEFAULT 0 NOT NULL,
    notes text,
    meta_default_data integer DEFAULT 0,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.rack OWNER TO postgres;

--
-- Name: rm_meta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rm_meta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rm_meta_id_seq OWNER TO postgres;

--
-- Name: rm_meta; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rm_meta (
    id integer DEFAULT nextval('rm_meta_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    value character varying(510) NOT NULL
);


ALTER TABLE public.rm_meta OWNER TO postgres;

--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_id_seq OWNER TO postgres;

--
-- Name: role; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE role (
    id integer DEFAULT nextval('role_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    descript character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.role OWNER TO postgres;

--
-- Name: room_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE room_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.room_id_seq OWNER TO postgres;

--
-- Name: room; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE room (
    id integer DEFAULT nextval('room_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    building integer NOT NULL,
    has_rows integer DEFAULT 0 NOT NULL,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.room OWNER TO postgres;

--
-- Name: row_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE row_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.row_id_seq OWNER TO postgres;

--
-- Name: row; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE "row" (
    id integer DEFAULT nextval('row_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    room integer NOT NULL,
    room_pos integer NOT NULL,
    hidden_row integer DEFAULT 0 NOT NULL,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public."row" OWNER TO postgres;

--
-- Name: service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE service_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.service_id_seq OWNER TO postgres;

--
-- Name: service; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE service (
    id integer DEFAULT nextval('service_id_seq'::regclass) NOT NULL,
    name character varying(510) NOT NULL,
    descript character varying(510) DEFAULT NULL::character varying,
    notes text,
    meta_default_data integer DEFAULT 0 NOT NULL,
    meta_update_time character varying(510) DEFAULT NULL::character varying,
    meta_update_user character varying(510) DEFAULT NULL::character varying
);


ALTER TABLE public.service OWNER TO postgres;

--
-- Name: app_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY app
    ADD CONSTRAINT app_name_key UNIQUE (name);


--
-- Name: app_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY app
    ADD CONSTRAINT app_pkey PRIMARY KEY (id);


--
-- Name: app_relation_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY app_relation
    ADD CONSTRAINT app_relation_name_key UNIQUE (name);


--
-- Name: app_relation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY app_relation
    ADD CONSTRAINT app_relation_pkey PRIMARY KEY (id);


--
-- Name: building_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY building
    ADD CONSTRAINT building_name_key UNIQUE (name);


--
-- Name: building_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY building
    ADD CONSTRAINT building_pkey PRIMARY KEY (id);


--
-- Name: device_app_app_device_relation_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device_app
    ADD CONSTRAINT device_app_app_device_relation_key UNIQUE (app, device, relation);


--
-- Name: device_app_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device_app
    ADD CONSTRAINT device_app_pkey PRIMARY KEY (id);


--
-- Name: device_name_domain_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_name_domain_key UNIQUE (name, domain);


--
-- Name: device_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_name_key UNIQUE (name);


--
-- Name: device_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_pkey PRIMARY KEY (id);


--
-- Name: domain_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_name_key UNIQUE (name);


--
-- Name: domain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (id);


--
-- Name: hardware_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hardware
    ADD CONSTRAINT hardware_name_key UNIQUE (name);


--
-- Name: hardware_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY hardware
    ADD CONSTRAINT hardware_pkey PRIMARY KEY (id);


--
-- Name: logging_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY logging
    ADD CONSTRAINT logging_pkey PRIMARY KEY (id);


--
-- Name: org_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY org
    ADD CONSTRAINT org_name_key UNIQUE (name);


--
-- Name: org_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY org
    ADD CONSTRAINT org_pkey PRIMARY KEY (id);


--
-- Name: os_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_name_key UNIQUE (name);


--
-- Name: os_name_key1; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_name_key1 UNIQUE (name);


--
-- Name: os_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_pkey PRIMARY KEY (id);


--
-- Name: rack_name_row_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rack
    ADD CONSTRAINT rack_name_row_key UNIQUE (name, "row");


--
-- Name: rack_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rack
    ADD CONSTRAINT rack_pkey PRIMARY KEY (id);


--
-- Name: rm_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rm_meta
    ADD CONSTRAINT rm_meta_pkey PRIMARY KEY (id);


--
-- Name: role_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY role
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: room_name_building_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY room
    ADD CONSTRAINT room_name_building_key UNIQUE (name, building);


--
-- Name: room_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY room
    ADD CONSTRAINT room_name_key UNIQUE (name);


--
-- Name: room_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY room
    ADD CONSTRAINT room_pkey PRIMARY KEY (id);


--
-- Name: row_name_room_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "row"
    ADD CONSTRAINT row_name_room_key UNIQUE (name, room);


--
-- Name: row_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "row"
    ADD CONSTRAINT row_pkey PRIMARY KEY (id);


--
-- Name: service_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY service
    ADD CONSTRAINT service_name_key UNIQUE (name);


--
-- Name: service_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY service
    ADD CONSTRAINT service_pkey PRIMARY KEY (id);


--
-- Name: device_app_app_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_app_app_idx ON device_app USING btree (app);


--
-- Name: device_app_device_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_app_device_idx ON device_app USING btree (device);


--
-- Name: device_app_relation_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_app_relation_idx ON device_app USING btree (relation);


--
-- Name: device_customer_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_customer_idx ON device USING btree (customer);


--
-- Name: device_domain_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_domain_idx ON device USING btree (domain);


--
-- Name: device_hardware_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_hardware_idx ON device USING btree (hardware);


--
-- Name: device_os_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_os_idx ON device USING btree (os);


--
-- Name: device_rack_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_rack_idx ON device USING btree (rack);


--
-- Name: device_role_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_role_idx ON device USING btree (role);


--
-- Name: device_service_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX device_service_idx ON device USING btree (service);


--
-- Name: hardware_manufacturer_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX hardware_manufacturer_idx ON hardware USING btree (manufacturer);


--
-- Name: os_manufacturer_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX os_manufacturer_idx ON os USING btree (manufacturer);


--
-- Name: rack_row_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX rack_row_idx ON rack USING btree ("row");


--
-- Name: room_building_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX room_building_idx ON room USING btree (building);


--
-- Name: row_room_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX row_room_idx ON "row" USING btree (room);


--
-- Name: device_app_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device_app
    ADD CONSTRAINT device_app_ibfk_1 FOREIGN KEY (app) REFERENCES app(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_app_ibfk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device_app
    ADD CONSTRAINT device_app_ibfk_2 FOREIGN KEY (device) REFERENCES device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_app_ibfk_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device_app
    ADD CONSTRAINT device_app_ibfk_3 FOREIGN KEY (relation) REFERENCES app_relation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_1 FOREIGN KEY (domain) REFERENCES domain(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_2 FOREIGN KEY (rack) REFERENCES rack(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_3 FOREIGN KEY (hardware) REFERENCES hardware(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_4; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_4 FOREIGN KEY (os) REFERENCES os(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_5; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_5 FOREIGN KEY (customer) REFERENCES org(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_6; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_6 FOREIGN KEY (service) REFERENCES service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: device_ibfk_7; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY device
    ADD CONSTRAINT device_ibfk_7 FOREIGN KEY (role) REFERENCES role(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hardware_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY hardware
    ADD CONSTRAINT hardware_ibfk_1 FOREIGN KEY (manufacturer) REFERENCES org(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: os_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY os
    ADD CONSTRAINT os_ibfk_1 FOREIGN KEY (manufacturer) REFERENCES org(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: rack_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY rack
    ADD CONSTRAINT rack_ibfk_1 FOREIGN KEY ("row") REFERENCES "row"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: room_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY room
    ADD CONSTRAINT room_ibfk_1 FOREIGN KEY (building) REFERENCES building(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: row_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "row"
    ADD CONSTRAINT row_ibfk_1 FOREIGN KEY (room) REFERENCES room(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: app_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE app_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE app_id_seq FROM postgres;
GRANT ALL ON SEQUENCE app_id_seq TO postgres;
GRANT USAGE ON SEQUENCE app_id_seq TO insert_entries;


--
-- Name: app; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE app FROM PUBLIC;
REVOKE ALL ON TABLE app FROM postgres;
GRANT ALL ON TABLE app TO postgres;
GRANT SELECT ON TABLE app TO query_tables;
GRANT SELECT,UPDATE ON TABLE app TO update_tables;
GRANT SELECT,DELETE ON TABLE app TO delete_entries;
GRANT SELECT,INSERT ON TABLE app TO insert_entries;
GRANT SELECT ON TABLE app TO logging;


--
-- Name: app_relation_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE app_relation_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE app_relation_id_seq FROM postgres;
GRANT ALL ON SEQUENCE app_relation_id_seq TO postgres;
GRANT USAGE ON SEQUENCE app_relation_id_seq TO insert_entries;


--
-- Name: app_relation; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE app_relation FROM PUBLIC;
REVOKE ALL ON TABLE app_relation FROM postgres;
GRANT ALL ON TABLE app_relation TO postgres;
GRANT SELECT ON TABLE app_relation TO query_tables;
GRANT SELECT,UPDATE ON TABLE app_relation TO update_tables;
GRANT SELECT,DELETE ON TABLE app_relation TO delete_entries;
GRANT SELECT,INSERT ON TABLE app_relation TO insert_entries;
GRANT SELECT ON TABLE app_relation TO logging;


--
-- Name: building_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE building_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE building_id_seq FROM postgres;
GRANT ALL ON SEQUENCE building_id_seq TO postgres;
GRANT USAGE ON SEQUENCE building_id_seq TO insert_entries;


--
-- Name: building; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE building FROM PUBLIC;
REVOKE ALL ON TABLE building FROM postgres;
GRANT ALL ON TABLE building TO postgres;
GRANT SELECT ON TABLE building TO search_devices;
GRANT SELECT ON TABLE building TO query_tables;
GRANT SELECT,UPDATE ON TABLE building TO update_tables;
GRANT SELECT,DELETE ON TABLE building TO delete_entries;
GRANT SELECT,INSERT ON TABLE building TO insert_entries;
GRANT SELECT ON TABLE building TO logging;


--
-- Name: customer; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE customer FROM PUBLIC;
GRANT SELECT ON TABLE customer TO search_devices;
GRANT SELECT ON TABLE customer TO query_tables;
GRANT SELECT,UPDATE ON TABLE customer TO update_tables;
GRANT SELECT,DELETE ON TABLE customer TO delete_entries;
GRANT SELECT,INSERT ON TABLE customer TO insert_entries;
GRANT SELECT ON TABLE customer TO logging;


--
-- Name: device_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE device_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE device_id_seq FROM postgres;
GRANT ALL ON SEQUENCE device_id_seq TO postgres;
GRANT USAGE ON SEQUENCE device_id_seq TO insert_entries;


--
-- Name: device; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE device FROM PUBLIC;
REVOKE ALL ON TABLE device FROM postgres;
GRANT ALL ON TABLE device TO postgres;
GRANT SELECT ON TABLE device TO search_devices;
GRANT SELECT ON TABLE device TO query_tables;
GRANT SELECT,UPDATE ON TABLE device TO update_tables;
GRANT SELECT,DELETE ON TABLE device TO delete_entries;
GRANT SELECT,INSERT ON TABLE device TO insert_entries;
GRANT SELECT ON TABLE device TO logging;


--
-- Name: device.id; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(id) ON TABLE device FROM PUBLIC;
REVOKE ALL(id) ON TABLE device FROM postgres;
GRANT SELECT(id) ON TABLE device TO logging;
GRANT SELECT(id) ON TABLE device TO os_update;


--
-- Name: device.name; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(name) ON TABLE device FROM PUBLIC;
REVOKE ALL(name) ON TABLE device FROM postgres;
GRANT SELECT(name) ON TABLE device TO os_update;
GRANT SELECT(name) ON TABLE device TO logging;


--
-- Name: device.os; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(os) ON TABLE device FROM PUBLIC;
REVOKE ALL(os) ON TABLE device FROM postgres;
GRANT UPDATE(os) ON TABLE device TO os_update;


--
-- Name: device.os_version; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(os_version) ON TABLE device FROM PUBLIC;
REVOKE ALL(os_version) ON TABLE device FROM postgres;
GRANT UPDATE(os_version) ON TABLE device TO os_update;


--
-- Name: device.meta_update_time; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(meta_update_time) ON TABLE device FROM PUBLIC;
REVOKE ALL(meta_update_time) ON TABLE device FROM postgres;
GRANT UPDATE(meta_update_time) ON TABLE device TO os_update;


--
-- Name: device.meta_update_user; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(meta_update_user) ON TABLE device FROM PUBLIC;
REVOKE ALL(meta_update_user) ON TABLE device FROM postgres;
GRANT UPDATE(meta_update_user) ON TABLE device TO os_update;


--
-- Name: device_app_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE device_app_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE device_app_id_seq FROM postgres;
GRANT ALL ON SEQUENCE device_app_id_seq TO postgres;
GRANT USAGE ON SEQUENCE device_app_id_seq TO insert_entries;


--
-- Name: device_app; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE device_app FROM PUBLIC;
REVOKE ALL ON TABLE device_app FROM postgres;
GRANT ALL ON TABLE device_app TO postgres;
GRANT SELECT ON TABLE device_app TO query_tables;
GRANT SELECT,UPDATE ON TABLE device_app TO update_tables;
GRANT SELECT,DELETE ON TABLE device_app TO delete_entries;
GRANT SELECT,INSERT ON TABLE device_app TO insert_entries;
GRANT SELECT ON TABLE device_app TO logging;


--
-- Name: domain_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE domain_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domain_id_seq FROM postgres;
GRANT ALL ON SEQUENCE domain_id_seq TO postgres;
GRANT USAGE ON SEQUENCE domain_id_seq TO insert_entries;


--
-- Name: domain; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE domain FROM PUBLIC;
REVOKE ALL ON TABLE domain FROM postgres;
GRANT ALL ON TABLE domain TO postgres;
GRANT SELECT ON TABLE domain TO search_devices;
GRANT SELECT ON TABLE domain TO query_tables;
GRANT SELECT,UPDATE ON TABLE domain TO update_tables;
GRANT SELECT,DELETE ON TABLE domain TO delete_entries;
GRANT SELECT,INSERT ON TABLE domain TO insert_entries;
GRANT SELECT ON TABLE domain TO logging;


--
-- Name: hardware_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE hardware_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE hardware_id_seq FROM postgres;
GRANT ALL ON SEQUENCE hardware_id_seq TO postgres;
GRANT SELECT,UPDATE ON SEQUENCE hardware_id_seq TO insert_entries;


--
-- Name: hardware; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE hardware FROM PUBLIC;
REVOKE ALL ON TABLE hardware FROM postgres;
GRANT ALL ON TABLE hardware TO postgres;
GRANT SELECT ON TABLE hardware TO search_devices;
GRANT SELECT ON TABLE hardware TO query_tables;
GRANT SELECT,UPDATE ON TABLE hardware TO update_tables;
GRANT SELECT,DELETE ON TABLE hardware TO delete_entries;
GRANT SELECT,INSERT ON TABLE hardware TO insert_entries;
GRANT SELECT ON TABLE hardware TO logging;


--
-- Name: logging_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE logging_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE logging_id_seq FROM postgres;
GRANT ALL ON SEQUENCE logging_id_seq TO postgres;
GRANT USAGE ON SEQUENCE logging_id_seq TO logging;


--
-- Name: logging; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE logging FROM PUBLIC;
REVOKE ALL ON TABLE logging FROM postgres;
GRANT ALL ON TABLE logging TO postgres;
GRANT SELECT,INSERT ON TABLE logging TO logging;


--
-- Name: org_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE org_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE org_id_seq FROM postgres;
GRANT ALL ON SEQUENCE org_id_seq TO postgres;
GRANT USAGE ON SEQUENCE org_id_seq TO insert_entries;


--
-- Name: org; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE org FROM PUBLIC;
REVOKE ALL ON TABLE org FROM postgres;
GRANT ALL ON TABLE org TO postgres;
GRANT SELECT ON TABLE org TO search_devices;
GRANT SELECT ON TABLE org TO query_tables;
GRANT SELECT,UPDATE ON TABLE org TO update_tables;
GRANT SELECT,DELETE ON TABLE org TO delete_entries;
GRANT SELECT,INSERT ON TABLE org TO insert_entries;
GRANT SELECT ON TABLE org TO logging;


--
-- Name: os_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE os_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE os_id_seq FROM postgres;
GRANT ALL ON SEQUENCE os_id_seq TO postgres;
GRANT USAGE ON SEQUENCE os_id_seq TO insert_entries;


--
-- Name: os; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE os FROM PUBLIC;
REVOKE ALL ON TABLE os FROM postgres;
GRANT ALL ON TABLE os TO postgres;
GRANT SELECT ON TABLE os TO search_devices;
GRANT SELECT ON TABLE os TO query_tables;
GRANT SELECT,UPDATE ON TABLE os TO update_tables;
GRANT SELECT,DELETE ON TABLE os TO delete_entries;
GRANT SELECT,INSERT ON TABLE os TO insert_entries;
GRANT SELECT ON TABLE os TO logging;


--
-- Name: os.id; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(id) ON TABLE os FROM PUBLIC;
REVOKE ALL(id) ON TABLE os FROM postgres;
GRANT SELECT(id) ON TABLE os TO os_update;


--
-- Name: os.name; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL(name) ON TABLE os FROM PUBLIC;
REVOKE ALL(name) ON TABLE os FROM postgres;
GRANT SELECT(name) ON TABLE os TO os_update;


--
-- Name: rack_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE rack_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE rack_id_seq FROM postgres;
GRANT ALL ON SEQUENCE rack_id_seq TO postgres;
GRANT USAGE ON SEQUENCE rack_id_seq TO insert_entries;


--
-- Name: rack; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE rack FROM PUBLIC;
REVOKE ALL ON TABLE rack FROM postgres;
GRANT ALL ON TABLE rack TO postgres;
GRANT SELECT ON TABLE rack TO search_devices;
GRANT SELECT ON TABLE rack TO query_tables;
GRANT SELECT,UPDATE ON TABLE rack TO update_tables;
GRANT SELECT,DELETE ON TABLE rack TO delete_entries;
GRANT SELECT,INSERT ON TABLE rack TO insert_entries;
GRANT SELECT ON TABLE rack TO logging;


--
-- Name: rm_meta_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE rm_meta_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE rm_meta_id_seq FROM postgres;
GRANT ALL ON SEQUENCE rm_meta_id_seq TO postgres;


--
-- Name: rm_meta; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE rm_meta FROM PUBLIC;
REVOKE ALL ON TABLE rm_meta FROM postgres;
GRANT ALL ON TABLE rm_meta TO postgres;


--
-- Name: role_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE role_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE role_id_seq FROM postgres;
GRANT ALL ON SEQUENCE role_id_seq TO postgres;
GRANT SELECT,UPDATE ON SEQUENCE role_id_seq TO insert_entries;


--
-- Name: role; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE role FROM PUBLIC;
REVOKE ALL ON TABLE role FROM postgres;
GRANT ALL ON TABLE role TO postgres;
GRANT SELECT ON TABLE role TO search_devices;
GRANT SELECT ON TABLE role TO query_tables;
GRANT SELECT,UPDATE ON TABLE role TO update_tables;
GRANT SELECT,DELETE ON TABLE role TO delete_entries;
GRANT SELECT,INSERT ON TABLE role TO insert_entries;
GRANT SELECT ON TABLE role TO logging;


--
-- Name: room_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE room_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE room_id_seq FROM postgres;
GRANT ALL ON SEQUENCE room_id_seq TO postgres;
GRANT USAGE ON SEQUENCE room_id_seq TO insert_entries;


--
-- Name: room; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE room FROM PUBLIC;
REVOKE ALL ON TABLE room FROM postgres;
GRANT ALL ON TABLE room TO postgres;
GRANT SELECT ON TABLE room TO search_devices;
GRANT SELECT ON TABLE room TO query_tables;
GRANT SELECT,UPDATE ON TABLE room TO update_tables;
GRANT SELECT,DELETE ON TABLE room TO delete_entries;
GRANT SELECT,INSERT ON TABLE room TO insert_entries;
GRANT SELECT ON TABLE room TO logging;


--
-- Name: row_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE row_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE row_id_seq FROM postgres;
GRANT ALL ON SEQUENCE row_id_seq TO postgres;
GRANT USAGE ON SEQUENCE row_id_seq TO insert_entries;


--
-- Name: row; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE "row" FROM PUBLIC;
REVOKE ALL ON TABLE "row" FROM postgres;
GRANT ALL ON TABLE "row" TO postgres;
GRANT SELECT ON TABLE "row" TO search_devices;
GRANT SELECT ON TABLE "row" TO query_tables;
GRANT SELECT,UPDATE ON TABLE "row" TO update_tables;
GRANT DELETE ON TABLE "row" TO delete_entries;
GRANT SELECT,INSERT ON TABLE "row" TO insert_entries;
GRANT SELECT ON TABLE "row" TO logging;


--
-- Name: service_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE service_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE service_id_seq FROM postgres;
GRANT ALL ON SEQUENCE service_id_seq TO postgres;
GRANT USAGE ON SEQUENCE service_id_seq TO insert_entries;


--
-- Name: service; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE service FROM PUBLIC;
REVOKE ALL ON TABLE service FROM postgres;
GRANT ALL ON TABLE service TO postgres;
GRANT SELECT ON TABLE service TO search_devices;
GRANT SELECT ON TABLE service TO query_tables;
GRANT SELECT,UPDATE ON TABLE service TO update_tables;
GRANT SELECT,DELETE ON TABLE service TO delete_entries;
GRANT SELECT,INSERT ON TABLE service TO insert_entries;
GRANT SELECT ON TABLE service TO logging;


--
-- PostgreSQL database dump complete
--

