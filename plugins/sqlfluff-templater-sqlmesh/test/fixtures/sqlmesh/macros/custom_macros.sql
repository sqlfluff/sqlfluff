-- Custom macros for SQLMesh test fixtures

@DEF(safe_divide, column, divisor)
    CASE 
        WHEN @divisor = 0 THEN NULL
        ELSE @column / @divisor
    END
@END

@DEF(extract_domain, email_column)
    SUBSTRING(@email_column FROM POSITION('@' IN @email_column) + 1)
@END
