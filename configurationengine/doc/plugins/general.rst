ImplML and plug-ins
===================

The `configuration project` concept contains an interface/implementation split
by using the Configuration Markup Language (ConfML) to specify the interface for
configurable entities in a project, and an arbitrary number of Implementation
Markup Languages (ImplML) to specify the output generated based on the interface.

ConE plug-ins supply the actual code-level implementations for the different
implementation languages. This page describes common ImplML concepts.


ImplML basics
-------------

All implementation languages are based on XML, and each separate
Implementation Mark-up Language (ImplML) resides within a single
XML namespace. The namespace of the ImplML must be defined in
the file, or the implementation won't be recognized. For example,
the following file is an example of CRML (Central Repository
Mark-up Language):


.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <repository xmlns="http://www.s60.com/xml/cenrep/1" uidName="Feature1_1" uidValue="0x00000001" owner="0x12341000">
        <access type="R" capabilities="AlwaysPass"/>
        <access type="W" capabilities="AlwaysPass"/>
        
        <key ref="Feature1/IntSetting" name="Int setting" int="0x00000001" type="int" readOnly="false" backup="true">
            <access type="R" capabilities="AlwaysPass"/>
        </key>
    </repository>

Notice the use of the XML namespace ``xmlns="http://www.s60.com/xml/cenrep/1"``
in the root element. This is what tells ConE that a CRML implementation should
be read from this XML document's root element. Here there is only one implementation
language used, and the extension of the file can reflect this (the extension is
.crml in this case).

However, the use of XML namespaces to differentiate implementation languages
enables the mixing of multiple languages in a single implementation file.
For example, the following file uses two implementation languages under common container,
RuleML and ContentML:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        <ruleml xmlns="http://www.s60.com/xml/ruleml/2">
            <rule>
                CustomSettings.StartupSoundFile.localPath configures StartupSettings.StartupSoundPath
                    = Startup.StartupSoundPath filenamejoin CustomSettings.StartupSoundFile.localPath
            </rule>
        </ruleml>

        <content xmlns="http://www.s60.com/xml/content/3">
            <output file="${StartupSettings.StartupSoundPath}">
                <input file="${CustomSettings.StartupSoundFile.localPath}"/>
            </output>
        </content>        
    </container>

The execution order of elements inside the container is the same as the order of definition.

In this example, the RuleML section first sets the value of a ConfML setting,
whose value is then used in the ContentML section to copy the file to the
correct place. 
Notice how the XML namespaces are defined. 

 - The container is in http://www.symbianfoundation.org/xml/implml/1, the root element of implml namespace must always be container
 - The ruleml is in http://www.s60.com/xml/ruleml/2
 - The content is in xmlns="http://www.s60.com/xml/content/3"

When reading the implementation file, ConE checks the document root and its namespace 
to find out from namespace to start parsing. 

.. _implml-file-extensions:

File extensions
^^^^^^^^^^^^^^^

Implementations are read from files under layers' ``implml/`` directories
inside the configuration project. The extensions of these files matter
in whether implementations are attempted to be read from a file or
not. The generic implementation file extension is ``implml``, but plug-ins
may extend the list of supported file extensions. However, the extension
does nothing more than specify whether the file is attempted to be parsed or
not; no checking on the implementation types is done. This means that
it is possible to create e.g. a CRML file with the extension ``templateml``,
but of course this makes no sense and should be avoided. 

The extension checking mechanism is there in order to differentiate
implementation files and any other related files, e.g. Python scripts
used by RuleML implementations. This way, if an implementation file
contains invalid XML data an error will be shown to the user, but a
Python script (the reading of which as XML would invariably fail and
produce an error) will simply be ignored.

If you want to see what file extensions are supported, run to following
command::

    cone info --print-supported-impls

