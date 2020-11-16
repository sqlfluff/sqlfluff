fixtures/dbt_project/dbt_modules:
ifeq (,$(shell which dbt))
	$(info "dbt was not found, skipping..")
else
	cd fixtures/dbt_project && dbt deps
endif
