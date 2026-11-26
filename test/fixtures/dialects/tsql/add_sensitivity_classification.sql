-- https://learn.microsoft.com/en-us/sql/t-sql/statements/add-sensitivity-classification-transact-sql
ADD SENSITIVITY CLASSIFICATION TO
    dbo.sales.price, dbo.sales.discount
WITH (LABEL = 'Highly Confidential', INFORMATION_TYPE = 'Financial', RANK = CRITICAL);

ADD SENSITIVITY CLASSIFICATION TO
    dbo.customer.comments
WITH (LABEL = 'Confidential', LABEL_ID = '643f7acd-776a-438d-890c-79c3f2a520d6');

ADD SENSITIVITY CLASSIFICATION TO [dbo].[customer].[email]
WITH (INFORMATION_TYPE_ID = '5c503e21-22c6-81fa-620b-f369b8ec38d1');

ADD SENSITIVITY CLASSIFICATION TO customer.email WITH (RANK = NONE);

ADD SENSITIVITY CLASSIFICATION TO dbo.customer.notes
WITH (LABEL = N'Confidential', INFORMATION_TYPE = N'Contact Info', RANK = LOW);

ADD SENSITIVITY CLASSIFICATION TO dbo.customer.phone WITH (RANK = MEDIUM);

ADD SENSITIVITY CLASSIFICATION TO dbo.customer.birth_date WITH (RANK = HIGH);
