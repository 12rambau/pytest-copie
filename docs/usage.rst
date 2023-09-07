Usage
=====

The ``copie`` fixture will allow you to ``copy`` a template and run tests against it. It will also clean up the generated project after the tests have been run.

For these examples, let's assume the current folder ``Path(".")`` is a copier template. it should include a ``copier.yml`` file and a ``{{repo_name}}`` folder containing jinja templates.

.. code-block::

   my_template/
   ├── {{repo_name}}/
   │   └── README.rst.jinja
   ├── tests/
   │   └── test_template.py
   └── copier.yaml

the copier.yaml file has the following content:

.. code-block:: yaml

   repo_name:
      type: str
      default": foobar
   short_description:
      type: str
      default: Test Project

And the readme template is:

.. code-block:: rst

   {{ repo_name }}
   ===============

   {{ short_description }}

default project
---------------

Use the following code in your test file to generate the project with all the default values:

.. code-block:: python

    def test_template(copie):
        res = copie.copy()

        assert res.exit_code == 0
        assert res.exception is None
        assert result.project_dir.name == "foobar"
        assert result.project_dir.is_dir()

It will generate a folder based on the default parameter of the ``copier.yaml`` file:

.. code-block::

   foobar/
   └── README.rst

the ``Return`` object can then be used to access the process outputs:

- ``result.project_dir``: the path to the generated project
- ``result.exception``: the exception raised by the process if any
- ``result.exit_code``: the exit code of the process
- ``result.answers``: the context used to generate the project (questions and answers)

The temp folder will be cleaned up after the test is run.

Custom answers
--------------

Use the ``extra_answers`` parameter to pass custom answers to the ``copier.yaml`` questions.
The parameter is a dictionary with the question name as key and the answer as value.

.. code-block:: python

    def test_template(copie):
        res = copie.copy(extra_answers={"repo_name": "helloworld"})

        assert result.project_dir.name == "helloworld"

Custom template
---------------

By default ``copie.copy()`` looks for a copier template in the current directory.
This can be overridden on the command line by passing a ``--template`` parameter to pytest:

.. code-block:: console

   pytest --template TEMPLATE

You can also customize the template directory from a test by passing in the optional ``template`` parameter:

.. code-block:: python

   @pytest.fixture
   def custom_template(tmp_path) -> Path:

    (template := tmp / "copier-template").mkdir()
    questions = {"toto": {"type": "str", "default": "toto"}
    (template /"copier.yaml").write_text(yaml.dump(questions))
    (repo_dir := template / "{{toto}}").mkdir()
    (repo_dir / "README.rst.jinja").write("{{toto}}")

    return template


   def test_copie_custom_project(copie, custom_template):

      result = copie.copy(template=str(custom_template), extra_answers={"toto": "tutu"})

      assert result.project_dir.name == "tutu"
      assert result.project_dir.is_dir()

.. important::

      The ``template`` parameter will override any ``--template`` parameter passed on the command line.

Keep output
-----------

By default ``copie`` removes copied projects.
However, you can pass the ``keep-copied-projects`` flag if you'd like to keep them in the temp directory.

.. note::

   It won't clutter as pytest only keeps the three newest temporary directories

.. code-block:: console

   pytest --keep-copied-projects
