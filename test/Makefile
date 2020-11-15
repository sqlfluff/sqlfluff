DBT_CMD := $(shell command -v dbt)

fixtures/dbt_project/dbt_modules:
ifndef DBT_CMD
	$(info "dbt was not found, skipping..")
else
	cd fixtures/dbt_project && dbt deps
endif

