SELECT *
    FROM sales UNPIVOT INCLUDE NULLS
    (sales FOR quarter IN (q1       AS `Jan-Mar`,
                           q2       AS `Apr-Jun`,
                           q3       AS `Jul-Sep`,
                           sales.q4 AS `Oct-Dec`));

SELECT *
    FROM oncall UNPIVOT ((name, email, phone) FOR precedence IN ((name1, email1, phone1) AS primary,
                                                                 (name2, email2, phone2) AS secondary));
