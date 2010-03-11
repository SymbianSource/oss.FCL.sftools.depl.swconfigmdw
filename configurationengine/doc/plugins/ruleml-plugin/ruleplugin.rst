User guide for Rule Plugin usage in ConE
----------------------------------------

Introduction
'''''''''''''
This page describes how to use ConE Rule plugin. With rule plugin one may set rule configuration 
for the values in the confml. So for ex. one may have a case where is one confml value is been setted
and one may create a rule configuration that if this value is for ex. 'foo' then some other value is
'bar'. Value may be required or configures. 


Creating a rule configuration file
''''''''''''''''''''''''''''''''''
Create a new file a example.ruleml and set it's file encoding to UTF-8.
Place the file in the impml folder in configuration project.
The file is a XML base file. 
First set the encoding tag 

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>* 

and then create a root tag

.. code-block:: xml

  <ruleml xmlns="http://www.s60.com/xml/ruleml/1">*
 
give a set of rules for ex. 
 
.. code-block:: xml

  <rule>mms.imagesize == 'large' configures pd.ref1 = True and pd.ref2 = True</rule>*
 
and close the ruleml tag.

One may say use several boolean operators for the configuration rule like for ex.
 
.. code-block:: xml

  and, or, ==, !=* 
 
Like for ex.

.. code-block:: xml

  <rule>mms.imagesize == 'large' configures pd.ref1 = True and pd.ref2 = True</rule>*
 
means that if reference link mms/imagesize  in some confml file is set to large then reference 
link pd/ref1 value is true and pd/ref2 value is set to true also.

**All in all one may create a dependency like project configuration with ruleml files.**  

Ruleml version 2 adds support for calling `Python <http://www.python.org/doc/2.5/>`_ expressions from rules. Python expression are defined between ``{%`` and ``%}``:

.. code-block:: xml

  <rule>feat1.setting2 == True configures feat2.setting2 = {% ${feat3.setting2} %}</rule>

Expression return a result, that can be used in rule e.g. to set a value to some setting in configuration. These expression can be used to create more complex logic into rules that is not possible with standard rule expressions. Inside eval expressions features and feature's values can be accessed by following syntax:

Accesses to the value::

  ${Feature.Setting}

Accesses to the feature object::

  @{Feature.Setting}

Python functions or constants that can be accessed inside expressions can be defined by ``<eval_globals>`` elements:

.. code-block:: xml

  <eval_globals>
  def my_function1(attribute):
      return attribute + 1
  </eval_globals>
  
  <eval_globals>CONST_1 = "my constant"</eval_globals>
  
  <eval_globals file=".scripts/evals_in_file.py"/>
  
Definitions can be inside <eval_globals> elements or definitions can be in separate file referenced with ``file`` attribute.
The path specified in this attribute is relative to the RuleML implementation file. So, for example, if your implementation
file's location is ``some/layer/implml/my_rules.ruleml``, the actual path specified in the above example would be
``some/layer/implml/.scripts/evals_in_file.py``. It is recommended to place the scripts under a directory beginning
with a dot, so that the plug-in loader does not attempt to load the .py file as an implementation (files and directories beginning
with a dot are ignored in the implementation loading phase).

Running
'''''''''''''''''''''

::

  cone generate -p someproject.cpf -o c:/temp/coneoutput -i rulemlfile.ruleml

Generates files out of configuration file and takes the implementation rulemlfile.ruleml in concern,
and the output is to been set to -o given folder 

for more example see the cone documentation

Examples
'''''''''


**Ruleml version 1 file example**

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <ruleml xmlns="http://www.s60.com/xml/ruleml/1">
  <rule>imaker.imagetarget configures imakerapi.outputLocation = imaker.imagetarget</rule>
  <rule>mms.imagesize == 'large' configures pd.ref1 = True and pd.ref2 = True</rule>
  <rule>mms.imagesize == 'small' configures pd.ref1 = False and pd.ref2 = True</rule>
  <rule>mms.imagesize == 'extrasmall' configures pd.ref1 = False and pd.ref2 = False</rule>
  <rule>mms.imagesize == 'extralarge' configures pd.ref1 = True and pd.ref2 = False</rule>
  </ruleml>

**What do the example ruleml file means**

The example file set the values upon the image size. First it sets the iMaker output
location target and then it starts to set the mms message image size settings. So if for ex.
*mms/imagesize* refence link value in confml file is set to *extralarge* then the value of
*pd/ref1* is set to *true* and the value *pd/ref2* is set to false.


**Ruleml version 2 file example**

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <ruleml xmlns="http://www.s60.com/xml/ruleml/2">
  <rule>feat1.setting1 == 'somevalue' configures feat2.setting1 = {% len( ${feat3.setting1} ) %}</rule>
  <rule>feat1.setting2 == True configures feat2.setting2 = {% my_function1( ${feat3.setting2} ) %}</rule>
  <rule>feat1.setting3 == True configures feat2.setting3 = {% CONST_1 %}</rule>
  <rule>{% my_function2( ${feat1.setting4} ) %} configures feat2.setting4 = False</rule>
  <rule>{% @{feat1.setting5}.get_type() %} == 'int' configures feat2.setting5 = 'integer'</rule>
  <rule>feat1.setting6 == True configures feat2.setting6 = {% '0x%08X' % ${feat2.setting6} %}</rule>
  <eval_globals>
  def my_function1(attribute):
      return attribute + 1
  def my_function2(attribute):
      if attribute == 'abc':
          return True
      else:
          return False
  </eval_globals>
  <eval_globals>
  CONST_1 = "my constant"
  </eval_globals>
  <eval_globals file=".scripts/evals_in_file.py"/>
  </ruleml>

XSD
'''''''''

Ruleml version 1: :download:`ruleml.xsd </xsd/ruleml.xsd>`

Ruleml version 2: :download:`ruleml2.xsd </xsd/ruleml2.xsd>`

FAQ
'''''''''
This will be updated based on the questions.
