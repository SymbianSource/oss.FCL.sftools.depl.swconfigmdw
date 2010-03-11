Cone command line interface
===========================

ConE command line interface is desinged to offer different actions. A action can be anything that utilizes the ConE interface and 
somehow interacts with a Configuration Project. Each action has it's own set of command line arguments.

Calling ConE
------------

All ConE commands are wrapped up by the cone.cmd, which executes internally cone_tool.py. The cone_tool.py searches for all conesub_*.py 
matching files under the same scripts folder under cone installation. So basically adding a new action is just adding a new conesub_*.py file.

To get a list of all available cone commands run::

    cone -h
    
or::

    cone --help
  
And you will get something like this as output::

    Usage: cone_tool.py [action] [options].
    
    Available actions
        info
        compare
        merge
        export
        generate
        update
    
    Use cone_tool.py [action] -h to get action specific help.
    
    Options:
      --version                         show program's version number and exit
      -h, --help                        show this help message and exit 
      -c CONFIG, --configuration=CONFIG  Define the name of the configuration for the action
      -v LEVEL, --verbose=LEVEL          Print error, warning and information on system out. 
                                            Possible choices:
                                                NONE 0
                                                CRITICAL 1 
                                                ERROR 2 
                                                WARNING 3 
                                                INFO 4 
                                                DEBUG 5 
                                            Default is 3.
      -p STORAGE, --project=STORAGE      Defines the location of current project. Default is the current working directory.


ConE actions
------------
.. toctree::
    :maxdepth: 2

    info
    compare
    merge
    export
    generate
    update
    report

