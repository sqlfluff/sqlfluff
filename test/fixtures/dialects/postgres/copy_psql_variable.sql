COPY tmp_table FROM :source;
COPY tmp_table FROM :'filename' WITH delimiter E'\t' csv;
COPY tmp_table TO :"filename" WITH (FORMAT csv);