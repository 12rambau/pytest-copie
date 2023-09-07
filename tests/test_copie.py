"""Test the pytest_copie package."""


def test_copie_fixture(testdir, test_check):
    """Make sure that pytest accepts the "copie" fixture."""
    # create a tmp pytest module
    testdir.makepyfile(
        """
        def test_valid_fixture(copie):
            assert hasattr(copie, "copie")
            assert callable(copie.copie)
        """
    )

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")
    test_check(result, "test_valid_fixture")
    assert result.ret == 0


def test_copie_copie(testdir, copier_template, test_check):
    """Programmatically create a **Copier** template and use `copie` to create a project from it."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copie(extra_context={"repo_name": "helloworld"})

            assert result.exit_code == 0
            assert result.exception is None

            assert result.project_path.stem == "helloworld"
            assert result.project_path.is_dir()
            assert str(result) == f"<Result {result.project_path}>"
        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_copie_with_template_kwarg(testdir, copier_template, test_check):
    """Copie accepts a template kwarg."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copie(
                extra_context={"repo_name": "helloworld"},
                template=Path(r"%s"),
            )

            assert result.exit_code == 0
            assert result.exception is None
            assert result.project_path.stem == "helloworld"
            assert result.project_path.is_dir()

            assert str(result) == f"<Result {result.project_path}>"
        """
        % copier_template
    )

    # run pytest without the template cli arg
    result = testdir.runpytest("-v")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_copie_fixture_removes_directories(testdir, copier_template, test_check):
    """Check the copie fixture removes the output directories from one test to another."""
    testdir.makepyfile(
        """
        from pathlib import Path

        def test_create_result(copie):
            result = copie.copie()
            globals().update(result_path = result.project_path.parent)
            assert result.exception is None

        def test_previous_directory_is_removed(copie):
            assert result_path.is_dir() is False
        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_create_result")
    test_check(result, "test_previous_directory_is_removed")
    assert result.ret == 0


def test_copie_fixture_keeps_directories(testdir, copier_template, test_check):
    """Check the copie fixture keeps the output directories from one test to another."""
    testdir.makepyfile(
        """
        from pathlib import Path

        def test_create_result(copie):
            result = copie.copie()
            globals().update(result_path = result.project_path.parent)
            assert result.exception is None

        def test_previous_directory_is_kept(copie):
            assert result_path.is_dir() is True
    """
    )

    result = testdir.runpytest(
        "-v", f"--template={copier_template}", "--keep-copied-projects"
    )
    test_check(result, "test_create_result")
    test_check(result, "test_previous_directory_is_kept")
    assert result.ret == 0


def test_copie_result_context(testdir, copier_template, test_check):
    """Check that the result holds the rendered context."""
    testdir.makepyfile(
        """
        def test_copie_project(copie):
            result = copie.copie(extra_context={
                "repo_name": "cookies",
                "short_description": "copie is awesome",
            })

            assert result.exit_code == 0
            assert result.exception is None
            assert result.project_path.stem == 'cookies'
            assert result.project_path.is_dir()

            assert result.context == {
                "repo_name": "cookies",
                "short_description": "copie is awesome",
            }
            assert str(result) == f"<Result {result.project_path}>"
        """
    )

    result = testdir.runpytest("-v", f"--template={copier_template}")
    test_check(result, "test_copie_project")
    assert result.ret == 0


def test_cookies_group(testdir):
    """Make sure that pytest accepts the --cookies-group option."""
    result = testdir.runpytest("--help")
    result.stdout.fnmatch_lines(["copie:", "*--template=TEMPLATE*"])

    
def test_config(testdir, test_check):
    """Make sure that pytest accepts the `copie` fixture."""
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
