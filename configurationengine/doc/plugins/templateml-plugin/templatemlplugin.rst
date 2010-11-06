User guide for Template Configuration File Markup Language (TemplateML) Plugin
------------------------------------------------------------------------------

Introduction
'''''''''''''
This page describes how to use and configure Template Configuration File Markup Language 
(TemplateML) plugin fo ConE. TemplateML is one of the implementation mapping languages for
Configuration Markup Language (ConfML). This plugin is used to generate arbitrary text file
formats. It doesn't have a specific extension or encoding. Currently 
this language uses `Jinja 2 template engine <http://jinja.pocoo.org/2/>`_ to generate 
output files.

Templates are based on Jinja syntax and semantics that are described in detail `Jinja 2 Template Designer Documentation <http://jinja.pocoo.org/2/documentation/templates>`_
One important concept in Jinja is `template inheritance <http://jinja.pocoo.org/2/documentation/templates#template-inheritance>`_, which means that you can overwrite only specific blocks within a template, customizing it while also keeping the changes at a minimum.

Templateml plugin supports also `XML Inclusions (XInclude) <http://www.w3.org/TR/xinclude/>`_ 
that allows a mechanism for merging XML documents. By writing inclusion tags in a "main" 
document it automatically includes other documents.

TemplateML files are executed by default in **normal** :ref:`invocation phase <implml-common-invocation-phase>`.

Template Configuration File ML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The TemplateML syntax is a extension of Configuration markup language (confml). The term in confml for this extension 
is implementation method language (implml), which in TemplateML case is a xml file. 

All input values, excluding template and filter elements text content, can be given as ConfML refs.

  * Namespace: ``http://www.s60.com/xml/templateml/1``
  * File extension: ``templateml``

.. note::

   More information about :ref:`file extensions <implml-file-extensions>`. 

TemplateML Elements
...................

The TemplateML model is drawn out as a uml model in below picture.

  .. image:: templateml.jpg

.. note::

   TemplateML supports also common ImplML elements. More information about :ref:`ImplML elements <implml-common-elements>`. 


templateml element
**************************

The root element of the templateml file is always templateml, which defines the xml namespace (xmlns) 
to http://www.s60.com/xml/templateml/1 in the current version. 

**templateml example**:

.. code-block:: xml

  <templateml xmlns="http://www.s60.com/xml/templateml/1">

desc element
**************************

Description element's content is not used in output file generation, but it can be used to describe temlplateml file.

**desc example**:

.. code-block:: xml

  <desc>Description field text</desc>

output element
**************************

