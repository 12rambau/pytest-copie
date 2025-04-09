
pytest-copie
============

.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg?logo=opensourceinitiative&logoColor=white
    :target: LICENSE
    :alt: License: MIT

.. |commit| image:: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git&logoColor=white
   :target: https://conventionalcommits.org
   :alt: conventional commit

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: ruff badge

.. |prettier| image:: https://img.shields.io/badge/code_style-prettier-ff69b4.svg?logo=prettier&logoColor=white
   :target: https://github.com/prettier/prettier
   :alt: prettier badge

.. |pre-commmit| image:: https://img.shields.io/badge/pre--commit-active-yellow?logo=pre-commit&logoColor=white
    :target: https://pre-commit.com/
    :alt: pre-commit

.. |pypi| image:: https://img.shields.io/pypi/v/pytest-copie?color=blue&logo=pypi&logoColor=white
    :target: https://pypi.org/project/pytest-copie/
    :alt: PyPI version

.. |conda| image:: https://img.shields.io/conda/v/conda-forge/pytest-copie?logo=condaforge&logoColor=white&color=blue
   :target: https://anaconda.org/conda-forge/pytest-copie
   :alt: Conda

.. |build| image:: https://img.shields.io/github/actions/workflow/status/12rambau/pytest-copie/unit.yaml?logo=github&logoColor=white
    :target: https://github.com/12rambau/pytest-copie/actions/workflows/unit.yaml
    :alt: build

.. |coverage| image:: https://img.shields.io/codecov/c/github/12rambau/pytest-copie?logo=codecov&logoColor=white
    :target: https://codecov.io/gh/12rambau/pytest-copie
    :alt: Test Coverage

.. |docs| image:: https://img.shields.io/readthedocs/pytest-copie?logo=readthedocs&logoColor=white
    :target: https://pytest-copie.readthedocs.io/en/latest/
    :alt: Documentation Status

|license| |commit| |ruff| |prettier| |pre-commmit| |pypi| |build| |coverage| |docs| |conda|

Overview
--------

pytest-copie is a `pytest <https://github.com/pytest-dev/pytest>`__ plugin that comes with a ``copie`` fixture which is a wrapper on top the `copier <https://github.com/copier-org/copier>`__ API for generating projects. It helps you verify that your template is working as expected and takes care of cleaning up after running the tests. :ledger:

It is an adaptation of the `pytest-cookies <https://github.com/hackebrot/pytest-cookies>`__ plugin for `copier <https://github.com/copier-org/copier>`__ templates.

It’s here to help templates designers to check that everything works as expected on the generated files including (but not limited to):

-   linting operations
-   testing operations
-   packaging operations
-   documentation operations
-   …

Installation
------------

**pytest-copie** is available on `PyPI <https://pypi.org/project/pytest-copie/>`__ and can be installed with `pip <https://pip.pypa.io/en/stable/>`__:

.. code-block:: console

    pip install pytest-copie

Usage
-----

The ``copie`` fixture will allow you to ``copy`` a template and run tests against it. It will also clean up the generated project after the tests have been run.

.. code-block:: python

    def test_template(copie):
        res = copie.copy(extra_answers={"repo_name": "helloworld"})

        assert res.exit_code == 0
        assert res.exception is None
        assert result.project_dir.is_dir()

Context and template location can be fully customized, see our `documentation <https://pytest-copie.readthedocs.io>`__ for more details.

Credits
-------

This package was created with `Copier <https://copier.readthedocs.io/en/latest/>`__ and the `@12rambau/pypackage <https://github.com/12rambau/pypackage>`__ 0.1.16 project template.
