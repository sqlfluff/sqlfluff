CREATE TYPE mood AS ENUM ('happy', 'sad', 'curious');
CREATE TYPE many_things AS STRUCT(k integer, l varchar);
CREATE TYPE one_thing AS UNION (number integer, string varchar);
CREATE TYPE x_index AS integer;
CREATE TYPE myschema.mytype AS int;
CREATE TYPE "myschema".mytype2 AS int;
CREATE TYPE myschema.mytype3 AS myschema.mytype2;
