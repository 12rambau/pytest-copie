pytest-copie
============

.. toctree::
   :hidden:

   install
   usage
   contribute

Overview
--------

pytest-copie is a `pytest <https://github.com/pytest-dev/pytest>`__ plugin that comes with a ``copie`` fixture which is a wrapper for the `copier <https://github.com/copier-org/copier>`__ API for generating projects. It helps you verify that your template is working as expected and takes care of cleaning up after running the tests. :ledger:

It is an adaptation of the `pytest-cookies <https://github.com/hackebrot/pytest-cookies>`__ plugin for `copier <https://github.com/copier-org/copier>`__ templates.

It's here to help templates designers to check that everything works as expected on the generated files including (but not limited to):

- linting operations
- testing operations
- packaging operations
- documentation operations
- ...
