"""A pytest plugin to build copier project from a template."""
from dataclasses import dataclass, field
from pathlib import Path
from shutil import rmtree
from typing import Generator, Optional, Union

import pytest
import yaml
from _pytest.tmpdir import TempPathFactory
from copier import run_copy


@dataclass
class Result:
    """Holds the captured result of the copier project generation."""

    exception: Union[Exception, SystemExit, None] = None
    "The exception raised during the copier project generation."

    exit_code: Union[str, int, None] = 0
    "The exit code of the copier project generation."

    project_dir: Optional[Path] = None
    "The path to the generated project."

    answers: dict = field(default_factory=dict)
    "The answers used to generate the project."

    def __repr__(self) -> str:
        """Return a string representation of the result."""
        return f"<Result {self.exception or self.project_dir}>"


@dataclass
class Copie:
    """Class to provide convenient access to the copier API."""

    default_template_dir: Path
    "The path to the default template to use to create the project."

    test_dir: Path
    "The directory where the project will be created."

    config_file: Path
    "The path to the copier config file."

    counter: int = 0
    "A counter to keep track of the number of projects created."

    def copy(self, extra_answers: dict = {}, template_dir: Optional[Path] = None) -> Result:
        """Create a copier Project from the template and return the associated :py:class:`Result <pytest_copie.plugin.Result>` object.

        Args:
            extra_answers: extra answers to pass to the Copie object and overwrite the default ones
            template_dir: the path to the template to use to create the project instead of the default ".".

        Returns:
            the result of the copier project generation
        """
        # set the template dir and the associated copier.yaml file
        template_dir = template_dir or self.default_template_dir
        files = template_dir.glob("copier.*")
        try:
            copier_yaml = next(f for f in files if f.suffix in [".yaml", ".yml"])
        except StopIteration:
            raise FileNotFoundError("No copier.yaml configuration file found.")

        # create a new output_dir in the test dir based on the counter value
        (output_dir := self.test_dir / f"copie{self.counter:03d}").mkdir()
        self.counter += 1

        try:

            # make sure the copiercopier project is using subdirectories
            _add_yaml_include_constructor(template_dir)

            all_params = yaml.safe_load_all(copier_yaml.read_text())
            if not any("_subdirectory" in params for params in all_params):
                raise ValueError(
                    "The plugin can only work for templates using subdirectories, "
                    '"_subdirectory" key is missing from copier.yaml'
                )

            worker = run_copy(
                src_path=str(template_dir),
                dst_path=str(output_dir),
                unsafe=True,
                defaults=True,
                user_defaults=extra_answers,
                vcs_ref="HEAD",
            )

            # refresh project_dir with the generated one
            # the project path will be the first child of the ouptut_dir
            project_dir = Path(worker.dst_path)

            # refresh answers with the generated ones and remove private stuff
            answers = worker._answers_to_remember()
            answers = {q: a for q, a in answers.items() if not q.startswith("_")}

            return Result(project_dir=project_dir, answers=answers)

        except SystemExit as e:
            return Result(exception=e, exit_code=e.code)
        except Exception as e:
            return Result(exception=e, exit_code=-1)


@pytest.fixture(scope="session")
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
    """Yield an instance of the :py:class:`Copie <pytest_copie.plugin.Copie>` helper class.

    The class can then be used to generate a project from a template.

    Args:
        request: the pytest request object
        tmp_path: the temporary directory
        _copier_config_file: the temporary copier config file

    Returns:
        the object instance, ready to copy !
    """
    # extract the template directory from the pytest command parameter
    template_dir = Path(request.config.option.template)

    # set up a test directory in the tmp folder
    (test_dir := tmp_path / "copie").mkdir()

    yield Copie(template_dir, test_dir, _copier_config_file)

    # don't delete the files at the end of the test if requested
    if not request.config.option.keep_copied_projects:
        rmtree(test_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def copie_session(
    request, tmp_path_factory: TempPathFactory, _copier_config_file: Path
) -> Generator:
    """Yield an instance of the :py:class:`Copie <pytest_copie.plugin.Copie>` helper class.

    The class can then be used to generate a project from a template.

    Args:
        request: the pytest request object
        tmp_path_factory: the temporary directory
        _copier_config_file: the temporary copier config file

    Returns:
        the object instance, ready to copy !
    """
    # extract the template directory from the pytest command parameter
    template_dir = Path(request.config.option.template)

    # set up a test directory in the tmp folder
    test_dir = tmp_path_factory.mktemp("copie")

    yield Copie(template_dir, test_dir, _copier_config_file)

    # don't delete the files at the end of the test if requested
    if not request.config.option.keep_copied_projects:
        rmtree(test_dir, ignore_errors=True)


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


def _add_yaml_include_constructor(
    template_dir: Path,
):
    """Adds an include constructor to yaml.SafeLoader."""

    def include_constructor(
        loader: yaml.SafeLoader,
        node: yaml.Node,
    ):
        fullpath = template_dir / node.value

        if not fullpath.is_file():
            raise FileNotFoundError(f"The filename '{fullpath}' does not exist.")

        with fullpath.open("rb") as f:
            return yaml.safe_load(f)

    yaml.add_constructor("!include", include_constructor, yaml.SafeLoader)
