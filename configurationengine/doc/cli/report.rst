ConE report action
==================

The report action can be used to create a report based on report generation
data created beforehand by the generate action using the switch ``--report-data-output``.
The report can be generated based on a single data file, or by merging multiple files.

Examples
--------

**Creating a report from a single data file**::

    cone report --input-data report.dat

This would generate a report based on the data in ``report.dat`` into ``report.html``
in the current directory.

**Creating a report from multiple files**::

    cone report --input-data rofs3.dat --input-data uda.dat --template template.html

This would generate a report based the data from two generation runs, one for ROFS3 data
and one for UDA data. The used template is overridden using ``--template``.

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

  Report options:
    The report function generates a report using previously generated
    intermediary report data as input.

    -i FILE, --input-data=FILE
                        Defines an input file for report generation. If
                        specified more than once, the data of all specified
                        report data files is merged.
    -r FILE, --report=FILE
                        Generates a report about settings that are properly
                        generated.Example -r report.html.
    -t FILE, --template=FILE
                        Template used in report generation.Example -t
                        report_template.html.
