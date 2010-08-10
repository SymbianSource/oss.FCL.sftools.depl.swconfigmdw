ConE export action
==================
Running action export
Usage: cone export [options]

The export functionality exports configurations from the current project to a remote project. Default value for the current project is the currently working directory. A project can be either a folder or a CPF/ZIP file or even a Carbon webstorage (via ExtAPI).

Examples
--------

**Export a configuration from configuration project folder to a zip file**::

    >cd configproject_root
    >cone export -c configuration_root.confml --remote=exported.zip

or use the option -p|--project to point to the configuration project root::

    >cone export --project=configproject_root --remote=exported.zip -c configuration_root.confml

**Export a configuration from a zip|cpf file to a folder**

The different to the previous example is that the project parameters are turned otherway around. ::

    >cd configproject_root
    >cone export --project exported.zip --remote=. -c configuration_root.confml 

**Export a configuration from a webstorage (carbon) file to a folder**

The Carbon functionality will be released in ConE 1.2 release and is not yet officially available. 
The usage is similar to the previous, but the carbon path is given as http://serverpath/extapi.::

    >cd configproject_root
    >cone export --project http://carbonqa.nokia.com/extapi -r . -c configuration_root.confml 

See the info action for getting a list of available configurations inside Carbon.

**Export a configuration from a folder to webstorage (carbon)**::

    >cd configproject_root
    >cone export --remote http://carbonqa.nokia.com/extapi -c configuration_root.confml 

**Export a configuration and run a action during the export**::
ConE can also run separate actions during the exporting for example to fix model level errors if possible. To run for example the fix step during export you can use --run-action=fix attribute.

    >cd configproject_root
    >cone export -c configuration_root.confml --remote=../export_folder --run-action=fix


Options list
------------
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --print-settings      Print all the default settings from the current
                        setting container.
  --print-supported-impls
                        Print all supported ImplML XML namespaces and file
                        extensions.
  --print-runtime-info  Print runtime information about ConE.
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
  --log-config=FILE     Location of the used logging configuration file.
                        Default is 'logging.ini'
  --username=USERNAME   Username for webstorage operations. Not needed for
                        filestorage or cpf storage. If the username
                        is not given, the tool will use the logged in
                        username. Example: cone export -p webstorage_url -r .
                        -c sample.confml --username=admin --password=abc123.
  --password=PASSWORD   Password for webstorage operations. Not needed for
                        filestorage or cpf storage. If the password
                        is not given, the tool will prompt for password if
                        needed.
  -c CONFIG, --configuration=CONFIG
                        Defines the name of the configuration for the action,
                        can be specified multiple times to include multiple
                        configurations.
  --config-wildcard=WILDCARD
                        Wildcard pattern for including configurations, e.g.
                        product_langpack_*_root.confml
  --config-regex=REGEX  Regular expression for including configurations, e.g.
                        product_langpack_\d{2}_root.confml
  -p STORAGE, --project=STORAGE
                        defines the location of current project. Default is
                        the current working directory.

  Export options:
    The export action is intended for exporting configurations from one
    project (storage) to another. A project can be a folder, a CPF or ZIP
    file, or a Carbon web storage URL.
    Two different ways of exporting are supported:
    1. Exporting multiple configurations into one new project using
    --remote
    2. Exporting configurations into a number of new projects using
    --export-dir

    -r STORAGE, --remote=STORAGE
                        Defines the location of remote storage. All
                        configurations included using --configuration,
                        --config-wildcard and --config-regex are exported into
                        the storage. If the remote storage location is not
                        given, the default location is determined based on the
                        first included source configuration name. E.g.
                        'example.confml' would be exported into 'example.cpf'
    --export-dir=EXPORT_DIR
                        Defines the directory where each included
                        configuration is exported as a new project.
    --export-format=EXPORT_FORMAT
                        Defines the format into which projects are exported
                        when using --export-dir. Possible values are 'cpf'
                        (the default) and 'dir'.
    -a CONFIG, --add=CONFIG
                        Adds a configuration layer to the given configuration
                        as last element. The add operation can be used several
                        times in a single command and it can create even an
                        empty layer. Example --add foo/root.confml --add bar
                        /root-confml.
    --run-action=PLUGIN
                        Adds a execution of extra step that can manipulate the
                        configuration before it is exported to external
                        storage. The --run-action operation can be used
                        several times in a single command and it will execute
                        the actions in given order.Example --run-action=fix,
                        which would execute fix action during export.
    --exclude-folders   Excludes empty folders from export
