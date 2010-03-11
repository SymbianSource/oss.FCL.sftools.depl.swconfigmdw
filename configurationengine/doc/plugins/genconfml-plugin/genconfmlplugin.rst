User guide for Generic Configuration File Markup Language (GenConfML) Plugin
----------------------------------------------------------------------------

Introduction
'''''''''''''
This page describes how to use and configure Generic Configuration File Markup Language 
(GenConfML) plugin fo ConE. GenConfML is one of the implementation mapping languages for
Configuration Markup Language (ConfML). This plugin is used to generate arbitrary text file
formats. Currently this language uses a `eXtensible Stylesheet Language Transformations 
(XSLT) <http://www.w3.org/TR/xslt>`_ style sheet for generating a file for selected settings. 
Support for other style sheet or transformation mechanisms than 
`XSLT <http://www.w3.org/TR/xslt>`_ could be added later.

GenConfML files are executed by default in **normal** :ref:`invocation phase <implml-common-invocation-phase>`.

GenConfML
'''''''''

The GenConfML (Generic Configuration File ML) syntax is a extension of Configuration markup 
language (confml). The term in confml for this extension is implementation method language 
(implml), which in GenConfML case is a xml file. 

  * Namespace: ``http://www.s60.com/xml/genconfml/1``
  * File extension: ``gcfml``

.. note::

   More information about :ref:`file extensions <implml-file-extensions>`. 

GenConfML Elements
..................

The GenConfML model is drawn out as a uml model in below picture.

  .. image:: gcfml.jpg

.. note::

   GenConfML supports also common ImplML elements. More information about :ref:`ImplML elements <implml-common-elements>` . 

<file> Element
**************

The ``file`` element is the root element of the configuration, and acts as a container to the rest of the elements. Each 
generated file must be defined in its own Generic Configuration File XML file.  The input file for XSLT processor is 
the Configuration ML file including only the data element containing values for all selected settings. Following XSLT 
output types are supported: XML, HTML, and text.  

Attributes
++++++++++

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
name                  Yes                     Defines a name of the output file. Can contain path that is used to create 
                                              subfolders under output directory.
target                No                      Defines a Symbian specific attribute for additional path information. Final 
                                              target path is a combination of target and name. The combined path is used in 
                                              output directory and in IBY file. If target attribute is not supported full 
                                              path can be defined also as a value of name attribute.
====================  ======================  ===============================================================================


Child Elements
++++++++++++++

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
setting               0 .. *                  Defines a configuration setting reference that is used as an input in  XSLT
                                              prosessing.
xsl:stylesheet        1                       Defines stylesheet for XSLT processor. 
====================  ======================  ===============================================================================

Example
+++++++

.. code-block:: xml

    <file xmlns="http://www.s60.com/xml/genconfml/1" name="myname.txt" target="">
     ...
    </file>


<setting> Element
*****************

Setting element is mandatory element containing the settings used in this transformation.


Attributes
++++++++++

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
ref                   Yes                     Defines a Feature/setting reference pair. All settings inside one feature 
                                              can be selected by using Feature/*.
====================  ======================  ===============================================================================

Example
+++++++

.. code-block:: xml

    <setting ref="MyFeature/Setting1"/> 
    

<xsl:stylesheet> Element
************************

Xsl:stylesheet element defines the XSLT [3] stylesheet used to transform input data from ConfML to output file.

The style sheet can be defined inside file element or in external file identified using stylesheet attribute.
If style sheet is completely omitted then input file is to be used as such as the configuration file without any transformation.
The MIME type for XML files of Generic Configuration File ML is ``text/application+xml``. 


Full example files
''''''''''''''''''

Example Generic Configuration File ML file:

.. literalinclude:: genconfml_example1.txt
   :language: xml

Example file that is passed to the included XSLT processor contains only selected data elements:

.. literalinclude:: genconfml_example2.txt
   :language: xml
   
Example output file that is generated by XSLT processor:

.. literalinclude:: genconfml_example3.txt
   :language: xml

The output file will be located under the output folder in a sub-folder determined based on the
name and target attributes of the file element. E.g., in this case the output file's path is
``output_dir/private/2000BEE5/CamcorderData.xml``.

Notice that same result is obtained by having the following line in the GenConfML file:

.. literalinclude:: genconfml_example5.txt
   :language: xml

XSD
'''''''''

Download: :download:`gcfml.xsd </xsd/gcfml.xsd>`


FAQ
'''''''''

This will be updated based on the questions.

