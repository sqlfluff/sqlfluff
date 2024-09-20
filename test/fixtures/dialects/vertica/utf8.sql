SELECT amount+1 AS 'amount' FROM num1;

SELECT höhe+1 AS 'höhe' FROM num1;


SELECT amount*2 AS 'amount' FROM num1;

SELECT höhe*2 AS 'höhe' FROM num1;


SELECT employees.personal.name, neighbors.area FROM neighbors, employees
WHERE employees.personal.address.zipcode=neighbors.area.zipcode AND neighbors.num_neighbors > 1;

SELECT mitarbeiter.persönlicher.name, nachbarn.bereich FROM nachbarn, mitarbeiter
WHERE mitarbeiter.persönlicher.adresse.zipcode=nachbarn.gebiet.zipcode AND nachbarn.nummer_nachbarn > 1;


SELECT itemkey AS key, IMPLODE(itemprice) WITHIN GROUP (ORDER BY itemprice) AS prices
    FROM filtered GROUP BY itemkey ORDER BY itemkey;

SELECT ключтовара AS key, IMPLODE(ценатовара) WITHIN GROUP (ORDER BY ценатовара) AS цены
    FROM отфильтровано GROUP BY ключтовара ORDER BY ключтовара;


SELECT State, APPROXIMATE_PERCENTILE(sales USING PARAMETERS percentiles='0.5') AS median
FROM allsales GROUP BY state;

SELECT Χώρα, APPROXIMATE_PERCENTILE(πωλήσεις USING PARAMETERS percentiles='0.5') AS διάμεσος
FROM όλεςτιςπωλήσεις GROUP BY χώρα;


SELECT customer_state, customer_key, annual_income, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY annual_income)
      OVER (PARTITION BY customer_state) AS PERCENTILE_CONT
   FROM customer_dimension WHERE customer_state IN ('DC','WI') ORDER BY customer_state, customer_key;

SELECT état_du_client, clé_client, revenu_annuel, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY revenu_annuel)
      OVER (PARTITION BY état_du_client) AS PERCENTILE_CONT
   FROM dimension_client WHERE état_du_client IN ('Provence','Сhampagne') ORDER BY état_du_client, clé_client;


SELECT customer_state, customer_key, annual_income,
      PERCENTILE_DISC(.2) WITHIN GROUP(ORDER BY annual_income)
      OVER (PARTITION BY customer_state) AS PERCENTILE_DISC
   FROM customer_dimension
   WHERE customer_state IN ('DC','WI')
   AND customer_key < 300
   ORDER BY customer_state, customer_key;

SELECT état_du_client, clé_client, revenu_annuel,
      PERCENTILE_DISC(.2) WITHIN GROUP(ORDER BY annual_income)
      OVER (PARTITION BY état_du_client) AS PERCENTILE_DISC
   FROM dimension_client
   WHERE état_du_client IN ('Provence','Сhampagne')
   AND clé_client < 300
   ORDER BY état_du_client, clé_client;

SELECT customer_state, customer_key, annual_income, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY annual_income)
      OVER (PARTITION BY customer_state) AS PERCENTILE_CONT
   FROM customer_dimension WHERE customer_state IN ('DC','WI') AND customer_key < 300
   ORDER BY customer_state, customer_key;

SELECT état_du_client, clé_client, revenu_annuel, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY revenu_annuel)
      OVER (PARTITION BY état_du_client) AS PERCENTILE_CONT
   FROM dimension_client WHERE état_du_client IN ('Provence','Сhampagne') AND clé_client < 300
   ORDER BY état_du_client, clé_client;


SELECT store_region, store_city||', '||store_state location, store_name, number_of_employees FROM store.store_dimension
     LIMIT 2 OVER (PARTITION BY store_region ORDER BY number_of_employees ASC);

SELECT регион_магазина, город_магазина||', '||область_магазина местоположение, имя_магазина, количество_сотрудников FROM магазины.измерение_магазины
     LIMIT 2 OVER (PARTITION BY регион_магазина ORDER BY количество_сотрудников ASC);


SELECT PREDICT_LINEAR_REG(waiting USING PARAMETERS model_name='myLinearRegModel') FROM
faithful ORDER BY id;

SELECT PREDICT_LINEAR_REG(attente USING PARAMETERS model_name='monRegModèleLinéaire') FROM
fidèle ORDER BY id;


SELECT INFER_EXTERNAL_TABLE_DDL('/data/people/*.parquet'
        USING PARAMETERS format = 'parquet', table_name = 'employees');

SELECT INFER_EXTERNAL_TABLE_DDL('/data/άνθρωποι/*.parquet'
        USING PARAMETERS format = 'parquet', table_name = 'εργαζόμενοι');


SELECT PREDICT_ARIMA(temperature USING PARAMETERS model_name='arima_temp', start=100, npredictions=10) OVER(ORDER BY time) FROM temp_data;

SELECT PREDICT_ARIMA(температура USING PARAMETERS model_name='arima_temp', start=100, npredictions=10) OVER(ORDER BY time) FROM временные_данные;

SELECT INFER_TABLE_DDL ('/data/*.json'
    USING PARAMETERS table_name='restaurants', format='json',
max_files=3, max_candidates=3);

SELECT INFER_TABLE_DDL ('/data/*.json'
    USING PARAMETERS table_name='εστιατόρια', format='json',
max_files=3, max_candidates=3);


SELECT PURGE_TABLE('store.store_sales_fact');

SELECT PURGE_TABLE('المتجر.متجر_مبيعات_المتجر');


SELECT MSE(obs, prediction) OVER()
   FROM (SELECT eruptions AS obs,
                PREDICT_LINEAR_REG (waiting USING PARAMETERS model_name='myLinearRegModel') AS prediction
         FROM faithful_testing) AS PredictionOutput;

