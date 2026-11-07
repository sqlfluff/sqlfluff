CREATE VIRTUAL TABLE customers USING fts5(name, addr, uuid UNINDEXED);

CREATE VIRTUAL TABLE documents USING fts5(
    title,
    document_id UNINDEXED,
    content='',
    body,
    source_id unindexed,
    tokenize='porter ascii',
    prefix=2
);

CREATE VIRTUAL TABLE quoted_columns USING fts5(
    "document id" UNINDEXED,
    'source id' UNINDEXED,
    `external id` Unindexed,
    body
);

CREATE VIRTUAL TABLE keyword_column USING fts5(unindexed, body UNINDEXED);
