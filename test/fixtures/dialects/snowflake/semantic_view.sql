-- Core clause combinations and identifier forms.
SELECT *
FROM SEMANTIC_VIEW(
    sales_analysis
    DIMENSIONS orders.order_date
);

SELECT *
FROM SEMANTIC_VIEW(
    semantic.sales_analysis
    METRICS
        orders.revenue AS total_revenue,
        orders.order_count order_total
);

SELECT *
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    FACTS orders.unit_price, orders.quantity
);

-- METRICS and DIMENSIONS can appear in either order.
SELECT *
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    METRICS SUM(orders.revenue) + orders.tax AS gross_revenue
    DIMENSIONS DATE_TRUNC('MONTH', orders.order_date) AS order_month
);

SELECT *
FROM SEMANTIC_VIEW(
    "sales analysis"
    DIMENSIONS orders.*, "order facts"."order date" order_date
    METRICS orders.revenue
);

-- FACTS and DIMENSIONS can appear in either order.
SELECT *
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    FACTS orders.unit_price * orders.quantity
    DIMENSIONS orders.order_id
);

SELECT *
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    DIMENSIONS orders.order_id
    FACTS orders.unit_price, orders.quantity
);

-- Predicates can use semantic fields, functions, arithmetic, and date literals.
SELECT *
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    DIMENSIONS orders.order_date
    METRICS COALESCE(orders.revenue, 0) revenue
    WHERE orders.order_date >= DATE '2025-01-01'
        AND orders.quantity * orders.unit_price > 100
        AND UPPER(orders.status) = 'COMPLETE'
);

-- Keywords are case-insensitive.
SELECT *
FROM semantic_view(
    analytics.semantic.sales_analysis
    dimensions orders.order_date
    metrics orders.revenue
);

-- Relational contexts.
SELECT sv.order_date, sv.revenue
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    DIMENSIONS orders.order_date
    METRICS orders.revenue
) AS sv
WHERE sv.revenue > 0
ORDER BY sv.order_date;

WITH semantic_sales AS (
    SELECT order_date, revenue
    FROM SEMANTIC_VIEW(
        analytics.semantic.sales_analysis
        DIMENSIONS orders.order_date
        METRICS orders.revenue
    )
)
SELECT semantic_sales.order_date
FROM semantic_sales;

SELECT sv.order_date, targets.target
FROM SEMANTIC_VIEW(
    analytics.semantic.sales_analysis
    DIMENSIONS orders.order_date
    METRICS orders.revenue
) AS sv
JOIN revenue_targets AS targets
    ON sv.order_date = targets.order_date;
