ConE rootflatten action
=======================

The *rootflatten* action is intended to be a temporary solution for enabling 
Configuration roots anywhere inside the project structure. The current 
Configuration project specification (0.4) is defined to allow configuration roots
only in the project root folder, so the root flatten will convert a file located
in any subfolder of the project to root file under the project folder that follows 
the Configuration project specification. 

The configuration roots in the subfolders can use absolute includes to include other 
configuration roots and / or layers.


Examples
--------

**Create a flat configuration from a Country configuration**

The configuration root could for example exist in family/product/country/`product_Euro2_ALPS_02_customisation_root.confml <../_static/country/product_Euro1_ALPS_01_customisation_root.confml>`_.
So this configuration root includes another configuration and two extra layers. The script trusts that the normal SD naming convention is in use, where all layer root confml files 
are just name root.confml (to know what is a configuration root and what is a layer). 

Commands::

    > cd configproject_root
    > cone rootflatten -c family\product\country\product_Euro2_ALPS_02_customisation_root.confml
    Running action rootflatten
    Processing configurations ['family\\product\\country\\product_Euro1_ALPS_01_customisation_root.confml']
    opened family\product\country\product_Euro1_ALPS_01_customisation_root.confml for flattening
    Creating a new configuration root 'product_Euro1_ALPS_01_customisation_root.confml' for flattening

After the conversion there will be a file with the same name in root where includes are flattened and meta data is merged. 
 * See `product_Euro2_ALPS_02_customisation_root.confml <../_static/product_Euro1_ALPS_01_customisation_root.confml>`_


Options list
------------
Options:
  -h, --help            show this help message and exit
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
