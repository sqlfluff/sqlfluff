select
    json_query(payload format json, 'lax $.unstructured.abcd[*].field?(@ > 0.5)' with array wrapper),
    json_query(payload format json encoding utf8, 'lax $.unstructured.abcd[*].field?(@ > 0.5)' without array wrapper),
    json_query(payload format json encoding utf16, 'lax $.unstructured.abcd[*].field?(@ > 0.5)' with conditional wrapper),
    json_query(payload format json encoding utf32, 'lax $.unstructured.abcd[*].field?(@ > 0.5)' with unconditional array wrapper),
    json_query(payload format json, 'lax $.unstructured.abcd[*].field?(@ > 0.5)')
;
