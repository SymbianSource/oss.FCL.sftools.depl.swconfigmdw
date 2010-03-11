Look in the generated drawsvg_temp\system_model_svg_tmp.xml file:

1. every item (not units) in the hardware layer should have: <... foo="bar" baz="xyzzy">
	Nothing else should have foo or baz attributes.

2. MTP Data Providers and all children (not units) should have <... this="comm"  that="no">

3. Generic OS Services shold have:    <block name="Generic OS Services" levels="physical-abstraction app-libs encoding translation data-services utilities" comment="This package is...">
	Nothing else should have a comment attribute