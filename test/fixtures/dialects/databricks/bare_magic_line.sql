-- Databricks notebook source

-- COMMAND ----------
%python
print("Hello world")

-- COMMAND ----------

SELECT a FROM b;

-- COMMAND ----------

%run ./Notebook

-- COMMAND ----------

%tensorboard --logdir /logs

-- COMMAND ----------

%set_cell_max_output_size_in_mb 10

-- COMMAND ----------

%skip print("This won't run")

-- COMMAND ----------

%%profile my_function()

-- COMMAND ----------

%%oprofile my_function()

-- COMMAND ----------

%uv pip install simplejson
