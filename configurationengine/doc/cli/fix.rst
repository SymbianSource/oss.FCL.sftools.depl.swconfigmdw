ConE fix action
================
Running action fix
Usage: cone fix [options]

The fix functionality is meant for running possible automatic fixes to problems which validation reports.

Examples
--------

**Fix a configuration**::

    >cd configproject_root
    >cone fix -c configuration_root.confml

or use the option -p|--project to point to the configuration project root::

    >cone fix --project=configproject_root -c configuration_root.confml

**Print a list of available fix classes**::

    >cone fix --print-available-fixes
    
    Running action fix
    Available fixers:
    <class 'cone.validation.builtinvalidators.confml.DuplicateFeatureFixer'>:
        A Fix class for duplicate features that merges all setting under a duplicate feature
        to the first instance of the feature and removes the duplicates.
        
Options list
------------
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
                        Defines the name of the configuration for the action
  -p STORAGE, --project=STORAGE
                        defines the location of current project. Default is
                        the current working directory.

  Fix options:
    The fix action is intended for performing fixes on a
    configuration.

    --print-available-fixes
                        Print all configuration fixer objects available.
    --exclude-filter=EXCLUDE_FILTER
                        Exclude problems by given filter. Examples: --exclude-
                        filter=schema, --exclude-filter=schema.implml,
                        --exclude-filter=schema.confml, --exclude-
                        filter=schema.implml.ruleml
    --include-filter=INCLUDE_FILTER
                        Include problems by given filter.Examples: --include-
                        filter=schema.implml, --include-
                        filter=schema.implml.ruleml