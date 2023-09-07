"""A pytest plugin to build copier project from a template."""
from dataclasses import dataclass, field
from pathlib import Path
from shutil import rmtree
from typing import Any, Generator, Optional, Union

import pytest
import yaml
from copier import run_copy


@dataclass
class Result:
    """Holds the captured result of the copier project generation."""

    exception: Union[Exception, SystemExit, None] = None
    exit_code: Union[str, int, None] = 0
    project_dir: Optional[Path] = None
    answers: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a string representation of the result."""
        return f"<Result {self.exception or self.project_dir}>"


class Copie:
    """Class to provide convenient access to the copier API."""

    def __init__(
        self,
        default_template: Path,
        test_dir: Path,
        config_file: Path,
        counter: int = 0,
    ):
        """Initialize the Copie object."""
        self.default_template = default_template
        self.test_dir = test_dir
        self.config_file = config_file
        self.counter = counter

    def copy(self, extra_answers: dict = {}, template: Any = None) -> Result:
        """Create a copier Project from the template and return the associated Result object.

        Args:
            extra_answers: extra answers to pass to the Copie object and overwrite the default ones
            template: the template to use to create the project instead of the default ".".

        Returns:
            the Result object of the copier project generation
        """
        # set the template dir and the associated copier.yaml file
        template_dir = template or self.default_template
        copier_file = template_dir / "copier.yaml"

        # create a new output_dir in the test dir based on the counter value
        (output_dir := self.test_dir / f"copie{self.counter:03d}").mkdir()
        self.counter += 1

        try:
            # get the answers from default and overwrite the one present in extra_answers.
            questions = yaml.safe_load(copier_file.read_text())
            answers = {q: a.get("default", None) for q, a in questions.items()}
            answers = {**answers, **extra_answers}

            worker = run_copy(
                src_path=str(template_dir),
                dst_path=str(output_dir),
                data=answers,
                unsafe=True,
            )

            # the project path will be the first child of the ouptut_dir
            w_project_dir = next(d for d in worker.dst_path.glob("*") if d.is_dir())
            w_answers = worker._answers_to_remember()
            w_answers = {q: a for q, a in answers.items() if not q.startswith("_")}
            w_exception, w_exit_code = None, 0

        except SystemExit as e:
            w_exception, w_exit_code, w_project_dir, w_answers = e, e.code, None, {}  # type: ignore
        except Exception as e:
            w_exception, w_exit_code, w_project_dir, w_answers = e, -1, None, {}  # type: ignore

        return Result(w_exception, w_exit_code, w_project_dir, w_answers)


@pytest.fixture
def _copier_config_file(tmp_path_factory) -> Path:
    """Return a temporary copier config file."""
    # create a user from the tmp_path_factory fixture
    user_dir = tmp_path_factory.mktemp("user_dir")

    # create the different folders and files
    (copier_dir := user_dir / "copier").mkdir()
    (replay_dir := user_dir / "copier_replay").mkdir()

    # set up the configuration parameters in a config file
    config = {"copier_dir": str(copier_dir), "replay_dir": str(replay_dir)}
    (config_file := user_dir / "config").write_text(yaml.dump(config))

    return config_file


@pytest.fixture
def copie(request, tmp_path: Path, _copier_config_file: Path) -> Generator:
    """Yield an instance of the ``Copie`` helper class.

    The class can then be used to generate a project from a template.

    Args:
        request: the pytest request object
        tmp_path: the temporary directory
        _copier_config_file: the temporary copier config file

    Returns:
        the ``Copie`` instance

    Example:
        res = copie.copie(extra_context={"project_name": "foo"})
    """
    # extract the template directory from the pytest command parameter
    template_dir = Path(request.config.option.template)

    # set up a test directory in the tmp folder
    (test_dir := tmp_path / "copie").mkdir()

    yield Copie(template_dir, test_dir, _copier_config_file)

    # don't delete the files at the end of the test if requested
    if not request.config.option.keep_copied_projects:
        rmtree(test_dir)


def pytest_addoption(parser):
    """Add option to the pytest command."""
    group = parser.getgroup("copie")

    group.addoption(
        "--template",
        action="store",
        default=".",
        dest="template",
        help="specify the template to be rendered",
        type=str,
    )

    group.addoption(
        "--keep-copied-projects",
        action="store_true",
        default=False,
        dest="keep_copied_projects",
        help="Keep projects directories generated with 'copie.copie()'.",
    )


def pytest_configure(config):
    """Force the template path to be absolute to protect ourselves from fixtures that changes path."""
    config.option.template = str(Path(config.option.template).resolve())
