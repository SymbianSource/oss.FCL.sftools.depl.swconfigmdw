.. _validation-overview:

Validation overview
===================

.. note::
    This page gives an overview of ConfML and ImplML validation with ConE.
    For the actual CLI action see :ref:`cli-action-validate`

ConE supports validation of the ConfML and ImplML files in configurations
projects. This basically means that you can pass a configuration for validation
and ConE will spit out a list for *problems*, which can be errors, warnings or
informational messages associated with a file and a line number.

For example, a list of validation problems might look something like the
following:

=================================== ======  ======================================  =========== ===========================================================================
File                                Line    Type                                    Severity    Message
=================================== ======  ======================================  =========== ===========================================================================
Layer1/confml/broken.confml         1       xml.confml                              error       no element found: line 1, column 0
Layer1/confml/test.confml           11      model.confml.invalid_value.maxlength    error       Setting ValidationTest.Foo: Maximum number of characters is 3 (value has 6)
Layer1/confml/test.confml           12      model.confml.missing_feature_for_data   error       Feature 'ValidationTest.Bar' not found
Layer1/implml/00000002_foo.crml     6       model.implml.crml.invalid_ref           error       Setting 'Foo.Bar' not found in configuration
Layer1/implml/00000003_bar.crml     10      model.implml.crml.duplicate_uid         error       Duplicate key UID 0x00000001 (duplicate with keys on lines 6, 7 and 8)
Layer1/root.confml                  7       schema.confml                           error       Element 'foo': This element is not expected.
=================================== ======  ======================================  =========== ===========================================================================

From a slightly lower-level perspective validation happens on three levels:

#. XML level - Files that contain invalid XML data are caught here
#. XML Schema level - Things like missing attributes in elements are caught here
#. Model level - The rest of possible problems that the other validation levels
   cannot handle are caught here

Problem types and filtering
---------------------------

You might have noticed the *type* column in the example above. This is a
hierarchical problem type ID that can be used to filter a list of problems to
narrow it down to only problems of interest. *Hierarchical* here means that
the parts separated by commas are basically sub-IDs, the highest level sub-ID 
being the leftmost one. For example, suppose that we have a problem whose type
is ``model.implml.crml.invalid_ref``. Reading the sub-IDs from left to right
we can see that:

#. It is a problem caught during model-level validation
#. It is an ImplML problem
#. The specific ImplML in this case is CRML
#. The problem is that a CRML key references a ConfML setting that does not exist

Filtering of problems by type happens by specifying a list of *includes* and
a list of *excludes*. The output will contain only problems that match any of
the includes, but do not match any of the excludes.

If we wanted to set up a filter that shows only problems of the type in the 
example above, we could simply use a single include: ``model.implml.crml.invalid_ref``.
However, if we wanted to see all model-level CRML problems *except* that one,
we could include ``model.implml.crml`` and exclude ``model.implml.crml.invalid_ref``.
Now invalid reference errors would not show up, but duplicate UID errors
(type ``model.implml.crml.duplicate_uid``) would. Wildcards are also possible,
so including ``*.confml`` would include all ConfML problems: XML-level,
schema-level and model-level, or ``model.implml.*.invalid_ref`` would include
all ImplML errors for references to non-existent settings.

The two first sub-IDs for problem types come from the three validation
levels and the fact that ConfML and ImplML can be validated. The following
table shows the problem types for all cases:

+-------------------+--------------------+-------------------+
|                   | **ConfML**         | **ImplML**        |
+-------------------+--------------------+-------------------+
| **XML-level**     | ``xml.confml``     | ``xml.implml``    |
+-------------------+--------------------+-------------------+
| **Schema-level**  | ``schema.confml``  | ``schema.implml`` |
+-------------------+--------------------+-------------------+
| **Model-level**   | ``model.confml``   | ``model.implml``  |
+-------------------+--------------------+-------------------+

The sub-IDs after that depend on the context. For example, ImplML validation
typically has the implementation language as the next sub-ID: ``model.implml.crml``
or ``schema.implml.genconfml``.
