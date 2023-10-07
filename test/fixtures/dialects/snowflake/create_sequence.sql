CREATE SEQUENCE seq;

CREATE OR REPLACE SEQUENCE IF NOT EXISTS seq
WITH
    START WITH = 2
    INCREMENT BY = 15
    ORDER
    COMMENT = 'this_a_beautiful_sequence';


CREATE OR REPLACE SEQUENCE IF NOT EXISTS seq
START = 2
INCREMENT = 15
NOORDER;

CREATE SEQUENCE seq
START 2;

CREATE SEQUENCE seq
INCREMENT 2;
