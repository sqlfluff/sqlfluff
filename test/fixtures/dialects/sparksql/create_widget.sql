-- Create dropdown widget
CREATE WIDGET DROPDOWN state DEFAULT "CA" CHOICES
    SELECT
        *
    FROM (VALUES ("CA"), ("IL"), ("MI"), ("NY"), ("OR"), ("VA"));

-- Create text widget
CREATE WIDGET TEXT database DEFAULT "customers_dev";