Output element describes how one output file is generated. Output has one mandatory attribute 'file' that defines filename for output file. If you want to generate output file to some other than default folder, it can be done by defining a output directory to 'dir' attribute. Default encoding for output file is 'UTF-8', if some other encoding is wanted, it can be defined by 'encoding' attribute.  This encoding should be one of the standard Python codecs encoding (see http://docs.python.org/library/codecs.html#standard-encodings). By 'newline' attribute the output file's newline characters can be defined. The default value is 'unix' that use LF (Line feed, '\n', 0x0A) in output file. LF is used Unix-like systems and web applications. If output file has to use CR (Carriage Return) followed by LF (CR+LF, '\r\n', 0x0D 0x0A) as newline characters, 'newline' attribute should have value 'win'. CR+LF is used in non-Unix systems like DOS, Windows and Symbian OS.

Template element is mandatory child element for output element. One output element can have only one template element.
Output element can also contain optional filter and filters elements that are specific just for this output file. Global filters that are common for all output files should be defined under root templateml element. 

**output example**:

.. code-block:: xml

  <output file="my_output.txt" encoding="UTF-8" dir="output" newline="win">
    <template>Hello world!</template>
    <filter name="filter1">lambda a,b: a+b</filter>
    <filter name="filter2">lambda a,b: a*b</filter>
    <filters>
    def filter3(a,b):
      return a-b
    </filters>
  </output>

For unicode transformation formats, control over the BOM is provided by the attribute ``bom``.
This attribute defines whether the BOM is written to the output or not. If the attribute is not
defined, the default behavior of the encoding is used (i.e. BOM is written for UTF-16, but not for UTF-16-BE,
UTF-16-BE or UTF-8). For encodings where the BOM makes no sense (e.g. ASCII), the attribute does nothing.

**Examples**:

.. code-block:: xml

    <output file="test.txt" encoding="UTF-8" bom="true">
        <template>test</template>
    <output>
    
    <output file="test.txt" encoding="UTF-8" bom="false">
        <template>test</template>
    <output>

template element
****************

Template can be defined in template element or in external file. If both are defined file attribute overwrites. 

**template example 1:**:

.. code-block:: xml

  <template>Some Jinja template goes here</template>

Notice that if you want to define create xml output files and you don't want to encode special characters you can use CDATA section http://www.w3schools.com/xmL/xml_cdata.asp. 

.. code-block:: xml
  
  <template>
  <![CDATA[
  <xml name="xml temp">Some Jinja xml template</xml>
  ]]>
  </template>
  
**template example 2:**:

.. code-block:: xml

  <template file="../../templates/template.txt"/>
  <template file="${feat1.tempfile_setting}"/>

With template's file attribute template is defined relatively to templateml file. 

filter element
**************************

With filter element you can define custom filters. Custom filters are Python lambda functions that take the left side of the filter as first argument and the the arguments passed to the filter as extra arguments or keyword arguments. Filter element has mandatory 'name' attribute that defines the name of the filter. Name is used in template to refer to that filter. Filter can be defined in filter element or in external file. If both are defined file attribute overwrites. 

`Jinja has built-in filters <http://jinja.pocoo.org/2/documentation/templates#builtin-filters>`_ (e.g. capitalize, replace, trim, urlize, format, escape) that can be utilized without any extra definitions templateml file.

**filter example**:

.. code-block:: xml

  <filter name="minus">lambda a,b: a-b</filter>

With filter's file attribute filter is defined relatively to templateml file. 

filters element
**************************

With filters element you can also define custom filters. These can be any Python functions that take the left side of the filter as first argument and the the arguments passed to the filter as extra arguments or keyword arguments. Function name is used to refer to the filter. Filters can be defined in filters element or in external file. If both are defined file attribute overwrites. 

**filters example**:

.. code-block:: xml

  <filters>
  def sum(a,b):
    return a+b  
  </filters>

With filters's file attribute filter is defined relatively to templateml file. 

Variables
+++++++++

The TemplateML plugin passes variables to the templates you can mess around in the template. Every feature has 
following attributes:

 * _name
 * _namespace
 * _value
 * _fqr 
 * _type

Currently TempleML plugin passes features in three different structure: feat_tree, feat_list and configuration.
 
feat_tree
+++++++++

Variable 'feat_tree' contains features in a tree structure. It allows easy access to features attributes, 
when feature explicitly known: 

.. literalinclude:: templateml_example2.txt
   :language: xml

feat_list
++++++++++++++++++++++++++

Variable 'feat_tree' contains features in an array and allows easy access to all features e.g. in loops:

.. literalinclude:: templateml_example1.txt
   :language: xml

Generates to output file e.g following content:

.. literalinclude:: templateml_example1_result.txt
   :language: xml

configuration
++++++++++++++++++++++

Configuration object that is defined ConE API can be accessed also inside template.

.. code-block:: xml

    <template>Configuration name: {{ configuration.get_path() }}
    {% for feature in configuration.get_default_view().get_features('**') %}
    {{ feature.fqr }}
    {% endfor %}
    </template>


Examples
'''''''''

An example of templateml file, that generates three output files, utilizes XInclude and defines a number of custom filters:

.. literalinclude:: templateml_example0.txt
   :language: xml


FAQ
'''''''''
This will be updated based on the questions.


