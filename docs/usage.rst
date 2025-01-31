Usage
=====

The :py:func:`copie <pytest_copie.plugin.copie>` fixture will allow you to :py:meth:`copy <pytest_copie.plugin.Copy.copy>` a template and run tests against it. It will also clean up the generated project after the tests have been run.

For these examples, let's assume the current folder is a copier template. it should include a ``copier.yml`` file and a ``template`` folder containing jinja templates.

.. tip::

   If needed you can also switch to the :py:func:`copie_session<pytest_copie.plugin.copie_session>` fixture to get the same functionalities but session scoped.

.. note::

   The name of the template folder can be anything as long as it matches the ``_subdirectory`` key in the ``copier.yml`` file.

.. code-block::

   demo_template/
   ├── template
   │   └── README.rst.jinja
   ├── tests/
   │   └── test_template.py
   └── copier.yaml

the ``copier.yaml`` file has the following content:

.. code-block:: yaml

   repo_name:
      type: str
      default: foobar
   short_description:
      type: str
      default: Test Project
   _subdirectory: template

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
        result = copie.copy()

        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_dir.is_dir()
        with open(result.project_dir / "README.rst") as f:
           assert f.readline() == "foobar\n"

It will generate a new repository based on your template, eg:

.. code-block::

   foobar/
   └── README.rst

the :py:class:`Return <pytest_copie.plugin.Return>` object can then be used to access the process outputs:

- :py:attr:`result.project_dir <pytest_copie.plugin.Return.project_dir>`
- :py:attr:`result.exception <pytest_copie.plugin.Return.exception>`
- :py:attr:`result.exit_code <pytest_copie.plugin.Return.exit_code>`
- :py:attr:`result.answers <pytest_copie.plugin.Return.answers>`

The temp folder will be cleaned up after the test is run.

Custom answers
--------------

Use the ``extra_answers`` parameter to pass custom answers to the ``copier.yaml`` questions.
The parameter is a dictionary with the question name as key and the answer as value.

.. code-block:: python

    def test_template_with_extra_answers(copie):
        result = copie.copy(extra_answers={"repo_name": "helloworld"})

        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_dir.is_dir()
        with open(result.project_dir / "README.rst") as f:
           assert f.readline() == "helloworld\n"

Custom template
---------------

By default :py:meth:`copy() <pytest_copie.plugin.Copy.copy>` looks for a copier template in the current directory.
This can be overridden on the command line by passing a ``--template`` parameter to pytest:

.. code-block:: console

   pytest --template TEMPLATE

You can also customize the template directory from a test by passing in the optional ``template`` parameter:

.. code-block:: python

   @pytest.fixture
   def custom_template(tmp_path) -> Path:
       # Create custom copier template directory
       (template := tmp_path / "copier-template").mkdir()
       questions = {"custom_name": {"type": "str", "default": "my_default_name"}}
       # Create custom subdirectory
       (repo_dir := template / "custom_template").mkdir()
       questions.update({"_subdirectory": "custom_template"})
       # Write the data to copier.yaml file
       (template /"copier.yaml").write_text(yaml.dump(questions, sort_keys=False))
       # Create custom template text files
       (repo_dir / "README.rst.jinja").write_text("{{custom_name}}\n")

       return template


   def test_copie_custom_project(copie, custom_template):

       result = copie.copy(
         template_dir=custom_template, extra_answers={"custom_name": "tutu"}
      )

       assert result.project_dir.is_dir()
       with open(result.project_dir / "README.rst") as f:
          assert f.readline() == "tutu\n"

.. important::

      The ``template`` parameter will override any ``--template`` parameter passed on the command line.

Keep output
-----------

By default :py:meth:`copie <pytest_copie.plugin.copie>` fixture removes copied projects at the end of the test.
However, you can pass the ``keep-copied-projects`` flag if you'd like to keep them in the temp directory.

.. note::

   It won't clutter as pytest only keeps the three newest temporary directories

.. code-block:: console

   pytest --keep-copied-projects
