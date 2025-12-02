CREATE TABLE "wellplated_format" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "bottom_row" varchar(1) NOT NULL,
    "right_column" smallint unsigned NOT NULL CHECK ("right_column" >= 0)
);
