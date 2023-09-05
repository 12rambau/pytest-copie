"""Pytest session configuration."""

from pathlib import Path

import pytest
import yaml

# plugin integrated to pytest to test pytest itself (in our case the copie plugin)
pytest_plugins = "pytester"


@pytest.fixture
def copier_template(tmpdir) -> Path:
    """Create a default template for the copier project generation."""
    template_dir = tmpdir / "copie-template"
    template_dir.mkdir()
    template_file = template_dir / "copier.yaml"
    template_config = {
        "repo_name": {"type": "str", "default": "foobar"},
        "short_description": {
            "type": "str",
            "default": "Test Project",
        },
    }
    template_file.write_text(yaml.dump(template_config))

    template_readme = [
        r"{{ repo_name }}",
        "{% for _ in repo_name %}={% endfor %}",
        r"{{ short_description }}",
    ]

    repo_dir = template_dir / r"{{ repo_name }}"
    repo_dir.mkdir()
    readm_file = repo_dir / "README.rst"
    readm_file.write_text("\n".join(template_readme))

    return template_dir
