"""Demo example of how to test a copier template with pytest-copie."""
from pathlib import Path


def test_template(copie):
    """Test the demo copier template using pytest-copie."""
    # This demo copier template is a subdirectory of the main repository
    # so we have to specify the location for pytest.
    # Users who have `copier.yaml` at the top level of their repository
    # can delete the template_dir keyword argument here.
    demo_template_dir = Path(__file__).parent.parent

    result = copie.copy(template_dir=demo_template_dir)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_dir.is_dir()
    with open(result.project_dir / "README.rst") as f:
        assert f.readline() == "foobar\n"


def test_template_with_extra_answers(copie):
    """Test the demo copier template with extra answers using pytest-copie."""
    # This demo copier template is a subdirectory of the main repository
    # so we have to specify the location for pytest.
    # Users who have `copier.yaml` at the top level of their repository
    # can delete the template_dir keyword argument here.
    demo_template_dir = Path(__file__).parent.parent

    result = copie.copy(extra_answers={"name": "helloworld"}, template_dir=demo_template_dir)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_dir.is_dir()
    with open(result.project_dir / "README.rst") as f:
        assert f.readline() == "helloworld\n"
