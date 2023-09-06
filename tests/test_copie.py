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

    # fnmatch_lines does an assertion internally
    test_check(result, "test_valid_fixture")

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_copie_copie(testdir, copier_template, test_check):
    """Programmatically create a **Copier** template and use `copie` to create a project from it."""
    testdir.makepyfile(
        """
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


def test_copie_copie_with_template_kwarg(testdir, copier_template, test_check):
    """Copie accepts a template kwarg."""
    testdir.makepyfile(
        """
        from pathlib import Path
        def test_copie_project(copie):
            result = copie.copie(
                extra_context={"repo_name": "helloworld"},
                template=Path("%s"),
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
