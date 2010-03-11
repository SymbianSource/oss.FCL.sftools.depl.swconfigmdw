Plug-in directory structure
===========================

ConE plug-ins are divided into plug-in "packages", which enables a ConE
distribution to be built with a specific set of installed plug-ins. There is a ``common``
package that contains the default plug-ins that are always present in a ConE installation,
and any other plug-in package provides extra plug-ins in addition to these.

For example, one might build a 'vanilla' ConE distribution which contains only the
core ConE components and common plug-ins, or a 'symbian' distribution which contains
those as well as all Symbian-specific plug-ins.

The plug-in packages are simply sub-directories of ``source/plugins``. For example, the
following shows the current plug-in packages:

  .. image:: plugins-dir.png

As can be seen, there are three plug-in packages (``common``, ``example`` and ``symbian``)
and several utility Python files.

Package directory structure
---------------------------

Each plug-in package contains the sources of all plug-ins, an optional integration test set,
and a Python script to run all test cases related to the plug-in package. For example, the
following shows the contents of the ``common`` plug-in package:

  .. image:: plugins-common-dir.png

The naming of the sub-directories is important:

- Directories with a name of the form ``Cone*Plugin`` are considered to be plug-in sources
- If a directory with the name ``integration-test`` exists, it is expected to contain a
  ``runtests.py`` file that runs the integration tests

Plug-in source directory structure
----------------------------------

A plug-in source directory is expected to contain two things:

- A single Python module that contains the plug-in sources
- ``setup.py`` for packaging the plug-in into an egg (``setup.cfg`` and ``makefile`` are related to this)

The following shows the contents of the command plug-in directory in the common package:

  .. image:: plugins-common-commandplugin-dir.png

For an example with more complete descriptions see
:ref:`here <plugin-howto-example-plugin-dir-structure>`.

Integration test directory structure
------------------------------------

In addition to a collection of plug-in sources a plug-in package directory may contain an
``integration-test`` directory. This directory is supposed to contain integration tests
for the plug-ins by running actions (e.g. generate) using the ConE CLI to test that the plug-ins
work correctly from the topmost level.

File naming matters here too:

- Files of the form ``unittest_*.py`` are expected to contain the test cases
- If a file named ``export_standalone.py`` exists, it is expected to contain a function that
  exports any needed extra data when exporting the integration tests into a standalone test set.

For an example with more complete descriptions see
:ref:`here <plugin-howto-example-plugin-integration-tests`.