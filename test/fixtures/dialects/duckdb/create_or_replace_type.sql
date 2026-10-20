CREATE OR REPLACE TYPE mood AS ENUM ('happy', 'sad');
CREATE OR REPLACE TYPE many_things AS STRUCT(k integer, l varchar);
CREATE OR REPLACE TYPE one_thing AS UNION (number integer, string varchar);
CREATE OR REPLACE TYPE x_index AS integer;
CREATE OR REPLACE TYPE main.mytype AS integer;
CREATE OR REPLACE TYPE "main"."mytype2" AS main.mytype;