SELECT MSE(наблюдения, предсказания) OVER()
   FROM (SELECT извержения AS наблюдения,
                PREDICT_LINEAR_REG (ожидания USING PARAMETERS model_name='myLinearRegModel') AS прогноз
         FROM верное_испытание) AS РезультатПрогноза;


SELECT ps[0] as q0, ps[1] as q1, ps[2] as q2, ps[3] as q3, ps[4] as q4
FROM (SELECT APPROXIMATE_PERCENTILE(sales USING PARAMETERS percentiles='0, 0.25, 0.5, 0.75, 1')
AS ps FROM allsales GROUP BY state) as s1;

SELECT pz[0] as q0, pz[1] as q1, pz[2] as q2, pz[3] as q3, pz[4] as q4
FROM (SELECT APPROXIMATE_PERCENTILE(Verkäufe USING PARAMETERS percentiles='0, 0.25, 0.5, 0.75, 1')
AS pz FROM alleVerkäufe GROUP BY Staat) as s1;


SELECT id.name, major, GPA FROM students
   WHERE id = ROW('alice',119, ARRAY['alice@example.com','ap16@cs.example.edu']);

SELECT ид.имя, курс, СРБАЛЛ FROM студенты
   WHERE ид = ROW('алиса',119, ARRAY['alice@example.com','ap16@cs.example.edu']);


SELECT E'first part o'
    'f a long line';

SELECT E'πρώτο μέρος μι'
    'ας μακράς γραμμής';


SELECT STRING_TO_ARRAY(name USING PARAMETERS collection_delimiter=' ') FROM employee;

SELECT STRING_TO_ARRAY(имя USING PARAMETERS collection_delimiter=' ') FROM сотрудники;

-- ALTER SCHEMA block
ALTER SCHEMA ms OWNER TO dbadmin CASCADE;

ALTER SCHEMA επιμελητεία OWNER TO διαχειριστής CASCADE;

ALTER SCHEMA логистика OWNER TO алиса CASCADE;

ALTER SCHEMA s1, s2 RENAME TO s3, s4;

ALTER SCHEMA εμπορικός, s2 RENAME TO продажи, s4;

-- ALTER TABLE block
ALTER TABLE public.store_orders ADD COLUMN expected_ship_date date;

ALTER TABLE public.κατάστημα_παραγγελίες ADD COLUMN αναμενόμενη_ημερομηνία_αποστολής date;

ALTER TABLE public.заказы_магазина ADD COLUMN ожиддаемая_дата_отгрузки date;

ALTER TABLE t33 OWNER TO Alice;

--! ALTER TABLE επιμελητεία OWNER TO διαχειριστής;

--! ALTER TABLE заказы OWNER TO алиса;

-- ARRAY block
SELECT (ARRAY['مسؤل', 'διαχειριστής', 'логистика', 'd', 'e'])[1];

-- Cast w/ whitespace
SELECT amount_of_honey :: FLOAT
FROM bear_inventory;

SELECT ποσότητα_μελιού :: FLOAT
FROM αρκούδα_αποθήκη;

SELECT количество_мёда :: FLOAT
FROM медвежий_склад;

-- COMMENT ON block
COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'alias of APPROXIMATE_PERCENTILE with 0.5 as its parameter';
COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'ψευδώνυμο APPROXIMATE_PERCENTILE με 0,5 ως παράμετρό του';
COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'псевдоним APPROXIMATE_PERCENTILE с 0,5 в качестве параметра';

COMMENT ON SCHEMA public  IS 'All users can access this schema';
COMMENT ON SCHEMA public  IS 'Όλοι οι χρήστες έχουν πρόσβαση σε αυτό το σχήμα';
COMMENT ON SCHEMA public  IS 'Все пользователи могут получить доступ к этой схеме';

-- COPY block
-- COPY INTO test_parquet
-- FROM 'https://myaccount.blob.core.windows.net/myblobcontainer/folder1/*.parquet'
-- WITH (
--     FILE_FORMAT = myFileFormat,
--     CREDENTIAL=(IDENTITY= 'Shared Access Signature', SECRET='<Your_SAS_Token>')
-- );

-- COPY INTO продажи.продажи_на_сегодня
-- FROM 'https://myaccount.blob.core.windows.net/myblobcontainer/folder0/*.txt'
-- WITH (
--     FILE_TYPE = 'CSV',
--     CREDENTIAL = (IDENTITY = 'Managed Identity'),
--     FIELDQUOTE = '"',
--     FIELDTERMINATOR=','
-- );

-- CREATE PROJECTION block
CREATE PROJECTION public.employee_dimension_super
    AS SELECT * FROM public.employee_dimension
    ORDER BY employee_key
    SEGMENTED BY hash(employee_key) ALL NODES;

CREATE PROJECTION εμπορικός.παραγγελίες_ανά_ημέρα
    AS SELECT * FROM εμπορικός.παραγγελίες
    ORDER BY employee_key
    SEGMENTED BY hash(employee_key) ALL NODES;

CREATE PROJECTION продажи.продажи_на_по_клиенту
    AS SELECT * FROM продажи.продажи_на_сегодня
    ORDER BY клиент
    SEGMENTED BY hash(клиент) ALL NODES;

-- CREATE SCHEMA block
-- CREATE SCHEMA IF NOT EXISTS foo COMMENT 'test schema' MANAGEDLOCATION 'hdfs://path';
-- CREATE SCHEMA IF NOT EXISTS εμπορικός COMMENT 'test schema' MANAGEDLOCATION 'hdfs://path';
-- CREATE SCHEMA IF NOT EXISTS продажи COMMENT 'test schema' MANAGEDLOCATION 'hdfs://path';
