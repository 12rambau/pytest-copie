pytest-copie
============

.. toctree::
   :hidden:

   install
   usage
   contribute

Overview
--------

pytest-copie is a `pytest <https://github.com/pytest-dev/pytest>`__ plugin that comes with a :py:func:`copie <pytest_copie.plugin.copie>` fixture which is a wrapper on top of the `copier <https://github.com/copier-org/copier>`__ API for generating projects. It helps you verify that your template is working as expected and takes care of cleaning up after running the tests. |:ledger:|

It is an adaptation of the `pytest-cookies <https://github.com/hackebrot/pytest-cookies>`__ plugin for `copier <https://github.com/copier-org/copier>`__ templates.

It's here to help templates designers to check that everything works as expected on the generated files including (but not limited to):

- linting operations
- testing operations
- packaging operations
- documentation operations
- ...

.. note::

   As this lib is designed to perform test on **copier** template, the test suit is expected to be outside of the source directory copied by **copier**. It can thus only be used in templates using ``subdirectories``. Using it in a raw template will raise a ``ValueError``.

.. warning::

   This plugin is called ``pytest-copie`` as the french word for a "copy" object. It should not be confused with ``pytest-copier`` another plugin using different approach that is still in the development phase.   You can find their repository  `here <https://github.com/noirbizarre/pytest-copier>`__.   A conversation about a potential merge of the two projects is ongoing `here <https://github.com/noirbizarre/pytest-copier/issues/9>`__.
