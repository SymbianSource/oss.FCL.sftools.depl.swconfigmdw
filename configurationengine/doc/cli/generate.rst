ConE generate action
====================
Running action generate
Usage: cone generate [options]

The generate action is intended to generate output files with different implementation plugins. The
implementation files can be filtered by different mechanism, via the command line options. 

Examples
--------

**Generate all files of a configurations**::

    >cd configproject_root
    >cone generate -c configuration_root.confml

or use the option -p|--project to point to the configuration project root::

    >cone generate --project=configproject_root -c configuration_root.confml

**Generate by filtering with values in last layer**

The data can be located in different layers in configuration project. Quite a common use case is to 
generate only output files that have been changed in the last layer.::

    >cd configproject_root
    >cone generate -c configuration_root.confml --layer=-1

This will read data value definitions on the last configuration layer (last included confml 
file in the root file), and run generate only to implementation files that use one of these
data values.

Options list
------------
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --print-settings      Print all the default settings from the current
                        setting container.
  --print-supported-impls
                        Print all supported ImplML XML namespaces and file
                        extensions.
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

  Generate options:
    The generate function will create target files from a specific
    configuration.The generate will always work with read-only mode of the
    project, so no changes are saved to project

    -o FOLDER, --output=FOLDER
                        defines the target folder where the files are is
                        generated or copied
    -l LAYER, --layer=LAYER
                        define layers of the configuration that are included
                        to the output. The layer operation can be used several
                        times in a single command.Example -l -1 --layer=-2,
                        which would append a layers -1 and -2 to the layers =>
                        layers = -1,-2
    --all-layers        Include all layers in generation. This switch
                        overrides all other layer configurations (iMaker API
                        and using the --layer parameter)
    -i IMPLS, --impl=IMPLS
                        Define a Python regular expression filter for actual
                        ImplML plugin(s) that needs to be executed. The whole
                        path to ImplML filename is used in the regexp
                        matching. The impl operation can be used several times
                        in a single command.
                        Example1 --impl crml => matches for any ImplML file
                        that has a CrML string in the path. Example2 --impl
                        makeml$ => matches for ImplML file that has ends with
                        MakeML string.
    --impl-tag=TAG      define a tag for the implementations that are included
                        to the output. A tag is name value pair and has the
                        following format: name:value, e.g.
                        target:rofs3.Example --impl-tag=target:uda --impl-
                        tag=target:content, which would include impls include
                        both tags.
    --impl-tag-policy=TAGS_POLICY
                        Policy for implementation tags. May have one of the
                        following values: --impl-tag-policy=AND, --impl-tag-
                        policy=OR. Default is OR.
    -s SET, --set=SET   Override a ConfML reference in the execution.The set
                        operation can be used several times in a single
                        command.Example -s foo.bar=10 -s foo.fea='test'.
    --add=CONF          Add a given configuration to the given configuration
                        as last element.The add operation can be used several
                        times in a single command.Example --add
                        foo/root.confml --add bar/root-confml.
    -r FILE, --report=FILE
                        Generates a report about settings that are properly
                        generated.Example -r report.html.
    -t FILE, --template=FILE
                        Template used in report generation.Example -t
                        report_template.html.
    --report-data-output=FILE
                        Specifies a file where intermediary report data is
                        generated.
    -n, --dryrun        Executes generation without generation output.
    --add-setting-file=FILE
                        Generate specific settings in ini format.Example -o
                        my_generate_settings.cfg.
