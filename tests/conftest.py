"""Pytest session configuration."""
from pathlib import Path
from typing import Callable

import pytest
import yaml

# plugin integrated to pytest to test pytest itself (in our case the copie plugin)
pytest_plugins = "pytester"


@pytest.fixture
def copier_template(tmpdir) -> Path:
    """Create a default template for the copier project generation."""
    # set up the configuration parameters
    template_config = {
        "repo_name": {"type": "str", "default": "foobar"},
        "short_description": {
            "type": "str",
            "default": "Test Project",
        },
        "_subdirectory": "project",
    }

    # content of a fake readme file
    template_readme = [
        r"{{ repo_name }}",
        "{% for _ in repo_name %}={% endfor %}",
        r"{{ short_description }}",
    ]

    # create all the folders and files
    (template_dir := Path(tmpdir) / "copie-template").mkdir()
    (template_dir / "copier.yaml").write_text(yaml.dump(template_config), "utf-8")
    (repo_dir := template_dir / r"project").mkdir()
    (repo_dir / "README.rst.jinja").write_text("\n".join(template_readme), "utf-8")

    return template_dir


@pytest.fixture(scope="session")
def test_check() -> Callable:
    """Return a method to test valid copiage."""

    def _test_check(result, test_name):
        result.stdout.re_match_lines([f".*::{test_name} (?:✓|PASSED).*"])

    return _test_check
