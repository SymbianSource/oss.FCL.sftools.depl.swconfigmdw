.. _plugin-howto-steps:

Step-by-step instructions for creating a new plug-in based on the example
=========================================================================

This page provides step-by-step instructions for creating a new plug-in based on the example
plug-in described in :ref:`plugin-howto-example-plugin`. The new plug-in will simply be exactly the same as the example plug-in, except that
the name will be changed from ExampleML to NewML.

These steps show how to create a new plug-in under the ``example`` plug-in package, but the instructions
can be used for creating an entirely new plug-in package also. To do that, simply export
``source/plugins/example`` into ``source/plugins/new`` instead of just ``source/plugins/example/ConeExamplePlugin``
into ``source/plugins/example/ConeNewPlugin``.

#. Export the example plug-in into the new plug-in path. With TortoiseSVN it can be done like this:
    #. Open ``source/plugins/example`` in Windows Explorer
    #. Drag'n'drop ``ConeExamplePlugin`` into the empty area using the right mouse button
    #. Select "SVN export to here" from the pop-up menu
    #. Select "Auto rename" from the dialog that pops up
    #. After the export is done, rename "Export of ConeExamplePlugin" to "ConeNewPlugin"
#. Refresh the ``plugins/`` directory in Eclipse
#. Rename all files and folders containing "exampleml" to "newml" under ``ConeNewPlugin/``
    - ``examplemlplugin/`` -> ``newmlplugin/``
    - ``exampleml_impl.py`` -> ``newml_impl.py``
    - ``tests/unittest_exampleml_generation.py`` -> ``tests/unittest_newml_generation.py``
    - ``tests/project/Layer/implml/test.exampleml`` -> ``tests/project/Layer/implml/test.newml``
    - etc.
#. Change "exampleml" to "newml" inside all files
    - Select "ConeNewPlugin" in the PyDev Package Explorer
    - Press Ctrl+H to do a file search. Use the following options:
         - Containing text: exampleml (case-insensitive)
         - File name patterns: *
         - Scope: Selected resources
    - Change the string everywhere (use the same case convention, e.g. "exampleml_impl" -> "newml_impl" and "ExamplemlReader" -> "NewmlReader")
#. Check that test cases are run correctly and they pass
    #. Run ``source/plugins/example/ConeNewPlugin/newmlplugin/tests/runtests.py`` to check that all tests pass (all modules are found etc.)
    #. Run ``source/plugins/example/runtests.py`` to check that all tests pass also from the plug-in package level
#. Modify ``setup.py``
#. Check that the new plug-in is present in a ConE installation created using the ``example`` plug-in package
    #. Go to the working directory on the command line and run (remember to use forward slashes)::
     
        install.cmd C:/cone_temp_or_whatever_dir example
    
    #. Go to the temporary directory specified in the previous step and run::
    
        cone info --print-supported-impls
    
    #. Check that you can find the new namespace and file extension in the list of supported namespaces and file extensions
