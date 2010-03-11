ConE export action
==================
Running action export
Usage: cone export [options]

The export functionality exports configurations from the current project to a remote project. Default value for the current project is the currently working directory. A project can be either a folder or a CPF/ZIP file.

Examples
--------

**Export a configuration from folder to a zip file**::

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

  Export options:
    The export functionality is meant to export configurations between
    current project (defined with -p) to an remote project (defined with
    -r). Default value for the current project is the currently working
    directory. A project can be either a folder or a cpf/zip file.

    -r STORAGE, --remote=STORAGE
                        defines the location of remote storage. Default name
                        for remote storage is the source configuration name
    -a SET, --add=SET   Add a configuration layer to the given configuration
                        as last element.The add operation can be used several
                        times in a single command and it can create even an
                        empty layer.Example --add foo/root.confml --add bar
                        /root-confml.
    --exclude-folders   Excludes empty folders from .cpf export
