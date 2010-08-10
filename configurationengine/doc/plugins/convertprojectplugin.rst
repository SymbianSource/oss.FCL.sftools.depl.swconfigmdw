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

Defining layer
'''''''''
.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <convertprojectml xmlns="http://www.s60.com/xml/convertprojectml/1">		
    <targetProject path=""/>
    <layer path="assets/s60">
      <folder path="implml">
        <filter action="add" data="assets/s60/confml/*.crml"/>
        <filter action="add" data="assets/s60/confml/*.gcfml"/>
      </folder>
      <file type="layer_root" path="root.confml">
        <filter action="include_file" data="confml/*.confml"/>
      </file>
      <file type="configuration_root" path="s60_root.confml">
        <filter action="include_layer" data="assets/s60/root.confml"/>
      </file>	
    </layer>
  </convertprojectml>
  
Normally targetProject's **path** attribute is defined as empty. It means that the project is generated to ConE's normal output location which can be given as command line parameter (-o). 

Convert project ML is constructed so that the highest data structure is **layer**. Layer has attribute **path**, which defines relative location to output path. Layer can contain one or more 
**folders** and/or **files**. 

Folder defines folder entry inside the layer and in file system level is a directory. Folder has **path** attribute which is relative to layer's path. Folder can contain **filters** which define 
how folder's content is constructed. With action **add** data is copied to the folder from location which is defined in **data** attribute. 
**Note** that the path in data attribute is relative to configuration project's root (normally \epoc32\rom\config). Example here copies  all crml and gcfml files from confml folder to impml folder.

Layer can also define files. Each file has **type** which can be layer_root or configuration_root. The former one is creating layer root file to the path defined in **path** attribute, location is 
relative to layers location. Action **include_file** defines a search pattern. In the example all files from layer's confml folder with extension confml are included in the layer's root file. This can
be used to generate layer root files automatically in the build even when the exact content in filename level is not known. Configuration root files are always generated to the root of the 
configuration project. Filter action **include_layer** defines configuration layer root files which are included to the configuration root.


Defining metadata and configuration name
'''''''''
.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <convertprojectml xmlns="http://www.s60.com/xml/convertprojectml/1">		
    <targetProject path=""/>
    <layer path="assets/s60">
      <file type="configuration_root" path="s60_root.confml" configuration_name="My S60 Config">
        <meta xmlns:cv="http://www.nokia.com/xml/cpf-id/1">
          <version>001</version>
          <cv:configuration-property name="sw_version" value="${convertproject.versioninfo}" />
        </meta>
        </file>	
    </layer>
  </convertprojectml>

File element's **configuration_name** attribute can be used to override ConE's default configuration name. Value is written to ConfML file's configuration element to name attribute. **Meta** 
structure defines ConfML metadata which is added to configuration root file. It supports normal ConfML metadata like in this example **version** and cv namespace metadata like **sw_version**. 
Value of sw_version is fetched from ConfML setting **convertproject.versioninfo** at run time. Configuration_name and metadata are available to both layer and configuration root files.

Creating loops
'''''''''
.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <convertprojectml xmlns="http://www.s60.com/xml/convertprojectml/1">		
    <targetProject path=""/>
    <foreach variable="{TEMPLATE}" data="/epoc32/rom/config/language_packs">	
      <layer path = language_packs/{TEMPLATE}">
        <file type="layer_root" path="root.confml">
          <filter action="include_file" data="confml/*.confml" remove_includes="true"/>
        </file>
        <file type="configuration_root" path="langpack_{TEMPLATE}_root.confml" configuration_name=" {TEMPLATE}">
          <filter action="include_layer" data="assets/s60/root.confml"/>
          <filter action="include_layer" data="assets/symbianos/root.confml"/>
          <filter action="include_layer" data="language_packs/{TEMPLATE}/root.confml"/>
        </file>
	  </layer>
  </foreach>
  </convertprojectml>

Loops can be defined in convert project ml using **foreach** structures. Attribute **data** defines path where from all the folder names  are scanned. Value of attribute **variable** is the 
name of the folder e.g. if /epoc32/rom/config/language_packs contains folders *lp1*,* lp2* and *lp3* then variable has value lp1 in the first round,  lp2 in the second round and lp3 in the third round. 
Meaning that in the first round layer path will be language_packs/lp1 and configuration root file name is langpack_lp1_root.confml, which includes language_packs/lp1/root.confml as the last layer root. 

Extending configuration root information
'''''''''
.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <convertprojectml xmlns="http://www.s60.com/xml/convertprojectml/1">		
    <targetProject path=""/>
    <foreach variable="{TEMPLATE}" data="/epoc32/rom/config/language_packs">	
      <layer path = language_packs/{TEMPLATE}">
        <file type="layer_root" path="root.confml">
          <filter action="include_file" data="confml/*.confml" remove_includes="true"/>
        </file>
        <file type="configuration_root" path="langpack_{TEMPLATE}_root.confml" configuration_name=" {TEMPLATE}">
          <filter action="include_layer" data="assets/s60/root.confml"/>
          <filter action="include_layer" data="assets/symbianos/root.confml"/>
          <filter action="include_layer" data="language_packs/{TEMPLATE}/root.confml"/>
        </file>
	  </layer>
    <layer path="">		
        <file type="configuration_root" path="langpack_lp1_root.confml">
          <meta xmlns:cv="http://www.nokia.com/xml/cpf-id/1">
            <cv:configuration-property name="based_on_ctr" value="abc123" />
          </meta>
        </file>
    </layer>
  </convertprojectml>

The first part is exactly same as above. What has been added is a new layer which includes only one file generated in the example above. Example here adds extra metadata *'based_on_ctr** to
the configuration root langpack_lp1_root.confml. Note that convert project ml works so that if there is no existing file then that is created in case file exists then it is updated. 


XSD
'''

Download: :download:`projectml.xsd </xsd/projectml.xsd>`


FAQ
'''''''''
This will be updated based on the questions.





