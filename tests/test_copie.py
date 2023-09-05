"""Test the pytest_copie package."""


def test_copie_fixture(testdir):
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
    result.stdout.fnmatch_lines(["*::test_valid_fixture ✓*"])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
