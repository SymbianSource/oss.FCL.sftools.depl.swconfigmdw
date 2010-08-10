.. _cone-development:

Development with ConE
=====================
This page should describe all relevant information on any developer who has or will create any functionality on
top of the ConE functionality.

ConE in SF
----------

ConE is a open source project (Currently under Eclipse Public License v1.0), which can take contributions from anyone interested in ConE. In future the ConE 
will propably be split to two separate parts; ConE *core* and ConE *plugins*. 

The core of ConE is mainly the public interface and the storage agnostic functionality of ConE. 
This core part is intended to be more generic and functional on any platform. 

The plugin part is meant for extensions of ConE that could be for example platform specific implementation plugins 
that generate output files based on the configurations.


Development environment
-----------------------
The development environment requires a set of python packages, which you mostly install with easy_install after 
installation of setuptools. So you must install the necessary libraries in order to be able to do cone development. 
The best way to test whether your development environment has everything that is required is to run all the unittest
of cone (See :ref:`cone-development-test-running`). When everything works, your environment is properly 
setup :)

**Required Python packages**
  - jinja2
  - simplejson 
  - lxml (at least version 2.2.2) run easy_install lxml==2.2.2
  - nose (for running testing)
  - epydoc (for documentation generation)
  - sphinx (for documentation generation) 
 
 
To install the above packages, run easy_install


easy_install call::

    easy_install <package-name>
    
easy_install jinja2 package::
    
    easy_install jinja2
  

.. _cone-development-test-running:

Running tests
-------------
The different packages inside cone have a tests subpackage which contains all the tests for that particular package. 
Each package also contains a runtests.py file that runs all tests inside that package with `nose <http://somethingaboutorange.com/mrl/projects/nose/0.11.3/>`_. 

The higher levels packages also contain a runtests.py which also collect all subpackage tests, so you can basically 
run every test of cone source by running the runtests.py at the root of source directory.

**Setting PYTHONPATH**

The cone modules need to be set to the PYTHONPATH to enable test running. If you are using eclipse with PyDev as 
developement environment, the PYTHONPATH should be automatically correct as the eclipse .project file is included 
in version control.

For command line testing you can run the testing_paths.cmd/testing_paths.sh to set the PYTHONPATH correctly. 
After that you should be able to run individual test are all test with a normal python call .

running all cone tests::
    
    cd source
    python runtests.py
    
    
running individual unittest example::
    
    cd source/cone/public/tests
    python unittest_configuration.py

running all module tests::
    
    cd source/cone/public/tests
    python runtests.py


running tests with nose::
    
    Tests can also be run with nose, effectively this is the same as running the runtests.py 
    
    cd source/cone/
    nosetests --include=unittest

Using ConE API
--------------

.. toctree::
    :maxdepth: 2

    api/api
