.. _plugin-api:

Extending ConE with plugin API
==============================

The Plugin api is intended for extending the ConE functionality with plugins.
Currently there are two ways to extend the functionality:

1. Adding support for new implementation languages
2. Extending ConfML or ImplML validation

Usually a plug-in that provides a new implementation language also provides
validation for it.

Developing a ConE plugin
------------------------
* See `Cone API epydoc <../epydoc/index.html>`_ for reference guide.

.. toctree::
    :maxdepth: 3

    ../plugins/dev-plugin/plugin-interface
    ../plugins/dev-plugin/index
    ../plugins/dev-plugin/validation-plugin-index