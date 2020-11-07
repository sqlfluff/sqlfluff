from sqlfluff.core.templaters import DbtTemplateInterface
import pytest
import os


@pytest.fixture()
def dbt_templater():
    """Returns an instance of the DbtTemplater."""
    return DbtTemplateInterface()


@pytest.fixture()
def in_dbt_project_dir():
    """A wrapper to chdir into the dbt_project fixture and back to cwd at the end of the test."""
    try:
        pre_test_dir = os.getcwd()
        os.chdir("test/fixtures/dbt_project")
        yield  # test runs here
    finally:
        os.chdir(pre_test_dir)

