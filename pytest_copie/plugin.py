"""A pytest plugin to build copier project from a template."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Union

import pytest
import yaml
from copier import run_copy


@dataclass
class Result:
    """Holds the captured result of the copier project generation."""

    exception: Union[Exception, SystemExit, None] = None
    exit_code: int = 0
    # context: Optional[Any]  = None
    _project_path: Optional[Path] = None

    @property
    def project_path(self) -> Optional[Path]:
        """Return the project dir if no exception occurred."""
        if self.exception is None:
            return self._project_path
        return None

    def __repr__(self) -> str:
        """Return a string representation of the result."""
        return f"Result {self.exception or self.project_path}"


@dataclass
class Copie:
    """Class to provide convenient access to the copier API."""

    _default_template: Path
    _output_factory: Callable
    _config_file: Path
    _counter: int = 0

    def _new_output_dir(self) -> Path:
        """Return a new output dir based on the counter value."""
        dirname = f"bake{self._counter:03d}"
        self._counter += 1
        return self._output_factory(dirname)

    def copie(self, extra_context: Any = None, template: Any = None) -> Result:
        """Create a copier Project from the template and return the result.

        Args:
            extra_context: extra context to pass to the copier
            template: the template to use to create the project

        Returns:
            the Result object of the copier project generation
        """
        exception = None
        exit_code = 0
        project_path = None
        # context = None

        template = template or self._default_template
        template / "copier.yaml"

        try:

            worker = run_copy(
                src_path=str(template),
                dts_path=str(self._new_output_dir()),
            )

            project_path = worker.dts_path

            # get the context
            # context = project.get_template_context(context_file)

            # get the project dir
            # project_dir = project.path

        except SystemExit as e:
            exception, exit_code = e, e.code  # type: ignore
        except Exception as e:
            exception, exit_code = e, -1  # type: ignore

        return Result(exception, exit_code, project_path)


@pytest.fixture
def _copier_config_file(tmp_path_factory):
    """Return a temporary copier config file."""
    user_dir = tmp_path_factory.mktemp("user_dir")
    config_file = user_dir / "config"

    copier_dir = user_dir / "copier"
    copier_dir.mkdir()
    replay_dir = user_dir / "replay_dir"
    replay_dir.mkdir()
    config = {
        "copier_dir": str(copier_dir),
        "replay_dir": str(replay_dir),
    }

    with config_file.open("w") as f:
        yaml.dump(config, f, Dumper=yaml.Dumper)

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
    template_dir = Path(".")
    output_dir = tmp_path / "copie"
    output_dir.mkdir()

    def output_factory(dirname: str) -> Path:
        new_dir = output_dir / dirname
        new_dir.mkdir()
        return new_dir

    yield Copie(template_dir, output_factory, _copier_config_file)

    # add an option to destroy the resulting file after the test
