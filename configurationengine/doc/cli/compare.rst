ConE compare action
===================
The compare action is intended to enable comparison of two configurations in different ways. The 
compare logic is done in a Jinja template, which makes it quite customizable. There are default
templates for data and API comparison that can be used with the --report-type switch, but a custom
template can also be used with the --template switch (see the examples).

Examples
--------

**Compare two configurations in current storage**::

    >cd configproject_root
    >cone compare -s configuration_root1.confml -t configuration_root2.confml

The output is generated under current folder.
By default the compare type is data comparison to data_comparison.html (use switch --report=FILENAME
to change the output file).

* Example output `Data comparison report <../_static/data_comparison.html>`_

**Compare configurations between the current storage and some remote storage**:

The target configuration can also include remote storage path, which must be separated from the 
configuration root by semicolon::

    >cd configproject_root
    >cone compare -s configuration_root1.confml -t \config_project2;configuration_root2.confml

**Compare configuration API between two configurations**

Use the --report-type switch make an API comparison.::

    >cd configproject_root
    >cone compare -s configuration_root1.confml -t \config_project2;configuration_root2.confml --report-type api

* Example output `API comparison report <../_static/api_comparison.html>`_

**Compare Customisation interface to a product configuration interface**

The **ci** comparison is created for specific comparison of Customisation interface to a product configuration interface. Its purpose is to find out differences between the CI and actual developer confmls (for example in assets/s60 layer). It compares the source configuration to target and reports differences and source features that are missing from target configuration. 

Use the --report-type switch make an ci (CustomisationInterface) comparison.::

    >cd configproject_root
    >cone compare -s customisation\CustomisationInterface\ci_root.confml -t vasco_langpack_01_root.confml --report-type=ci
    Writing report to ci_comparison.html
    Generated report to 'ci_comparison.html'
    Done.

* Example output `CI comparison report <../_static/ci_comparison.html>`_


**Compare configurations using a custom template**

Use the --template switch to specify a custom template file.::

    >cd configproject_root
    >cone compare -s configuration_root1.confml -t \config_project2;configuration_root2.confml --template my_template.html

Options list
------------
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --print-settings      Print all the default settings from the current
                        setting container.
  --print-supported-impls
                        Print all supported ImplML XML namespaces and file
                        extension.
  -v LEVEL, --verbose=LEVEL
                        Print error, warning and information on system out.
                        Possible choices: Default is 3.
                        NONE (all)    0
                        CRITICAL      1
                        ERROR         2
                        WARNING       3
                        INFO          4
                        DEBUG         5
  --log-file=FILE       Location of the used log file. Default is 'cone.log'
  -p STORAGE, --project=STORAGE
                        defines the location of current project. Default is
                        the current working directory.

  Compare options:
    The generate function will create target files from a specific
    configuration.The generate will always work with read-only mode of the
    project, so no changes are saved to project

    -s CONFIG, --sourceconfiguration=CONFIG
                        defines the name of the sourceconfiguration for the
                        compare action. The configuration is expected to be
                        located current storage.
    -t CONFIG, --targetconfiguration=CONFIG
                        defines the name of the target configuration for the
                        compare action. The configuration can be located in
                        the current storage or it the configurationdefinition
                        can contain a path to a storage. The storage
                        definition is given as a pathbefore semicolon. e.g.
                        x:\data\configproject;productx.confml,
                        test.cpf;root.confml
    --report=FILE       The file where the comparison report is written.By
                        default this value is determined by the used report
                        type. Example: -r report.html.
    --template=FILE     Template used in a report generation. By default this
                        value is determined by the used report type. Example:
                        -t report_template.html.
    --report-type=TYPE  The type of the report to generate. This is a
                        convenience switch for setting the used template.
                        Possible values:
                        api - Report changes in feature definitions
                        ci - Report changes in CustomisationInterface definitions
                        crml_dc - Report CRML data compatibility issues
                        crml_dc_csv - Report CRML data compatibility issues
                        (CSV format)
                        data - Report changes in data values
    --impl-filter=PATTERN
                        The pattern used for filtering implementations for the
                        comparison. See the switch --impl in action generate
                        for more info.
