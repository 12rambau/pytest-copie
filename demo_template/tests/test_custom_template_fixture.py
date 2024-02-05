"""Demo example of how to use pytest-copie with a custom template fixture."""
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def custom_template(tmp_path) -> Path:
    """Generate a custom copier template to use as a pytest fixture."""
    # Create custom copier template directory and copier.yaml file
    (template := tmp_path / "copier-template").mkdir()
    questions = {"custom_name": {"type": "str", "default": "my_default_name"}}
    (template / "copier.yaml").write_text(yaml.dump(questions))
    # Create custom subdirectory
    (repo_dir := template / "custom_template").mkdir()
    (template / "copier.yaml").write_text(yaml.dump({"_subdirectory": "custom_template"}))
    # Create custom template text files
    (repo_dir / "README.rst.jinja").write_text("{{custom_name}}\n")

    return template


def test_copie_custom_project(copie, custom_template):
    """Test custom copier template fixture using pytest-copie."""
    result = copie.copy(template_dir=custom_template, extra_answers={"custom_name": "tutu"})

    assert result.project_dir.is_dir()
    with open(result.project_dir / "README.rst") as f:
        assert f.readline() == "tutu\n"
