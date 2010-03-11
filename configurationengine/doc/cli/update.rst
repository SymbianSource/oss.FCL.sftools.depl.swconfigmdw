ConE update action
===================
Running action update
Usage: cone update [options]

The update functionality is meant for ConfML manipulation in current project (defined with -p). Default value for the current project is the currently working directory. A project can be either a folder or a cpf/zip file.

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

  Update options:
    The update functionality is meant for ConfML manipulation in current
    project (defined with -p). Default value for the current project is
    the currently working directory. A project can be either a folder or a
    cpf/zip file.

    -m META, --add-meta=META
                        Add given metadata to defined configuration.Example
                        --add-meta "owner=John Cone" -m product=E75
    --add-cpf-meta=CPFMETA
                        Add given CPF identification metadata to defined
                        configuration.Example --add-cpf-meta
                        "coreplat_name=Platform1"
    -d DESC, --add-desc=DESC
                        Add given description to defined configuration.Example
                        --add-desc "Customer one CPF" -d Description1
    --remove-meta=META  Removes given metadata from defined
                        configuration.Example --remove-meta owner --remove-
                        meta coreplat_name
    --remove-desc       Removes description from defined configuration.Example
                        --remove-desc
    --add-data=DATA     Add given ConfML data to defined configuration.Example
                        --add-data "KCRUidAvkon.KAknDefaultAppOrientation=1"
