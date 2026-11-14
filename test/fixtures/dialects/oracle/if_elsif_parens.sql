FUNCTION invcolor(
    p_is_available IN VARCHAR2,
    p_inventory_in_stock IN NUMBER
) RETURN VARCHAR2
IS
    color VARCHAR2(6);
BEGIN
    IF p_is_available = 'Y' THEN
        color := 'purple';
    ELSIF (p_inventory_in_stock > 0) THEN
        color := 'green';
    ELSE
        color := 'gray';
    END IF;

    RETURN color;
END invcolor;
/

IF p_is_available = 'Y' THEN
    color := 'purple';
ELSIF (p_inventory_in_stock > 0) THEN
    color := 'green';
ELSE
    color := 'gray';
END IF;
/