This will print something like the following::

    Running action info
    Supported ImplML namespaces:
    http://www.symbianfoundation.org/xml/implml/1
    http://www.s60.com/xml/cenrep/1
    http://www.s60.com/xml/content/1
    http://www.s60.com/xml/content/2
    http://www.s60.com/xml/convertprojectml/1
    http://www.s60.com/xml/genconfml/1
    http://www.s60.com/xml/imageml/1
    http://www.s60.com/xml/ruleml/1
    http://www.s60.com/xml/ruleml/2
    http://www.s60.com/xml/templateml/1
    http://www.s60.com/xml/thememl/1
    http://www.symbianfoundation.org/xml/hcrml/1

    Supported ImplML file extensions:
    implml
    content
    contentml
    crml
    gcfml
    convertprojectml
    ruleml
    imageml
    thememl
    templateml
    hcrml

Another way is to check the log file created when running ``cone generate``.
It should contain a line like the following::

    Supported implementation file extensions: ['templateml', 'ruleml', 'thememl', 'imageml', 'crml', 'content', 'contentml', 'convertprojectml', 'hcrml', 'gcfml', 'implml']

**Guidelines for implementation file naming**

- Use the corresponding file extension if the file contains only a
  single implementation instance (e.g. ``.crml`` for a CRML implementation)
- Otherwise use the generic ``implml`` extension with containers

Implementation container nesting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In example 1, implementations were defined under a single root container element. The container
elements can be nested to form sub containers under the single implementation file. 

For example:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        <container>
            <phase name="pre">
            <ruleml xmlns="http://www.s60.com/xml/ruleml/2">
                <rule>
                    CustomSettings.StartupSoundFile.localPath configures 
                    StartupSettings.StartupSoundPath = Startup.StartupSoundPath + "/" + CustomSettings.StartupSoundFile.localPath
                </rule>
            </ruleml>
        </container>
     
        <container>
            <phase name="normal">
            <content xmlns="http://www.s60.com/xml/content/3">
                <output file="${StartupSettings.StartupSoundPath}">
                    <input file="${CustomSettings.StartupSoundFile.localPath}"/>
                </output>
            </content>
            
            <!-- Another ContentML section, copies the file to another directory -->
            <content xmlns="http://www.s60.com/xml/content/3">
                <output dir="some/dir">
                    <input file="${CustomSettings.StartupSoundFile.localPath}"/>
                </output>
            </content>
        </container>
        
    </container>

Here the root level container has two sub-containers, where the first sub-container 
is executed in "pre" phase (<phase name="pre"> definition) and the second in "normal" phase.

.. _common-implml-namespace:

Common ImplML namespace
-----------------------

Because there are common elements that are relevant for most, if not all, implementations,
there is a common ImplML namespace (``http://www.symbianfoundation.org/xml/implml/1``)
that contains these. The common elements can be defined by default in the container elements.
The support for the plugin implementation support for common elements depends on the implementation 
of the plugin. So refer to the plugin specific documentation to what each plugins supports.

.. _implml-common-elements:

Elements 
^^^^^^^^

The common ImplML elements are illustrated with the following UML class diagram:

  .. image:: implml.jpg


====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
container             1 .. *                  Defines a container for sub elements. For details see 
                                              :ref:`implml-common-container` .
tempVariableSequence  0 .. *                  Defines a temporary sequence variable. For details see 
                                              :ref:`implml-common-temporary-variables`.
tempVariable          0 .. *                  Defines a temporary variable. For details see 
                                              :ref:`implml-common-temporary-variables`.
tag                   0 .. *                  Defines an implementation tag. For details see 
                                              :ref:`implml-common-implementation-tags`.
phase                 0 .. 1                  Defines a execution phase. For details see 
                                              :ref:`implml-common-invocation-phase` .
====================  ======================  ===============================================================================

.. _implml-common-container:

Container element
^^^^^^^^^^^^^^^^^

The container element in the common namespace is like its name says a implementation 
that can contain other implementations. So in other words containers can contain 
other containers or actual implementations, like templateml, content, ruleml, etc.

The key purpose of the containers is to offer a mechanism where one configuration 
implementation solution can be nicely wrapped to a single file. The whole solution might 
require generation of one or more output files, rules, content copying, executing system 
commands, etc. To resolve simple and more complex problems the containers offer a execution 
flow control, with phases, tags and conditions.

Example with conditional container execution:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1"
               condition="${Feature1.Setting1}"
               value="true">
        <!-- Affects to the root container and to the below implementation sections -->
        
        <content xmlns="http://www.s60.com/xml/content/2">
            <output dir="content" flatten="true">
                <input file="test/file1.txt"/>
            </output>
        </content>        
    </container>

In the above example the generation phase will check if the condition is evaluated as true before entering the container.
The condition="${Feature1.Setting1}" refers to a Feature value inside the configuration, and value="true" requires
that the value of that feature is True. So content copying of test/file1.txt to content/file1.txt is executed only when Setting1 
is set to True. 

.. _implml-common-invocation-phase:

Invocation phase
^^^^^^^^^^^^^^^^

Containers and implementations may define the phase in which they are executed, which can be 'pre',
'normal' or 'post'. The default phase is determined by the code-level implementation
(usually the default phase is 'normal'), but this can be overridden for an
implementation by using the ``phase`` element. The element contains a single mandatory
attribute, ``name``, which defines the execution phase.

When using containers in common implml files the ``phase`` of the implementation is always ignored. 
This enables overriding of the default ``phase`` of the implementations with the containers. 

Example with two implementation in post phase:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container  xmlns="http://www.symbianfoundation.org/xml/implml/1">        
        <!-- Affects to the root container and to the below implementation sections -->
        <phase name='post'/>
        
        <content xmlns="http://www.s60.com/xml/content/2">
            <output dir="content">
                <input>
                    <include files="test/file1.txt"/>
                </input>
            </output>
        </content>
        
        <ruleml xmlns="http://www.s60.com/xml/ruleml/1" xmlns:implml="http://www.symbianfoundation.org/xml/implml/1">                    
            <rule>X.Y configures X.Z = X.Y</rule>
        </ruleml>
    </container>


Example with two containers in different phases:

To run implementation in different phases you must define two separate containers
that have a separate phase in them. In the below example the root level container 
is entered and executed in pre,post phase but the first sub-container only in 
pre phase and the second container in post phase.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">        
        <container>
            <phase name='pre'/>
            <ruleml xmlns="http://www.s60.com/xml/ruleml/1" xmlns:implml="http://www.symbianfoundation.org/xml/implml/1">                    
                <rule>X.Y configures X.Z = X.Y</rule>
            </ruleml>
        </container>
    
        <container>
            <phase name='post'/>
            
            <content xmlns="http://www.s60.com/xml/content/2">
                <output dir="content">
                    <input>
                        <include files="test/file1.txt"/>
                    </input>
                </output>
            </content>
        </container>
            
    </container>
    
.. _implml-common-implementation-tags:

Implementation tags
^^^^^^^^^^^^^^^^^^^

A concept common to all implementations are implementation tags. These are simple
name-value pairs that can be used as one way of filtering the implementations
when generating. For example the tag ``target : core``, could be used to tag
the particular implementation and, when generating, the same tag could be used to
generate only implementations for the target *core*.

Tags can be defined in implementations that support them or in containers that 
hold implementations. The overall tags of a container is a sum of all tags defined 
in its children (including sub-container and implementations)

To generate only the implementations for the *core* target the following generation command could be used::

    cone generate --impl-tag=target:core

**Tag elements**

Tag elements are simple XML elements defining name-value pairs.
There can be multiple tags with the same name, in which case the resulting value
for that tag will be a list of all the specified values. Examples:

.. code-block:: xml

    <tag name="target" value="core">
    <tag name="target" value="rofs2">
    <tag name="target" value="uda">
    <tag name="content" value="music">

Tags can also get their values from ConfML settings, which can be referenced in the usual way:

.. code-block:: xml

    <tag name="${Feature.TagName}" value="somevalue"/>
    <tag name="target" value="${Feature.TargetValue}"/>

When tags are defined to the container it will basically affect on all its sub implementations.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        <tag name='target' value='core'/>
        <tag name='target' value='rofs2'/>
        
        <content xmlns="http://www.s60.com/xml/content/2">
            <output dir="content">
                <input>
                    <include files="test/file1.txt"/>
                </input>
            </output>
        </content>
        
        <ruleml xmlns="http://www.s60.com/xml/ruleml/1">
            <rule>X.Y configures X.Z = X.Y</rule>
        </ruleml>
    </container>

In this case both the ContentML and RuleML sections would have the same tags.

The tag elements can be defined also in some implementation namespaces directly under the root element. E.g. the content in the following
content file would be copied to the output only for targets *core* and *rofs2*:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <content xmlns="http://www.s60.com/xml/content/2" xmlns:implml="http://www.symbianfoundation.org/xml/implml/1">

        <tag name='target' value='core'/>
        <tag name='target' value='rofs2'/>
      
        <output dir="content">
            <input>
                <include files="test/file1.txt"/>
            </input>
        </output>
    </content>
    

Filtering Based on Implementation Tags
''''''''''''''''''''''''''''''''''''''

This chapter explains how to create implementation tag specific implementation files. 
`cone_defaults.cfg` defines the default tags for plugins. If nothing is defined 
for a certain plugin type then plugin_tags variable is empty. Basically empty 
tag means that corresponding plugin participates only those generation where 
generation is not filtered by any implementation tag. If generation defines 
implementation tag filter then generation is done only for those plugins that 
match with the filter. If filter is not given filtering is not done and all 
plugins are participating in generation. In case of customization layer this 
would mean that uda content could end up to rofs3 section. Filtering is done 
only for normal and post phases, which means that you don't need to define 
any tag for ruleml files since they are ran in pre phase. Default value 
can be overridden in implementation file of the plugin like the following example 
shows. 

**Example 1:**

Content plugin default value in cone_defaults.cfg is target:rofs3, which means 
that by default it participates in generations that doesn't define 
implementation tags or defines rofs3. However we want create content files that 
copies stuff to uda. It can be done by overriding tag in .content file by  
adding the following line there:

::

    <tag name='target' value='uda'/>

**Example 2:**

commsdat.content doesn't contain any tag information and cccccc00.cre should 
go to rofs3 image. No actions needed because default value for content is rofs3.

Current default values for plugins:

::

    CRML    = 'core','rofs2','rofs3'
    GCFML   = 'core','rofs2','rofs3'
    CONTENT = 'rofs3'
    MAKEML  = 'makefile'
    RULEML  = ''
    IMAGEML = 'rofs3'
    THEMEML = 'rofs3'

Workflow for creating new implementation file:

  .. image:: tag-fil.jpg



.. _implml-common-temporary-variables:

Temporary variables (generation-scope temporary ConfML features)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The common ImplML namespace also makes it possible to define temporary variables
for e.g. passing information between implementations or specifying a constant in only
one place. Unlike implementation tags, the temporary variables are not
implementation-specific, but they are visible to all implementations, because they are
normal ConfML settings. However, overwriting existing features in the
configuration is prevented by raising an error when defining a feature that already exists.
Therefore the names of used temporary variables should be chosen with care.

Temporary variables can be defined as follows:

.. code-block:: xml

    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        <tempVariable ref="TempFeature.IntSetting" type="int" value="123"/>
        
        <!-- Default type is 'string' -->
        <tempVariable ref="TempFeature.StringSetting" value="test"/>
        
        <!-- Initial value from an existing ConfML setting -->
        <tempVariable ref="TempFeature.StringSetting2" type="int" value="${ExistingFeature.Setting}"/>
        
        <!-- TempFeature.IntSetting has already been defined, so this will always raise an error -->
        <tempVariable ref="TempFeature.IntSetting" type="int" value="555"/>
        
        <!-- Simple sequences can also be defined. -->
        <tempVariableSequence ref="TempFeature.SequenceSetting">
            <tempVariable ref="StringSubSetting" type="string"/>
            <tempVariable ref="IntSubSetting" type="int"/>
        </tempVariableSequence>
    </container>

Temporary variables only support the simplest ConfML setting types:

- string
- int
- real
- boolean

**Usage example**

In this example, we have the need to copy files from a number of different
locations to the output directory based on arbitrary logic. To do this, we create
a temporary sequence, populate it in a rule, and finally copy the files to
the output. This way there is no need to define a custom ConfML setting in
a separate file and include it in the project, so all implementation-specific
concerns are on the implementation side and do not leak to the interface (ConfML).

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        
        <!-- Temporary sequence setting for storing a generation-time created list of files to copy -->
        <tempVariableSequence ref="FileCopyTemp.Files">
            <tempVariable ref="Path" type="string"/>
        </tempVariableSequence>
        
        <!-- Rule for populating the temporary sequence -->
        <ruleml xmlns="http://www.s60.com/xml/ruleml/2">
            <rule>True configures FileCopyTemp.Files = {% get_file_list() %}</rule>
            
            <!-- Python script containing the get_file_list() -->
            <!-- function used above. It does whatever tricks -->
            <!-- are necessary to obtain the list of files to -->
            <!-- copy.                                        -->
            <eval_globals file="scripts/file_copy.py"/>
        </ruleml>
        
        <!-- ContentML implementation for copying the created file list to output -->
        <content xmlns="http://www.s60.com/xml/content/3">
            <output dir="some_dir/">
                <input files="${FileCopyTemp.Files.Path}"/>
            </output>
        </content>
        
    </container>


.. _implml-common-setting-refs-override:

Overriding setting references
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During generation, implementation instance may be filtered based on the setting references
they use. Normally the set of references should be correctly determined by the implementation
instance itself, but if for some reason the references need to be overridden in the
ImplML file, it is possible by using the common ``settingRefsOverride`` element.
The element can be used in two ways:

- It may contain a set of ``settingRef`` sub-elements defining the setting
  references
- It may contain a ``refsIrrelevant`` attribute that, if set to ``true``,
  specifies that setting references are irrelevant for the implementation. In
  this case the implementation will never be filtered out based on setting
  references during generation.

**Examples**

.. code-block:: xml
    
    <settingRefsOverride refsIrrelevant="true"/>

.. code-block:: xml
    
    <settingRefsOverride>
        <settingRef value="SomeFeature.SomeSetting"/>
        <settingRef value="SomeFeature.SomeOtherSetting"/>
    </settingRefsOverride>


.. _implml-common-setting-output-dir-override:

Overriding output directory parts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final output directory for implementation output is consists of three parts:

- *Output root*, speficied from the command in the ``generate`` action
- *Output sub-dir*, specified in a setting file (e.g. ``content/`` for CRML in
  iMaker variant content output settings file)
- *Plug-in output*, specified in a setting file (e.g. ``private/10202BE9`` for CRML)
- *Output file name*, specified in the implementation file in some way, may also
  contain some intermediary directories before the actual file name
  (e.g. ``12345678.txt`` for a CRML file with repository UID 0x12345678)

Of these, the two first may be overridden in the implementation file using
the common ImplML elements ``outputRootDir`` and ``outputSubDir``. These elements
may contain a single ``value`` attribute containing the directory name.

**Examples**

.. code-block:: xml
    
    <outputRootDir value="\epoc32\data"/>
    <outputSubDir value="widgets"/>


.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
        
        <!-- Temporary sequence setting for storing a generation-time created list of files to copy -->
        <outputRootDir value="\epoc32\data"/>
        <outputSubDir value="widgets"/>

        <!-- ContentML implementation for copying the created file list to output -->
        <content xmlns="http://www.s60.com/xml/content/3">
            <output dir="some_dir/">
                <input file="test.wgz"/>
            </output>
        </content>
        
    </container>

In the above example the content is copied to \epoc32\data\widgets\some_dir\text.wgz.


.. rubric:: Footnotes

.. [#multi-content-note] In this case the run-time behavior would still be same; ContentML
   allows multiple ``output`` elements. However, this might not be the case for all
   implementation languages.

.. [#legacy-implml-root-name-note] The specifications for the legacy implementation
   languages CRML and GenConfML do give the root element names, and say that each
   implementation must be in its own crml/gcfml file.
   It is recommended to stick to this convention for these two implementation languages
   also in the future. Indeed, using them in a multi-implementation file has not been
   tested and may not even work correctly.
