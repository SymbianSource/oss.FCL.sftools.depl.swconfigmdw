ConE merge action
=================

The merge functionality is meant to merge configurations/layers from a
remote project (defined with -r) to the current project (defined with
-p). Default value for the current project is the current working
directory. A project can be either a folder or a CPF/ZIP file.

There are two ways to use merge:

    #. Merge a configuration root into another
    #. Merge a specific source layer into a specific target layer

These translate to two use cases:

    #. Merging an asset into an existing configuration project
    #. Merging a variant data layer from an exported CPF back into the
       configuration project

Examples for these two use cases are given below.

Examples
--------

Files containing the used example data:

    - :download:`config_project.zip <merge/config_project.zip>`
    - :download:`myasset2.zip <merge/myasset2.zip>`

Merging an asset into configuration project
'''''''''''''''''''''''''''''''''''''''''''

Say that we have a small configuration project that contains the configuration
interface and implementation of some component, and we want to merge this asset
as part of a configuration project, specifically into the ``assets/myassets/``
layer in the project. This can be done by using the layer -> layer merging
functionality.

The image below shows what we want to accomplish. You can see that the 
``assets/myassets/`` layer already contains asset1, and we want to merge asset2
there too.

    .. image:: merge/asset_merge.png

We need to give ConE the layer root .confml files of the layers we want to
merge. To do this, run the following command:

::

    > cone merge -p config_project --targetlayer assets/myassets/root.confml -r myasset2 --sourcelayer asset2/root.confml
    Running action merge
    Target project: config_project
    Source project: myasset2
    Target layer:   assets/myassets/root.confml
    Source layer:   asset2/root.confml
    Merging layers...
    Copying asset2/confml/asset2.confml
    Copying asset2/content/asset2_data/dummy.txt
    Copying asset2/implml/asset2.templateml
    Including confml/asset2.confml in layer root assets/myassets/root.confml

Now the ``assets/myassets`` layer in the configuration project contains also
the contents of asset2.

Merging a variant configuration into configuration project
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Another use case is merging the variant data layer of an exported CPF back
into the configuration project. This is where the configuration root merge
comes in.

First, using the same example project as in the previous example, export a CPF
containing a variant data layer:

::

    > cd config_project
    config_project> cone export -c product_x_root.confml -r test.cpf --add variants/variant/root.confml
    Running action export
    Export product_x_root.confml to test.cpf done!
    
Now the CPF can be modified somehow, here we'll add the content files ``foo.txt``
and ``bar.txt``. After this we can merge it back into the project as a new
configuration root that contains also the variant data layer:

::

    config_project> cone merge -c foobar.confml -r test.cpf --rename
    Running action merge
    Target project: .
    Source project: test.cpf
    Target config:  foobar.confml
    Source config:  product_x_root.confml
    Merging 1 layer(s)...
    Merging variants/variant/root.confml -> variants/variant_foobar/root.confml
    Copying variants/variant/confml/data.confml
    Copying variants/variant/content/bar.txt
    Copying variants/variant/content/foo.txt
    Including confml/data.confml in layer root variants/variant_foobar/root.confml

The rename option tells ConE to rename the variant layer based on the given
configuration root name, so that the variant data layer becomes ``variants/variant_foobar/``.
So, now the project looks like this:

    .. image:: merge/project_after_variant_layer_merge.png

Note that the default merge doesn't overwrite the layers, it only adds/replaces
files from the source layers. If the entire layer should be overwritten, the
option --merge-policy can be used to specify that layers should be entirely
overwritten. For example, if we remove ``foo.txt`` from the variant content
in the CPF and re-merge like this:

::

    config_project> cone merge -c foobar.confml -r test.cpf --rename --merge-policy overwrite-layer
    Running action merge
    Target project: .
    Source project: test.cpf
    Target config:  foobar.confml
    Source config:  product_x_root.confml
    Merging 1 layer(s)...
    Merging variants/variant/root.confml -> variants/variant_foobar/root.confml
    Copying variants/variant/confml/data.confml
    Copying variants/variant/content/bar.txt
    Including confml/data.confml in layer root variants/variant_foobar/root.confml

Now ``variants/variant_foobar/content/`` contains only ``bar.txt``.

Options list
------------
    -c CONFIG, --configuration=CONFIG
                        defines the name of the target configuration for the
                        action
    -p STORAGE, --project=STORAGE
                        defines the location of current project. Default is
                        the current working directory.
    -r STORAGE, --remote=STORAGE
                        defines the location of remote storage
    -s CONFIG, --sourceconfiguration=CONFIG
                        defines the name of the remote configuration inside
                        the remote storage for the merge action. Default is
                        the active root of the remote project.
    --sourcelayer=LAYER_ROOT
                        Defines a specific layer to use as the layer to merge
                        from the remote project. Must be the layer root
                        (ConfML file).For example: --sourcelayer
                        assets/somelayer/root.confml
    --targetlayer=LAYER_ROOT
                        Defines a specific layer (root) to use as the layer to
                        merge into the target project. Must be the layer root
                        (ConfML file).For example: --targetlayer
                        assets/somelayer/root.confml
    --rename            defines that the merged layers need to be renamed
    --all               Defines that the entire configuration (all layers)
                        needs to be merged. This has no effect when merging
                        layers directly using --sourcelayer and --targetlayer.
    -l LAYERS, --layer=LAYERS
                        Define the layers of the source configuration that are
                        included to merge action. The layer operation can be
                        used several times in a single command. Note that this
                        can only be used when merging configuration roots, not
                        specific layers using --sourcelayer and --targetlayer.
                        Example -l -1 --layer=-2, which would append a layers
                        -1 and -2 to the layers => layers = -1,-2
    --merge-policy=MERGE_POLICY
                        Specifies the merge policy to use when merging layers.
                        Possible values:
                        replace-add - Add/replace files from source layer, but
                        leave other files in the target as they are.
                        overwrite-layer - Overwrite the entire layer (remove
                        all previous content).
