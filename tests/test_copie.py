"""Test the pytest_copie package."""


def test_copie_fixture(testdir, test_check):
    """Make sure that pytest accepts the "copie" fixture."""
    # create a tmp pytest module
    testdir.makepyfile(
        """
        def test_valid_fixture(copie):
            assert hasattr(copie, "copy")
            assert callable(copie.copy)
        """
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")
    test_check(result, "test_valid_fixture")
    assert result.ret == 0


def test_copie_copy(testdir, copier_template, test_check, template_default_content):
    """Programmatically create a **Copier** template and use `copy` to create a project from it."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copy()

            assert result.exit_code == 0
            assert result.exception is None

            assert result.project_dir.stem.startswith("copie")
            assert result.project_dir.is_dir()
            assert str(result) == f"<Result {result.project_dir}>"
            readme_file = result.project_dir / "README.rst"
            assert readme_file.is_file()
            assert readme_file.read_text() == "%s"
        """
        % template_default_content
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_copy_without_subdirectory(
    testdir, incomplete_copier_template, test_check
):
    """Programmatically create a **Copier** template and use `copy` to create a project from it."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):

            result = copie.copy()

            assert result.exit_code == -1
            assert isinstance(result.exception, ValueError)
        """
    )

    result = testdir.runpytest("-v", f"--template={incomplete_copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_copy_with_extra(testdir, copier_template, test_check):
    """Programmatically create a **Copier** template and use `copy` to create a project from it."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copy(extra_answers={"repo_name": "helloworld"})
            templated_file = result.project_dir / "helloworld.txt"
            assert templated_file.is_file()

        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_with_template_kwarg(testdir, copier_template, test_check):
    """Check that copie accepts a template kwarg."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copy(
                extra_answers={"repo_name": "helloworld"}, template_dir=Path(r"%s"),
            )
            assert result.exit_code == 0
            assert result.exception is None
            assert result.project_dir.stem.startswith("copie")
            assert result.project_dir.is_dir()

            assert str(result) == f"<Result {result.project_dir}>"
        """
        % copier_template
    )

    # run pytest without the template cli arg
    result = testdir.runpytest("-v")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_fixture_removes_directories(testdir, copier_template, test_check):
    """Check the copie fixture removes the test directories from one test to another."""
    testdir.makepyfile(
        """
        from pathlib import Path

        def test_create_dir(copie):
            result = copie.copy()
            globals().update(test_dir = result.project_dir.parent)
            assert result.exception is None

        def test_previous_dir_is_removed(copie):
            assert test_dir.is_dir() is False
        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_create_dir")
    test_check(result, "test_previous_dir_is_removed")
    assert result.ret == 0


def test_copie_fixture_keeps_directories(testdir, copier_template, test_check):
    """Check the copie fixture keeps the test directories from one test to another."""
    testdir.makepyfile(
        """
        from pathlib import Path

        def test_create_dir(copie):
            result = copie.copy()
            globals().update(test_dir = result.project_dir.parent)
            assert result.exception is None

        def test_previous_dir_is_kept(copie):
            assert test_dir.is_dir() is True
    """
    )

    result = testdir.runpytest(
        "-v", f"--template={copier_template}", "--keep-copied-projects"
    )
    test_check(result, "test_create_dir")
    test_check(result, "test_previous_dir_is_kept")
    assert result.ret == 0


def test_copie_result_context(testdir, copier_template, test_check):
    """Check that the result holds the rendered answers."""
    testdir.makepyfile(
        """
        def test_copie_project(copie):
            my_answers = {'repo_name': 'foobar', "short_description": "copie is awesome"}
            default_answers = {"test_templated": "foobar", "test_value": "value"}
            result = copie.copy(extra_answers=my_answers)
            assert result.project_dir.stem.startswith("copie")
            assert result.answers == {**my_answers, **default_answers}
        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_cookies_group(testdir):
    """Check that pytest registered the --cookies-group option."""
    result = testdir.runpytest("--help")
    result.stdout.fnmatch_lines(["copie:", "*--template=TEMPLATE*"])


def test_config(testdir, test_check):
    """Check that pytest accepts the `copie` fixture."""
    # create a temporary pytest test module
    testdir.makepyfile(
        """
        import yaml

        def test_user_dir(tmp_path_factory, _copier_config_file):
            basetemp = tmp_path_factory.getbasetemp()
            assert _copier_config_file.stem == "config"
            user_dir = _copier_config_file.parent
            assert user_dir.stem.startswith("user_dir")
            assert user_dir.parent == basetemp


        def test_valid_copier_config(_copier_config_file):
            with open(_copier_config_file) as f:
                config = yaml.safe_load(f)
            user_dir = _copier_config_file.parent
            expected = {
                "copier_dir": str(user_dir / "copier"),
                "replay_dir": str(user_dir / "copier_replay"),
            }
            assert config == expected
        """
    )

    result = testdir.runpytest("-v")
    test_check(result, "test_user_dir")
    test_check(result, "test_valid_copier_config")
    assert result.ret == 0
