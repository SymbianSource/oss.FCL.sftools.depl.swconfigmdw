.. _validation-plugin-howto-example-plugin:

Example ConfML validation plug-in
=================================

The example plug-in implements a simple ConfML validator class, and so demostrates
how ConfML validation can be extended by plug-ins.

The extra validation in this case is as follows: we have a requirement that if
a string-type ConfML setting's reference starts with ``FOO_``, its value
should also contain the string ``foo``. For example, consider the following
file:

.. code-block :: xml
    :linenos:
    
    <?xml version="1.0" encoding="UTF-8"?>
    <configuration xmlns="http://www.s60.com/xml/confml/1" name="ExampleValidatorTest">
        <feature ref="ExampleValidatorTest" name="Settings for example validator testing">
            <setting ref="SomeSetting" name="Some setting" type="string"/>
            <setting ref="FOO_SomeSetting1" name="FOO - Some setting 1" type="string"/>
            <setting ref="FOO_SomeSetting2" name="FOO - Some setting 2" type="string"/>
        </feature>
        <data>
            <ExampleValidatorTest>
                <SomeSetting>foo bar</SomeSetting>
                <FOO_SomeSetting1>abc foo</FOO_SomeSetting1>
                <FOO_SomeSetting2>abc123</FOO_SomeSetting2>
            </ExampleValidatorTest>
        </data>
    </configuration>

Here two settings are prefixed with ``FOO_``, but only one of them has ``foo``
in its value, thus our custom validator should report a warning for the value
on line 12.

Directory structure
-------------------

- ``plugins/`` - Root directory for all ConE plug-in sources
    - ``example/`` - Example plug-in package directory
        - ``ConeExampleValidatorPlugin/`` - Source for the example validator plug-in
            - ``examplevalidatorplugin/`` - Module directory containing all plug-in code
                - ``tests/`` - Unit tests and test data for the plug-in
                    - ``testdata/`` - Directory containing all test data needed by the test cases
                    - ``__init__.py`` - Test module initialization file
                    - ``runtests.py`` - Script for running all test cases
                    - ``unittest_validation.py`` - File containing test cases
                - ``__init__.py`` - Plug-in module initialization file
                - ``validators.py`` - Plug-in source file
            - ``setup.py`` - Setup script for packaging the plug-in into an .egg file
            - ``setup.cfg`` - Configuration file for ``setup.py``

Plug-in code
------------

validators.py
.............

This file defines the validator class. The validator simply goes through all
``ConfmlStringSetting`` instances in the configuration and checks their values.

.. literalinclude:: /../source/plugins/example/ConeExampleValidatorPlugin/examplevalidatorplugin/validators.py
   :linenos:


unittest_validation.py
......................

The tests for the plug-in simply contain one test case that tests the validator
with the example ConfML file shown earlier, using the ``assert_problem_list_equals_expected()``
method provided by the ``testautomation`` module.

.. literalinclude:: /../source/plugins/example/ConeExampleValidatorPlugin/examplevalidatorplugin/tests/unittest_validation.py
   :linenos:


Plug-in packaging
-----------------

The file ``setup.py`` handles the packaging of the plug-in into an egg file.

The most important thing here is the plug-in's entry point info. The list
of validator classes provided by the plug-in must be specified as an entry
point. The entry point group in this case is ``cone.plugins.confmlvalidators``.

.. literalinclude:: /../source/plugins/example/ConeExampleValidatorPlugin/setup.py
   :linenos:
