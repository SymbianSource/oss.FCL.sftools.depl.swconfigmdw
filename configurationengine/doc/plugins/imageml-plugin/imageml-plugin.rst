User guide for ImageML Plugin usage in ConE
===========================================

Introduction
------------
This page describes how to use the ConE ImageML plug-in.
The plug-in defines the ImageML Implementation Markup Language, which provides
image conversion from BMP to MBM and SVG to MIF using the ``mifconv`` and
``bmconv`` tools.

XML namespace and file extension
--------------------------------

- Namespace: ``http://www.s60.com/xml/imageml/1``
- File extension: ``imageml``

ImageML elements
----------------

The ImageML XML element model is drawn out as a UML class diagram below:

  .. image:: imageml.jpg

output
^^^^^^

The ``output`` element defines an output file for image conversion. A single
ImageML implementation may contain multiple ``output`` elements.

**Attributes**

  * *file* - Output file location, for example ``resource/apps/image.mbm``.
    The output tool used to perform the conversion is deduced from the file
    extension: bmconv for .mbm and mifconv for .mif. The file location can
    also come from a ConfML setting using the ``${}`` notation.
  * *tool* - Override for the path to the tool to use. This is mainly useful
    for testing, in production use the bmconv and mifconv tools should be in PATH.
  * *palette* - Specifies a .pal file to use for MBM conversion.
  * *tooldir* - Override for the location of the bmconv and mifconv tools.
    This is mainly useful for testing, in production use the bmconv and mifconv
    tools should be in PATH.
  * *extraparams* - Optional attribute that can be used to pass extra parameters 
    for tool. For details see bmconv and mifconv documentation. E.g. "/V3" defines
    for mifconv the format version of SVG binary conversion. If not defined value
    forces Svgtbinencode to use the default platform specific value. 
    Options for mifconv /V parameter are:

.. list-table::

    - - *Value*
      - *Format type*
    - - /V1
      - BGR / float encoding
    - - /V2
      - BGR / fixed point encoding
    - - /V3
      - RGB / fixed point encoding
    - - /V4
      - RGB / float encoding
    - - /V5
      - NVG encoding


**Example**

.. code-block:: xml

    <output file="resource/apps/startup.mbm">
    
    <output file="resource/apps/startup.mif">
    
    <!--
    The drive letter is automatically stripped, and the output location
    is the same as in the example above
    -->
    <output file="Z:\\resource\\apps\\startup.mif">
    
    <output file="${StartupSettings.StartupAnimationPath}">


input
^^^^^

The ``input`` element defines a single input file for image conversion, or a
directory from which input files are selected based on regular expression
patterns. One ``output`` element may contain multiple ``input`` elements.

An input element must specify a file using the ``file`` attribute or a directory
using the ``dir`` attribute, but not both.

**Attributes**

  * *file* - Input file from the configuration project content. Can also be
    a ConfML setting reference using the ``${}`` notation.
  * *dir* - Directory for input files from the configuration project content.
    Can also be a ConfML setting reference using the ``${}`` notation.
  * *depth* - Color depth switch passed to bmconv for the file(s) specified by
    the current ``input`` element, does nothing if mifconv is used.
    Can also be a ConfML setting reference using the ``${}`` notation.
  * *optional* - If ``true``, then the input dir or file may be empty and
    no error is reported. Can be used to e.g. specify an optional mask bitmap.

**Examples**

.. code-block:: xml

    <input file="images/icon.svg"/>
    
    <input file="images/image.bmp" depth="c24"/>
    
    <input file="images/image_mask.bmp" depth="c1" optional="true"/>
    
    <input file="${TestFeature.BmpFile.localPath}" depth="${TestFeature.BmpDepth}"/>
    
    <input dir="images/svg_files/">
        <include pattern="svg$"/>
        <exclude pattern=".svn"/>
    </input>


include and exclude
^^^^^^^^^^^^^^^^^^^

The ``include`` and ``exclude`` elements specify regular expressions for
selecting input files from an input directory.

**Attributes**

  * *pattern* - The regular expression used to include or exclude files
  
**Examples**

.. code-block:: xml

    <include pattern="svg$"/>
    <include pattern="bmp$"/>
    <exclude pattern=".svn"/>

Setting references 
------------------

The setting references that an ImageML implementation uses are determined as
follows:

  * If any ``input`` elements contain setting references in their ``file``
    or ``dir`` attributes, those are the setting references used by the
    ImageML implementation.
  * If there are no setting references in those attributes, setting references
    are considered to be irrelevant, and the implementation is always run
    regardless of setting reference filtering.

See the examples in the section below.

ImageML examples
----------------

All the examples shown in this section can also be downloaded:

    * :download:`imageml-example-project.zip`

You need to have bmconv and mifconv somewhere in your path for generation to
work. To generate output from the project simply run::

    > cone generate -p imageml-example-project.zip

Or unzip (e.g. to ``imageml-example-project``) and run::
    
    > cd imageml-example-project
    imageml-example-project\> cone generate


Simple image conversion using a single input file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: examples/simple.imageml
   :language: xml

Setting references of this implementation: None (irrelevant)

Simple image conversion with ConfML setting references
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: examples/with_refs.imageml
   :language: xml

Setting references of this implementation:

    - ``TestSettings.ConeInputBmp.localPath``
    - ``TestSettings.IconInputSvg.localPath``

MBM conversion using multiple input files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: examples/multi_input.imageml
   :language: xml

Setting references of this implementation: None (irrelevant)

MBM conversion using an optional mask file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: examples/bmp_and_optional_mask.imageml
   :language: xml

Setting references of this implementation:

    - ``TestSettings.ConeInputBmp.localPath``
    - ``TestSettings.ConeInputBmpMask.localPath``

FAQ
---

This will be updated based on the questions.

