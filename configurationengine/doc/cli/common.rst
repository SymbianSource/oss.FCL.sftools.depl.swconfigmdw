.. _cone-cli:

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
    
    Usage: ConE [action] [options].
    
    
    Use ConE [action] -h to get action specific help.
    
    Available actions
    Main actions for one or more configurations.
        compare : Compare two configurations
        fix : Run automatic fixes for configurations.
        generate : Generate a configuration.
        report : Create report of existing report data.
        update : Update/set values to features in configuration(s).
        validate : Validate a configuration, or individual confml/imp
    
    
    Actions related to the configuration project maintenance.
        export : Export configurations.
        info : Get information about project / configurations.
        merge : Merge a configuration/layer to the project.
    
    
    extensions:
        initvariant : Initialize a variant from a cpf.
        packvariant : Pack (zip) the variant layers of a configuration.
        rootflatten : Configuration root flattener.


ConE actions
------------
.. toctree::
    :maxdepth: 1

    generate
    fix
    compare
    report
    update
    validate
    export
    merge
    info
    initvariant
    rootflatten

