SELECT col1
FROM {{ this }};

SELECT col1
FROM {{ this.render() }};
