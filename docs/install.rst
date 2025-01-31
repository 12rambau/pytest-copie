Installation
============

**pytest-copie** is available on `PyPI <https://pypi.org/project/pytest-copie/>`__ and can be installed with `pip <https://pip.pypa.io/en/stable/>`__:

.. code-block:: console

    pip install pytest-copie

Alternatively it is also available on `conda-forge <https://anaconda.org/conda-forge/pytest-copie>`__ and can be installed with `conda <https://docs.conda.io/en/latest/>`__:

.. code-block:: console

    conda install pytest-copie

.. warning::

    `pytest` is loading all the existing plugin from the running environment which is a super powerful feature of the framework. As this is a port of `pytest-cookies`,
    the 2 plugin will conflict with one another if installed in together as reported in https://github.com/12rambau/pytest-copie/issues/85. We highly recommend to run your tests
    in dedicated environements siloted from one another.
