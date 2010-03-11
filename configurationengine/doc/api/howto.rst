How to use cone APIs
====================

The ConE public usage is described here with few common use cases as HowTo guides. 

How to open a Configuration project
-----------------------------------

To open a project with ConE the api offers a Storage and Project classes. The Storage is the storage 
agostic implemenetation for cpf/zip, filestorage and soon also a webstorage. To access anything in ConE 
you must a project open. 

.. code-block:: python 

    from cone.public import api,exceptions
    """ 
    The Storage access can be given as a extra parameter. It can have values r=read|w=write|a=append. 
    The default Storage access is read, which will fail if the storage does not exist.
    
    The Storage.open method will try which of the storage implementations can open that particular path.
    So for example the path can be 
    'foo/bar'  => Opened with FileStorage
    'test.cpf' => Opened with ZipStorage
    'test.zip' => Opened with ZipStorage 
    """
    
    """ Open a storage to current path and give it to the project. """
    prj = api.Project(api.Storage.open('.'))
    """ Create a new storage to a cpf file and give it to the project. """
    prj = api.Project(api.Storage.open('test.cpf', 'w'))


How to access and manipulate Configurations
-------------------------------------------

A Configuration normally is presented inside the Configuration project as a .confml file. So when you
are accessing configurations your are actually accessing confml files. The project offers funtionality to 
get,add, remove configurations, which acts on root configurations inside the given project.

How to List configuration's
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python 

    from cone.public import api,exceptions
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ list and print all root configurations  """
    configlist = prj.list_configurations()
    for config in configlist:
        print config

How to Open configuration
^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: python 

    from cone.public import api,exceptions
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open a with name """
    """ 
    get_configuration raises a NotFound exception if the given configuration resource 
    is not found from Storage
    """
    try:
        myconfig = prj.get_configuration('myconfig.confml')
    except exceptions.NotFound:
        print "myconfml is not found from project!"

How to remove Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To remove a Configuration call  ``remove_configuration`` method of Configuration.

.. code-block:: python

    myconfig = prj.get_configuration('myconfig.confml')
    myconfig.remove_configuration('my_remove.confml')
    """ finally save and close project """
    prj.save()
    prj.close()

How to include a one Configuration to an other Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To include a one Configuration to an other call ``include_configuration()`` method of Configuration and pass the filename of Configuration as a parameter.

.. code-block:: python

    myconfig = prj.get_configuration('myconfig.confml')
    myconfig.include_configuration('../data.confml')

Feature Access and manipulation
-------------------------------

How to add a Feature to Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a Feature to Configuration ``add_feature()`` method can be used.

.. code-block:: python

    conf = api.Configuration("myconf.confml")
    conf.add_feature(api.Feature("feature1"))

How to add a child Feature to Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Childs can be added under Feature by ``add_feature()`` method and passing the parent Feature as a second paremeter:

.. code-block:: python

    conf = api.Configuration("myconf.confml")
    conf.add_feature(api.Feature("feature1"))
    conf.add_feature(api.Feature("feature11"),'feature1')

How to remove Feature from Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Features can be removed from Configuration by a following way:

.. code-block:: python

    conf1 = api.Configuration("myconf.confml")
    conf1.add_feature('feature1.feature12') # Add feature to Configuration
    conf1.remove_feature('feature1.feature12') # and then remove it
    """ finally save and close project """
    prj.save()
    prj.close()


How to get a Feature from Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Features can be accessed through View:

.. code-block:: python

    from cone.public import api
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open the first configuration from the list """
    firstconfig = prj.get_configuration(configlist[0])
    """ get default view of first configuration """
    default_view = firstconfig.get_default_view()
    """ fetch example_feature1 from default view """
    feature = default_view.get_feature('example_feature1')

Feature can be accessed also by a property:

.. code-block:: python

    from cone.public import api
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open the first configuration from the list """
    firstconfig = prj.get_configuration(configlist[0])
    """ get default view of first configuration """
    default_view = firstconfig.get_default_view()
    """ fetch example_feature1 from default view """
    feature = default_view.example_feature1

How to list all Features inside a certain View
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All Features can listed by calling ``list_all_features()`` method of View. Default view returns always 
the view from the Root configuration point of view.

.. code-block:: python

    from cone.public import api
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open the first configuration from the list """
    firstconfig = prj.get_configuration(configlist[0])
    """ get default view of first configuration """
    default_view = firstconfig.get_default_view()
    """ get all features in list from default view """
    features = default_view.list_all_features()

All features can be listed also using some custom View:

.. code-block:: python

    from cone.public import api
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open the first configuration from the list """
    firstconfig = prj.get_configuration(configlist[0])
    """ get my_view view to first configuration """
    view = firstconfig.get_view("my_view")
    """ fetch example_feature1 from my_view view """
    features = view.list_all_features()

How to list Features inside a certain View
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To list immediate Features found under the certain View can be done by calling ``list_features()`` method.

.. code-block:: python

    myconfig = api.Configuration("root.confml")
    view = myconfig.get_view("my_view")
    features = view.list_features()

How to list all Features inside a certain Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To list all Features found under a certain Configuration can be done by calling ``list_all_features()`` method of Configuration.

.. code-block:: python

    from cone.public import api
    """ Create a storage to current path and give it to the project """
    prj = api.Project(api.Storage.open('.'))
    """ open the first configuration from the list """
    firstconfig = prj.get_configuration(configlist[0])
    """ get all features in list from configuration """
    features = firstconfig.list_all_features()

How to read a value for a specific Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The a value of specific Feature can be read by calling ``get_value()`` method or using value property.

.. code-block:: python

    value1 = my_feature1.get_value()
    value2 = my_feature2.value

How to read a possible options of selection Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To list possible options of selection Feature can be done by calling ``get_valueset()`` method of Feature.

.. code-block:: python

    feature = api.Feature('my_selection_feature',type='selection')
    feature.add_option('one', '1')
    feature.add_option('two', '2')
    value_set = feature.get_valueset()
    feature.get_option('1').get_name() #returns  'one'

How to read a type of specific Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To read a specific type on Feature ``get_type()`` method or type property can be used. 

.. code-block:: python

    feature = dview.get_feature('my_feature')
    feature.get_type() # returns type of the Feature
    feature.type # returns type of the Feature

How to set a value for a specific Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set value for a specific Feature can be done by calling ``set_value()`` method or ``value`` property.

.. code-block:: python

    feature1 = dview.get_feature('my_feature1')
    feature2 = dview.get_feature('my_feature2')
    feature1.set_value(123)
    feature2.value = "my_value"
    """ finally save and close project """
    prj.save()
    prj.close()

Data access and manipulation
----------------------------
The data access inside a configuration is possible, but basically this can be avoided by manipulating the values 
of features, which actually modify the data elements inside the configuration.
However if direct data element access is needed, here's how you can do it.

How to add Data to Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add Data to Configuration can be done by calling ``add_data()`` method of Configuration: 

.. code-block:: python

    conf = api.Configuration("data.confml")
    conf.add_data(api.Data(ref='feature1', value=123))
    conf.add_data(api.Data(fqn='feature1.feature12', value="test"))
    """ finally save and close project """
    prj.save()
    prj.close()
    


