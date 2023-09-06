"""A pytest plugin to build copier project from a template."""

from pathlib import Path
from typing import Any, Callable, Generator, Optional, Union

import pytest
import yaml
from copier import run_copy


class Result:
    """Holds the captured result of the copier project generation."""

    def __init__(
        self,
        exception: Union[Exception, SystemExit, None] = None,
        exit_code: Union[str, int, None] = 0,
        _project_path: Optional[Path] = None,
        context: dict = {},
    ):
        """Initialize the Result object."""
        self.exception = exception
        self.exit_code = exit_code
        self._project_path = _project_path
        self.context = context

    @property
    def project_path(self) -> Optional[Path]:
        """Return the project dir if no exception occurred."""
        if self.exception is None:
            return self._project_path
        return None

    def __repr__(self) -> str:
        """Return a string representation of the result."""
        return f"<Result {self.exception or self.project_path}>"


class Copie:
    """Class to provide convenient access to the copier API."""

    def __init__(
        self,
        _default_template: Path,
        _output_factory: Callable,
        _config_file: Path,
        _counter: int = 0,
    ):
        """Initialize the Copie object."""
        self._default_template = _default_template
        self._output_factory = _output_factory
        self._config_file = _config_file
        self._counter = _counter

    @property
    def default_template(self) -> Path:
        """Return the path to the default template."""
        return self._default_template

    def _new_output_dir(self) -> Path:
        """Return a new output dir based on the counter value."""
        dirname = f"copie{self._counter:03d}"
        self._counter += 1
        return self._output_factory(dirname)

    def copie(self, extra_context: dict = {}, template: Any = None) -> Result:
        """Create a copier Project from the template and return the result.

        Args:
            extra_context: extra context to pass to the copier
            template: the template to use to create the project

        Returns:
            the Result object of the copier project generation
        """
        exception: Union[None, SystemExit, Exception] = None
        exit_code: Union[str, int, None] = 0
        project_path = None
        context_out = {}

        template_dir = template or self.default_template
        context_file = template_dir / "copier.yaml"

        output_dir = self._new_output_dir()
        print(f"output_dir: {output_dir.resolve()}")

        try:
            # write the answers in the destination folder so they are used by the worker
            config = yaml.safe_load(context_file.read_text())
            context = {k: v.get("default", None) for k, v in config.items()}
            context = {**context, **extra_context}

            worker = run_copy(
                src_path=str(template_dir),
                dst_path=str(output_dir),
                data=context,
                unsafe=True,
                answers_file=".copier-answers.yml",
            )

            # the project path will be the first child of the ouptut_dir
            project_path = next(d for d in worker.dst_path.glob("*") if d.is_dir())
            context_out = yaml.safe_load(
                (project_path / ".copier-answers.yml").read_text()
            )

        except SystemExit as e:
            exception, exit_code = e, e.code
        except Exception as e:
            exception, exit_code = e, -1

        return Result(exception, exit_code, project_path, context_out)


@pytest.fixture
def _copier_config_file(tmp_path_factory):
    """Return a temporary copier config file."""
    # create a user from the tmp_path_factory fixture
    user_dir = tmp_path_factory.mktemp("user_dir")

    # create the different folders and files
    (copier_dir := user_dir / "copier").mkdir()
    (replay_dir := user_dir / "replay_dir").mkdir()

    # set up the configuration parameters in a config file
    config = {
        "copier_dir": str(copier_dir),
        "replay_dir": str(replay_dir),
    }

    (config_file := user_dir / "config").write_text(yaml.dump(config))

    return config_file


@pytest.fixture
def copie(request, tmp_path: Path, _copier_config_file: Path) -> Generator:
    """Yield an instance of the Copie helper class.

    The class can then be used to generate a project from a template

    Args:
        request: the pytest request object
        tmp_path: the temporary directory
        _copier_config_file: the temporary copier config file

    Returns:
        the Copie instance

    Example:
        res = copie.copie(extra_context={"project_name": "foo"})
    """
    template_dir = Path(request.config.option.template)
    (output_dir := tmp_path / "copie").mkdir()

    def output_factory(dirname: str) -> Path:
        (new_dir := output_dir / dirname).mkdir()
        return new_dir

    yield Copie(template_dir, output_factory, _copier_config_file)

    # delete the files if necessary
    # if not request.config.option.keep_copied_projects:
    #    rmtree(output_dir)


def pytest_addoption(parser):
    """Add option to the pytest command."""
    group = parser.getgroup("copie")

    # --template option
    group.addoption(
        "--template",
        action="store",
        default=".",
        dest="template",
        help="specify the template to be rendered",
        type=str,
    )

    # --keep-copied-projects option
    group.addoption(
        "--keep-copied-projects",
        action="store_true",
        default=False,
        dest="keep_copied_projects",
        help="Keep projects directories generated with 'copie.copie()'.",
    )


def pytest_configure(config):
    """Force the template path to be absolute to protect ourselves from feature that changes path."""
    config.option.template = str(Path(config.option.template).resolve())
