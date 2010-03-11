User guide for Crml Plugin usage in ConE
----------------------------------------

Introduction
'''''''''''''
This page describes how to use ConE crml plugin. Crml plugin generates cenrep files out of 
configuration project which contains valid confml files and matching crml files.
Generated files can be included in phone image and creates settings according to confml and crml files.
You may change confml values and generate or regenerate confml project and thge generated cenrep files are changed
to given values. All files will be file encoded to UTF-16, (so you need a UTF-16 supported editor to view the
contents of the files)

CrML files are executed by default in **normal** :ref:`invocation phase <implml-common-invocation-phase>`.

CrML
'''''''''

The CrML syntax is a extension of Configuration markup language (confml). The term in confml for this extension 
is implementation method language (implml), which in CrML case is a xml file. 

All input values can be given as ConfML refs or as plain text. Also mixing text and ConfML ref information
is supported. 

  * Namespace: ``http://www.s60.com/xml/cenrep/1``
  * File extension: ``crml``

.. note::

   More information about :ref:`file extensions <implml-file-extensions>`. 

CrML Elements
.............

The CrML model is drawn out as a uml model in below picture.

  .. image:: crml.jpg

.. note::

   CrML supports also common ImplML elements. More information about :ref:`ImplML elements <implml-common-elements>` . 


<repository> Element
**************************

The repository element represents a single key repository (keyspace) in Central Repository.

Child Elements
++++++++++++++

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
key                   0 .. *                  Defines a single key in repository in Central Repository.
keyRange              0 .. *                  Defines a range of keys in repository in Central Repository.
access                0 .. 2                  Defines a represents read or write access control policy for a single key 
                                              or a key range. 
====================  ======================  ===============================================================================

Attributes
++++++++++

===================================  ======================  ===============================================================================
Attribute                            Required                Description
===================================  ======================  ===============================================================================
version                              Yes                     Defines the version of the language used. Must have value "1.0".
uidName                                                      Defines the unique identifier of the repository in symbolic form.
uidValue                                                     Defines the unique identifier of the repository in hexadecimal form. 
initialialisationFileVersion                                 Defines the version of the initialization file format. Default value is "1".
owner                                                        Defines the SID of the application or component which is responsible for 
                                                             backing up the repository. Defined in the form of hexadecimal number. 
                                                             Mandatory in case if repository contents are to be backed up by the secure
                                                             backup server.
backup                                                       Defines the default backup policy for runtime created keys. The supported 
                                                             values are "true" and "false". Should be set to true for non-read-only 
                                                             (that is, runtime writable) keys only. Default value is false.
===================================  ======================  ===============================================================================


Example
+++++++

.. code-block:: xml

  <repository version="1.0" uidName="KCRUidAvkon" uidValue="0x101F876E" owner="0x10207218">
        <desc>Keys for Avkon</desc>
        <meta>
            ...
        <meta/>
        <change>First version</change>
        <key>
            ...
        <key/>
        <key>
            ...
        <key/>
        <access>
            ...
        </access>
  </repository>


<key> Element
**************************

The key element represents a single key in repository in Central Repository.

Child Elements
++++++++++++++

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
value                 0 .. *                  Defines a mapping from a logical value in Configuration ML to an implementation
                                              specific value in a key in Central Repository.
bit                   0 .. *                  Defines a mapping from values of set of Boolean type settings in Configuration
                                              ML to a bitmask stored in a single key in Central Repository..
access                0 .. 2                  Defines a represents read or write access control policy for a single key 
                                              or a key range. 
====================  ======================  ===============================================================================

Attributes
++++++++++

===================================  ======================  ===============================================================================
Attribute                            Required                Description
===================================  ======================  ===============================================================================
name                                 Yes                     Defines the version of the language used. Must have value "1.0".
===================================  ======================  ===============================================================================


Example
+++++++

.. code-block:: xml

  <repository version="1.0" uidName="KCRUidAvkon" uidValue="0x101F876E" owner="0x10207218">
        <desc>Keys for Avkon</desc>
        <meta>
            ...
        <meta/>
        <change>First version</change>
        <key>
            ...
        <key/>
        <key>
            ...
        <key/>
        <access>
            ...
        </access>
  </repository>











Examples
'''''''''

**Cenrep file example**

* cenrep
* version 1
* [defaultmeta]
* 0
* cap_rd=alwayspass cap_wr=alwayspass
* [Main]
* 0x1 int 21 0 cap_rd=alwayspass cap_wr=alwaysfail
* 0x3 int 1801115478 0 cap_wr=alwaysfail
* 0x4 int 1082261569 0 cap_wr=alwaysfail

**What do the values mean**


* cenrep = tells that this is a cenrep configuration
* version = current version value
* [defaultmeta] = if the value is zero this file is not backuped in the rofs
* [platsec] = the values tells that which capabilities are passed or failed
* [Main] = start of the cenrep value information
* ex. 0x4 int 1082261569 0 cap_wr=alwaysfail
* eq. key key type value backup value capabilities

XSD
'''''''''

Download: :download:`crml.xsd </xsd/crml.xsd>`


FAQ
'''''''''
This will be updated based on the questions.





