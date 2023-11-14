from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Optional, Union

@dataclass
class Result:
    exception: Union[Exception, SystemExit, None] = ...
    exit_code: Union[str, int, None] = ...
    project_dir: Optional[Path] = ...
    answers: dict = ...
    def __repr__(self) -> str: ...
    def __init__(self, exception, exit_code, project_dir, answers) -> None: ...

@dataclass
class Copie:
    default_template_dir: Path
    test_dir: Path
    config_file: Path
    counter: int = ...
    def copy(
        self, extra_answers: dict = ..., template_dir: Optional[Path] = ...
    ) -> Result: ...
    def __init__(
        self, default_template_dir, test_dir, config_file, counter
    ) -> None: ...

def _copier_config_file(tmp_path_factory) -> Path: ...
def copie(request, tmp_path: Path, _copier_config_file: Path) -> Generator: ...
def pytest_addoption(parser) -> None: ...
def pytest_configure(config) -> None: ...
