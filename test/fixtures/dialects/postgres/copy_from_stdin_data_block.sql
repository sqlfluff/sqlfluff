COPY my_table (col1, col2) FROM stdin;
1	foo
2	bar
\.

COPY public.bookshelves_books (username, work_id, bookshelf_id) FROM stdin;
openlibrary	15298516	1
openlibrary	45310	3
\.

COPY my_table (
    col1,
    col2
)
FROM STDIN
WITH (FORMAT text);
1	foo
2	bar
\.

SELECT 1;
