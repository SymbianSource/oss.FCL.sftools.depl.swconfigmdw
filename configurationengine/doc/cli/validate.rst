.. _cli-action-validate:

ConE validate action
====================

The validate action can be used to validate individual ConfML and ImplML files,
or an entire configuration. See also :ref:`validation-overview`.

Examples
--------

**Validating a single ConfML file**::

    cone validate --confml-file something.confml

This will validate the specified ConfML file and generate a report in
``validation_report.html`` using the default html report template. If you would like to 
produce an xml report ``validation_report.xml`` (which is based on Diamonds format) use the following command instead::

    cone validate --confml-file something.confml --report-type xml

* Example output `Validation report for Diamonds <../_static/report.xml>`_

**Validating multiple ConfML files**::

    cone validate --confml-file file1.confml --confml-file file2.confml

This will validate the list of specified ConfML files with --confml-file option. Several Implml files can be validated correspondingly with 
--implml-file option.

**Validating an entire configuration**::

    cone validate --project myproject --configuration myconfig.confml

This will find all ConfML and ImplML files in the configuration and validate
them, generating a report into ``validation_report.html``. The command output
might look something like this::
    
    C:\>cone validate --project myproject --configuration myconfig.confml
    Running action validate
    Project:       myproject
    Configuration: myconfig.confml
    Finding ConfML files in configuration...
    282 ConfML file(s)
    2 problem(s) while parsing
    Performing XML schema validation on ConfML files...
    40 problem(s)
    Validating ConfML model...
    34 problem(s)
    Finding ImplML files in configuration...
    Found 393 supported files
    Performing XML schema validation on ImplML files...
    7 problem(s)
    Parsing implementations...
    Validating implementations...
    1 problem(s)
    Total 84 problem(s) after filtering
    Generating report...
    Generated report to 'validation_report.html'


**Validating only ConfML files in a configuration**::
    
    cone validate --project myproject --configuration myconfig.confml --include-filter *.confml

This will run the same validation as in the previous example, except that
ImplML files are not validated.

**Validating only ImplML files in a configuration**::

    cone validate --project myproject --configuration myconfig.confml --include-filter *.implml

**Performing only schema validation**::

    cone validate --project myproject --configuration myconfig.confml --include-filter schema

Options list
------------

    --confml-file=FILE  Validate only the given single ConfML file.
    --implml-file=FILE  Validate only the given single ImplML file.
    --template=FILE     Template used in report generation. Example:
                        --template report_template.html.
    --report=FILE       Specifies the location of the validation report.
                        Example --report report.html.
    --report-type=TYPE  The type of the report to generate. This is a
                        convenience switch for setting the used template. If 
                        --template is given, this option has no effect.
                        Possible values:
                        xml - Generate an xml report
                        html - Generate html report
    --dump-schema-files=DIR
                        Dump the XML schema files used for validation into the
                        specified directory.
    --exclude-filter=EXCLUDE_FILTER
                        Exclude validation problems by given filter. Examples:
                        --exclude-filter=schema, --exclude-
                        filter=schema.implml, --exclude-filter=schema.confml,
                        --exclude-filter=schema.implml.ruleml
    --include-filter=INCLUDE_FILTER
                        Include validation problems by given filter.Examples:
                        --include-filter=schema.implml, --include-
                        filter=schema.implml.ruleml
