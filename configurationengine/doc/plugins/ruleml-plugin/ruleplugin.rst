User guide for Rule Plugin usage in ConE
========================================

.. note::
    RuleML v3 is now the officially supported RuleML version.
    Support for versions 1 and 2 is still present in ConE, but they will not
    be maintained anymore. If you have e.g. a RuleML v2 file and require some
    new functionality, the new functionality will be added to RuleML v3 and
    you will need to update your RuleML file to use version 3.
    
    Updating should be easy, since the biggest change is setting reference
    syntax. Simply add ``${}`` around all setting references in the rules.

Introduction
------------
This page describes how to use the ConE Rule plugin. The plug-in provides
support for RuleML files, which can be used to execute rules during output
generation. The main use for RuleML is modifying the values of ConfML settings
on run-time based on the values of other settings.

The rule plug-in registers the ImplML namespace for defining rules, and the
RuleML-specific file extension:

  * Namespace: ``http://www.s60.com/xml/ruleml/3``
  * File extension: ``ruleml``

.. note::

   More information about :ref:`file extensions <implml-file-extensions>`. 

Usage
-----

A RuleML file is simply an XML file that defines a set of rules. For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>${SomeFeature.SomeSetting} == 'testing' configures ${SomeFeature.SomeOtherSetting} = 5</rule>
        <rule>${SomeFeature.SomeSetting} == 'xyz' configures ${SomeFeature.SomeOtherSetting} = 6</rule>
    </ruleml>

The above example sets the value of the setting ``SomeFeature.SomeOtherSetting``
to the integer value ``5`` or ``6`` if the value of ``SomeFeature.SomeSetting`` is
one of the strings ``testing`` or ``xyz``.

Rules can also contain multiple operations in a single rule, and can span
multiple lines to make the rule more readable. For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            ${SomeFeature.SomeSetting} == 'testing' configures
                ${SomeFeature.SomeOtherSetting} = 5 and
                ${SomeFeature.SomeOtherSetting2} = 6 and
                ${SomeFeature.SomeOtherSetting3} = 7
        </rule>
    </ruleml>

Sometimes the case is that the rule should be executed always, regardless of
the values of any other settings. To do this you can simply specify ``True``
as the left-hand side expression:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>True configures ${SomeFeature.SomeOtherSetting} = 'Hello!'</rule>
    </ruleml>

Python expressions in rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^

RuleML has an extension to the basic rule syntax, which allows any `Python <http://www.python.org/doc/2.5/>`_
expressions to be used. These can be used to create more complex logic into
rules than is possible with standard rule expressions. The Python expressions
are defined between ``{%`` and ``%}``, and can be used in place of normal
value expressions.

You can access global ruleml namespace, from which you can find Configuration and Generation Context of the active execution.

 * ruleml.configuration - links to `Configuration <../../../docbuild/epydoc/cone.public.api.Configuration-class.html>`_ object.
 * ruleml.context - links to `Generation Context <../../../docbuild/epydoc/cone.public.plugin.GenerationContext-class.html>`_ object.
 

*Examples of using Python scripts inside ruleml files:*

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.SomeOtherSetting} = {% 2 ** 16 %}
        </rule>
    </ruleml>

This sets the value of ``SomeFeature.SomeOtherSetting`` to the evaluated value
of the Python expression ``2 ** 16``, which is 65536.

Obviously, simple expressions like this cannot do much, but an expression can
also be a function call, and functions can do almost anything. Functions (and 
also any other globals) can be specified using ``<eval_globals>`` elements.
For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.SomeOtherSetting} = {% power(2, 16) %}
        </rule>
        <eval_globals>
    def power(x, y):
        result = 1
        for i in xrange(y):
            result *= x
        return result
        </eval_globals>
    </ruleml>

This does the same thing as the previous example, except that it uses a custom
function to do it.

It is also possible to use standard Python libraries or the
`ConE API <../../epydoc/index.html>`_ from ``<eval_globals>``, and also
some RuleML-specific things. Ruleml has all data from 
Configuration and Generation Context classes of the active execution. For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.SomeOtherSetting} = {% power(2, 16) %}
        </rule>
        <eval_globals>
    # Import the standard library urllib2 to do operations on URLs
    import urllib2
    
    # Import the ConE API
    from cone.public import api
    
    def get_project_path():
        # The current configuration is available in ruleml.configuration
        config = ruleml.configuration
        
        # Return the path of the storage the current project is in
        project = config.get_project()
        return project.storage.get_path()
        </eval_globals>
    </ruleml>
    

In this example configuration is got from ruleml. Generation Context can be 
accessed in the same way, ruleml.context will have all data stored in the 
Generation Context object.

Generation Context values can be accessed inside the Python expressions using the
ruleml.context like ruleml.context.output.

This example uses the Generation Context to get defined output folder. 
See how to access the data from the code example below.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.output} = {% get_output_folder() %}
        </rule>
        <eval_globals>
          
    def get_output_folder():
        output = ruleml.context.output
        return output
        </eval_globals>
    </ruleml>


Accessing ConfML values inside Python expressions
'''''''''''''''''''''''''''''''''''''''''''''''''

ConfML setting values can be accessed inside the Python expressions using the
same notation as elsewhere in the rules, i.e. using ``${`` and ``}``.
For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            ${SomeFeature.SomeSetting} == 'testing' configures ${SomeFeature.SomeOtherSetting} = {% ${SomeFeature.SomeSetting}.upper() %}
        </rule>
    </ruleml>

This sets the value of ``SomeFeature.SomeOtherSetting`` to 'TESTING'.

Accessing feature objects inside Python expressions
'''''''''''''''''''''''''''''''''''''''''''''''''''

Sometimes it is necessary to access the actual feature (or setting) object that
ConE uses internally to perform more complex operations. This can be done
similarly to accessing the setting values, the only difference is that the
setting reference needs to be surrounded by ``@{}``. For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.SomeOtherSetting} = {% get_location(@{SomeFeature.SomeSetting}) %}
        </rule>
        <eval_globals>
    from cone.public import api
    
    def get_location(setting):
        parent_config = setting._find_parent(type=api.Configuration)
        return parent_config.get_path()
        </eval_globals>
    </ruleml>

This example uses the ConE API to find the location (ConfML file) where the
given setting is defined.


Defining functions in a separate .py file
'''''''''''''''''''''''''''''''''''''''''

Defining the Python functions used in the rules in an ``<eval_globals>`` element
can quickly become unwieldy for larger functions:

- Things like ``<`` need to escaped using the corresponding XML entity references
- Syntax highlighting is not available
- Writing and running unit tests for the functions is not possible

For these reasons, the code of an ``<eval_globals>`` element can also be
specified in a separate Python file using the ``file`` attribute. For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ruleml xmlns="http://www.s60.com/xml/ruleml/3">
        <rule>
            True configures ${SomeFeature.SomeOtherSetting} = {% some_very_complex_operation(
                @{SomeFeature.SomeSetting1},
                ${SomeFeature.SomeSetting2},
                ${SomeFeature.SomeSetting3}) %}
        </rule>
        <eval_globals file="scripts/complex_function.py"/>
    </ruleml>

The path specified in the ``file`` attribute is relative to the implementation
file where the rule is specified, so if the RuleML file in this example was
located in ``assets/example/implml/some_rule.ruleml``, the referenced Python
file would be ``assets/example/implml/scripts/complex_function.py``.

FAQ
---
This will be updated based on any questions.
