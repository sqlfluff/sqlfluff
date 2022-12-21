INSERT INTO canada_pageviews
SELECT *
FROM vancouver_pageviews
WHERE pageview_date
    BETWEEN date '2019-07-01'
        AND date '2019-07-31';
