User guide for Convert Project Plugin
-------------------------------------

Introduction
'''''''''''''
This page describes how to use and configure Convert Project plugin. This plugin is 
used to convert old style configuration structure to Configuration project. The plugin 
can be used to create files and folders. For a folder you can define using absolute paths
or wildcards which files from previous structure are copied to the new structure. For files
it is possible just to copy a file from one location to another, create layer and configuration
root files. For these more complex type of files you can select which files are included using
absolute path or wildcards.


Configuring
''''''''''''
Plugin is configured by modifying .convertprojectml file that must be located in some layer's implml folder
that is included in generated configuration. Typical case is that the plugin is used in products that don't
have configuration project and layers. In that case refer to Installation/Running part.

Convert Project ML format
~~~~~~~~~~~~~~~~~~~~~~~~~~
+------------------+-----------------+----------------+-------------------------------+
| Elements         | Attributes      | Content model  | Description                   |
+==================+=================+================+===============================+
| convertprojectml | xmlns           |targetProject   | Collective/Top-most element   |
|                  |                 |layer*          | defines the namespace used    |
|                  |                 |foreach*        | in the file.                  |
+------------------+-----------------+----------------+-------------------------------+
| targetProject    | path            |                | Defines output path. By the   |
|                  | validate        |                | default all the paths later   |
|                  |                 |                | are relative to this path.    |
+------------------+-----------------+----------------+-------------------------------+
| layer            | path            | folder*        | Defines one configuration     |
|                  |                 | file*          | layer. Creates new layer      |
|                  |                 |                | folder defined in the path.   |
|                  |                 |                | Folder and file paths are     |
|                  |                 |                | relative to this path.        |    
+------------------+-----------------+----------------+-------------------------------+
| folder           | path            | filter*        | Defines one folder inside a   |
|                  |                 |                | layer. Creates new folder     |
|                  |                 |                | using path. Filter paths are  |
|                  |                 |                | relative to this path.        |
+------------------+-----------------+----------------+-------------------------------+
| file             | path            | filter*        | Element which can be used     |
|                  | type            |                | for three different purposes. |
|                  |                 |                | Copying files, creating layer |
|                  |                 |                | roots and configuration roots.| 
|                  |                 |                | Path defines target filename  |
|                  |                 |                | and type which kind of file   |
|                  |                 |                | is created.                   |
+------------------+-----------------+----------------+-------------------------------+
| filter           | action          |                | Filter is the element that    |
|                  | data            |                | does all the work. It has     |
|                  | remove_includes |                | attribute action, which can be|
|                  |                 |                | add, remove, include_file or  |
|                  |                 |                | include_layer. Data defines   |
|                  |                 |                | the search pattern for action | 
|                  |                 |                | Remove_includes can be used to|
|                  |                 |                | remove all existing includes  |
|                  |                 |                | from files that are included  |
|                  |                 |                | in layer root file.           |
+------------------+-----------------+----------------+-------------------------------+


Installation/Running
'''''''''''''''''''''
1. Download and install ConE according the ConE installation documentation.
2. Go to \\epoc32\\rom\\config folder
3. Create convertproject and convertproject\\implml folders
4. Copy example create_project.convertprojectml to convertproject\\implml folder
5. Modify according your needs
6. Create a layer root file called root.confml in convertproject folder. Use the following content:

.. code-block:: xml

  <?xml version="1.0" encoding="ASCII"?>
  <confml:configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:confml="http://www.s60.com/xml/confml/2" 
    xmlns:xi="http://www.w3.org/2001/XInclude" 
    xsi:schemaLocation="http://www.s60.com/xml/confml/2 http://www.s60.com/xml/confml/1#//confml2 http://www.w3.org/2001/XInclude http://www.s60.com/xml/confml/1#//include">
  </confml:configuration>

7. Create configuration root file called convert.confml in \epoc32\rom\config folder. Use the following content:

.. code-block:: xml

  <?xml version="1.0" encoding="ASCII"?>
  <confml:configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:confml="http://www.s60.com/xml/confml/2" 
    xmlns:xi="http://www.w3.org/2001/XInclude" 
    xsi:schemaLocation="http://www.s60.com/xml/confml/2 http://www.s60.com/xml/confml/1#//confml2 http://www.w3.org/2001/XInclude http://www.s60.com/xml/confml/1#//include">
  	<xi:include href="convertproject/root.confml"/>
  </confml:configuration>

8. Run ConE to generate content. 

::

  \epoc32\rom\config>cone --action generate -c convert.confml


Examples
'''''''''

XSD
'''

Download: :download:`projectml.xsd </xsd/projectml.xsd>`


FAQ
'''''''''
This will be updated based on the questions.





