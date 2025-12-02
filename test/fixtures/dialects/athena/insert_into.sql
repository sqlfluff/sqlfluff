INSERT INTO canada_pageviews
SELECT *
FROM vancouver_pageviews
WHERE pageview_date
    BETWEEN date '2019-07-01'
        AND date '2019-07-31';

INSERT INTO cities
VALUES (1,'Lansing','MI','Si quaeris peninsulam amoenam circumspice');

INSERT INTO cities
VALUES (1,'Lansing','MI','Si quaeris peninsulam amoenam circumspice'),
       (3,'Boise','ID','Esto perpetua');
