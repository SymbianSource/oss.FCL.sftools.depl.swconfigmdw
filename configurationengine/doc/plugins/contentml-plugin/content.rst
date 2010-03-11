How to use the ConE Content plugin
==================================

Introduction
'''''''''''''
The basic concept of Content plugin is to transfer file resources from
one place to another. So one may have for example; an audio file stored in the
configuration project and needs to define the audio file location in the
device. With ConE Content plugin you can basically define a copy operation. 
You just create <somename>.content (or general *.implml file) type file to the configuration project implml folder 
and set the rules or filters in there.    


content elements
----------------
The content model is drawn out as a uml model in below picture.

  .. image:: content2.jpg

content
^^^^^^^
The root element of the content file is always content, which defines the xml namespace (xmlns) 
to http://www.s60.com/xml/content/2 in the current version. 

**content example**::

  <content xmlns="http://www.s60.com/xml/content/2"/>

tag
^^^^

Implementation tag elements can be defined under the root element. See the page on `tags <tags.html>`_ for more info.

output
^^^^^^
The output element can define a output folder where content is copied from :ref:`content-input` elements that 
are children of this particular output. There can be several output elements inside a single content 
file or block.

**output example**::

  <output dir="foobar"/>

The above statement defines that content is copied under foobar folder in the cone output folder.


.. _content-input:

input
^^^^^^
The user can define input under the output element. The input element can define a source directory and two file filters for 
that directory (include and exclude filters). The input element will always search files under the content directories of the 
configuration project. But the content of the search directory is a layered content of all configuration project content directories 
(See content layering in Configuration project specification (TODO: add link here)).

**input example**::

  <input dir="foobar"/>

the above statement would include all files found under foobar directory.::

  <input file="foobar/file1.txt"/>

the above statement would include file1.txt from folder foobar to the copy operation.

include
^^^^^^^^
The include filter can be used inside input statement to filter files for the copy operation.

The include filter can have following attributes.

+------------------+-------------------------------------------+
| Attribute name   | description                               |
+==================+===========================================+
| files            | comma separated list of inpu files.       |
+------------------+-------------------------------------------+
| pattern          | regexp pattern to filter input files that |
|                  | are found in the input folder.            |
+------------------+-------------------------------------------+
| flatten          | "true"|"false" to define if the directory |
|                  | struture is flattened at output.          |
+------------------+-------------------------------------------+

**input include example**

This would copy files foobar/test/override.txt and foobar/test/s60.txt to output if they are found.::

  <input dir="foobar">
    <include files="test/override.txt, test/s60.txt"/>
  <input>

The below statement would copy all files ending with ".jpg" from userdata and copy them 
directly to the output root folder.::

  <input dir="userdata">
    <include pattern="\.jpg$" flatten="true"/>
  <input>

exclude
^^^^^^^^
The exclude filter can be used similarly as the include filter, but in a negative meaning. 
For example to ensure that files beginning with a dot are never copied.

The exclude filter can have following attributes.

+------------------+-------------------------------------------+
| Attribute name   | description                               |
+==================+===========================================+
| pattern          | regexp pattern to filter input files that |
|                  | are found in the input folder.            |
+------------------+-------------------------------------------+

**input exclude example**

This would exclude all files that have .svn as part of the file path::

  <input dir="foobar">
    <exclude pattern="\.svn"/>
  <input>


How to create a content file
----------------------------

* Create a new file in the content folder name for ex. mycontentfile.content
* Set the file encoding to UTF-8
* Set the definition tag first *<?xml version="1.0" encoding="UTF-8"?>*
* Set the content tag *<content xmlns="http://www.s60.com/xml/content/1">*
* Set the description tag *<desc>Copy only prod</desc>*
* Set a content configuration tag for ex. *<include pattern="prod"/>*
* Set another content configuration tag for ex. *<output dir="content"/>*
* Close the content tag *</content>*

Now you have content file which copies the prod files to the content directory in the device configuration 

**example of a entire content file**

The example defines here two copy operations to two different outputs. First one to content with selected 
files as input and the other to include, where it tries to copy all \*.hrh files to the root of the include 
directory.

.. literalinclude:: example.content


Logic and rules
---------------

What may you define with content file logic. Here are some explanations.

* *<include pattern="prod"/>* include the files in the prod folder
* *<exclude pattern="prod"/>* exclude the files in the prod folder
* *<input dir="${content.inputdir}"/>* input files are setted in the value of the content/inputdir reference link in confml
* *<output dir="${content.outputdir}"/>* output files are setted in the value of the content/outputdir reference link in confml

So you may include and exclude folder and files. Content file definition supports regex patterns
You may give the location of the content as a confml reference link, *note: use the dots instead of slashes*  
 
 
XSD
---

.. literalinclude:: ../../xsd/contentml2.xsd
   :linenos:

 
FAQ
---
This will be updated based on the questions.
