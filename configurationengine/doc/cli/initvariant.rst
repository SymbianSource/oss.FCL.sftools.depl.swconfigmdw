ConE initvariant action
=======================

The *initvariant* action is intended for merging a variant CPF back into the
configuration project. It is basically a special-purpose merge action that
merges all customer variant layers (layers with ``custvariant*`` in their path
name) and renames them based on the given variant ID and variant name
(``custvariant_<id>_<name>``).

Examples
--------

**Merging a variant CPF using variant ID and name**::

    > cd configproject_root
    > cone initvariant -r variant.cpf --variant-id 123 --variant-name foobar

This will merge customer variant layers into the project. The configuration
root into which they are merged is also determined automatically based on the
supplied information. The automatically determined root file is named
``<product-name>_custvariant_<variant-id>_<variant-name>_root.confml``,
and the merged layers will have ``custvariant_<variant-id>_<variant-name>``
as part of their layer path.
E.g. the layer ``familyx/productx/customer/custvariant/configurator/root.confml``
is merged as ``familyx/productx/customer/custvariant_123_foobar/configurator/root.confml``
and the configuration root would be ``productx_custvariant_123_foobar_root.confml``.

**Merging a variant CPF into a specific root file**::

    > cd configproject_root
    > cone initvariant -r variant.cpf --variant-id 123 -c foovariant.confml

This does basically the same thing as the previous command, except that the
configuration root into which the merge is done is explicitly specified. Also,
the optional argument ``--variant-name`` is missing, so the layers will be merged
as ``custvariant_<variant-id>``.

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
  -p STORAGE, --project=STORAGE
                        Defines the location of current project. Default is
                        the current working directory.

  Initvariant options:
    The initvariant action is intended for merging a variant CPF back into
    the configuration project. It merges all customer variant layers
    (layers with custvariant* in their path name) and renames them based
    on the variant ID and variant name ("custvariant_<id>_<name>").

    -c CONFIG, --configuration=CONFIG
                        Defines the name of the target configuration. By
                        default the configuration file name is composed of
                        product name, variant ID and variant name like this:
                        <product>_custvariant_<id>_<name>_root.confml
    -r STORAGE, --remote=STORAGE
                        Defines the location of remote storage (CPF)
    -s CONFIG, --sourceconfiguration=CONFIG
                        Defines the name of the remote configuration inside
                        the remote storage. Default is the active root of the
                        remote project.
    --variant-id=VARIANT_ID
                        Variant ID, mandatory.
    --variant-name=VARIANT_NAME
                        Variant name, optional.
    --product-name=PRODUCT_NAME
                        Product name, taken from the configuration data by
                        default (i.e. defaults to '${imakerapi.productname}')
    --set-active-root   Set the newly created (or merged) configuration root
                        as the project's active root after the merge is done.