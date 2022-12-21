CONSTRAINT valid_timestamp EXPECT (event_ts > '2012-01-01');

CONSTRAINT valid_current_page EXPECT (
    current_page_id IS NOT NULL AND current_page_title IS NOT NULL
) ON VIOLATION DROP ROW;

CONSTRAINT valid_count EXPECT (count > 0) ON VIOLATION FAIL UPDATE;
