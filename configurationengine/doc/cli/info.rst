ConE info action
================
Running action info
Usage: cone info [options]

The info functionality is meant for printing information about the contents of a CPF/ZIP file or Configuration Project (folder).
Examples
--------

**Get a list of root configurations inside the project**::

    >cd configproject_root
    >cone info 

or use the option -p|--project to point to the configuration project root::

    >cone info --project=configproject_root 

**Get a list of root configurations inside a carbon storage (Available in ConE 1.2)**::

    >cone info --project=http://carbonqa.nokia.com/extapi

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
  -c CONFIG, --configuration=CONFIG
                        defines the name of the configuration for the action
  -p STORAGE, --project=STORAGE
                        defines the location of current project. Default is
                        the current working directory.
  --dump-api=FILE       Write the confml feature api string representation to
                        a file.

  Info options:
    The info functionality is meant for printing information about the
    contents of a cpf/zip file or Configuration Project (folder).

    --template=FILE     Template used in a report generation.Example -t
                        report_template.html.