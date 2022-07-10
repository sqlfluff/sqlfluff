SELECT foo
FROM bar
WHERE
    baz > -2147483648
    AND baz > 9223372036854775807l
    AND baz > 9223372036854775807L
    AND baz > -32y
    AND baz > -32Y
    AND baz > 482s
    AND baz > 482S
    AND baz > 12.578
    AND baz > -0.1234567
    AND baz > -.1234567
    AND baz > -123.
    AND baz > 123.bd
    AND baz > 123.BD
    AND baz > 5e2
    AND baz > 5E2
    AND baz > 5d
    AND baz > 5D
    AND baz > -5bd
    AND baz > -5BD
    AND baz > 12.578e-2d
    AND baz > 12.578E-2D
    AND baz > -.1234567e+2bd
    AND baz > -.1234567E+2BD
    AND baz > +3.e+3
    AND baz > +3.E+3
    AND baz > -3.E-3D
    AND baz > -3.e-3d
    AND baz > -+-1
    AND baz > -+- 1
