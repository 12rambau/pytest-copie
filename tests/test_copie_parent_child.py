"""
Unit-tests for the “parent / child Copier template” feature.

The tests create two miniature Copier templates:

* parent_template/
      copier.yml
      parent_project/
          external_data.txt.jinja  -> "parent-data"

* child_template/
      copier.yml
      child_project/
          child.txt.jinja          -> "child-generated"

The new `copie` fixture must                                   │
  - render the parent first,                                   │
  - copy the resulting files into the child's output-dir, and  │
  - render the child successfully inside the parent            └── tested here
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from _pytest.pytester import Pytester


def _create_parent_template(base: Path) -> Path:
    """Return a ready-to-use *parent* Copier template."""
    tpl = base / "parent_template"
    proj = tpl / "template"
    proj.mkdir(parents=True)

    # minimal copier.yml - must use a subdirectory
    (tpl / "copier.yml").write_text(
        textwrap.dedent(
            """\
        _subdirectory: template
        _answers_file: .parent-answers.yml
        project_name: parent project
        """
        )
    )

    # File created by parent
    (proj / "parent_file.txt.jinja").write_text(
        textwrap.dedent(
            """\
        parent-data
        {{ project_name }}
        """
        )
    )

    # Parent answers file
    (proj / "{{ _copier_conf.answers_file }}.jinja").write_text(
        textwrap.dedent(
            """\
        # Changes here will be overwritten by Copier; NEVER EDIT MANUALLY
        {{ _copier_answers|to_nice_yaml -}}
        """
        )
    )

    return tpl


def _create_child_template(base: Path) -> Path:
    """Return a ready-to-use *child* Copier template."""
    tpl = base / "child_template"
    proj = tpl / "template"
    proj.mkdir(parents=True)

    # minimal copier.yml - must use a subdirectory
    (tpl / "copier.yml").write_text(
        textwrap.dedent(
            """\
        _subdirectory: template
        _answers_file: .child-answers.yml
        child_name: foo bar
        _external_data:
            parent_tpl: .parent-answers.yml
        project_name: "{{ _external_data.parent_tpl.project_name }}"
        """
        )
    )

    # File created by child
    (proj / "child.txt.jinja").write_text(
        textwrap.dedent(
            """\
        child-generated
        {{ project_name }}
        {{ child_name }}
        """
        )
    )

    # Child answers file
    (proj / "{{ _copier_conf.answers_file }}.jinja").write_text(
        textwrap.dedent(
            """\
        # Changes here will be overwritten by Copier; NEVER EDIT MANUALLY
        {{ _copier_answers|to_nice_yaml -}}
        """
        )
    )

    return tpl


# --------------------------------------------------------------------------- #
#                               Happy-path test                               #
# --------------------------------------------------------------------------- #
def test_parent_child_roundtrip(testdir: Pytester) -> None:
    """The child template is rendered with the files coming from its parent."""
    # ------------------------------------------------------------------ setup
    tmp = Path(testdir.tmpdir)
    parent_tpl = _create_parent_template(tmp)
    child_tpl = _create_child_template(tmp)

    # escape back-slashes for the inline test-code (Windows friendly)
    parent_tpl_s = str(parent_tpl).replace("\\", "\\\\")
    child_tpl_s = str(child_tpl).replace("\\", "\\\\")

    # ----------------------------------------------------------------- inline
    testdir.makepyfile(
        f"""
        from pathlib import Path

        def test_parent_child(copie):
            parent_template = Path(r"{parent_tpl_s}")
            child_template  = Path(r"{child_tpl_s}")

            # -------- parent ------------------------------------------------
            parent_result = copie.copy(template_dir=parent_template)
            assert parent_result.exit_code == 0
            assert (parent_result.project_dir / "parent_file.txt").is_file()

            # -------- child -------------------------------------------------
            child_copie   = copie(parent_result=parent_result,
                                  child_tpl=child_template)
            child_result  = child_copie.copy()
            assert child_result.exit_code == 0

            # The parent's file must have been copied *in to* the child project
            parent_file = child_result.project_dir / "parent_file.txt"
            assert parent_file.is_file()
            assert parent_file.read_text() == "parent-data\\nparent project\\n"

            # The child's file must have been rendered successfully
            child_file = child_result.project_dir / "child.txt"
            assert child_file.is_file()
            assert child_file.read_text() == "child-generated\\nparent project\\nfoo bar\\n"
        """
    )

    res = testdir.runpytest("-v")
    res.assert_outcomes(passed=1)


# --------------------------------------------------------------------------- #
#                         Validation / error-handling test                    #
# --------------------------------------------------------------------------- #
def test_invalid_parent_result_rejected(testdir: Pytester) -> None:
    """A parent ``Result`` with a non-zero exit-code must raise a ``ValueError``."""
    tmp = Path(testdir.tmpdir)
    dummy_child_tpl = _create_child_template(tmp)

    child_tpl_s = str(dummy_child_tpl).replace("\\", "\\\\")

    testdir.makepyfile(
        f"""
        from pathlib import Path
        import pytest
        from pytest_copie.plugin import Result

        def test_invalid_parent(copie, tmp_path):
            bad_parent = Result(exit_code=1, project_dir=tmp_path)   # ← invalid!
            child      = copie(parent_result=bad_parent,
                                child_tpl=Path(r"{child_tpl_s}"))
            with pytest.raises(ValueError, match="successful exit code"):
                child.copy()
        """
    )

    res = testdir.runpytest("-v")
    res.assert_outcomes(passed=1)
