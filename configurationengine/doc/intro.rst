Introduction
============

ConE installation offers three different use scenarios of the tool.

#. ConE API (read, write)
#. ConE plugin API (A plugin interface to add functionality to ConE)
#. ConE command line interface (tools/utilities that use the API)

ConE API introduction
---------------------
The ConE API tries to offer a simple way to access the configurations inside the Configuration
project. The concepts of confml and the Configuration project are quite complicated, but the API
simplifies the project quite a bit to enable effective programming. Although the API aims for 
simplicity, everything is made available via the API.

The API is described in :ref:`cone-api` with a :ref:`cone-api-howto` and with python api documentation tool *epydoc*. 

ConE plugin (extension) API
---------------------------
The purpose of the plugin API is to offer the possibility to expand the functionality of Configuration project. Normal use case
is an implementation plugin which reads data from the configuration and transforms it into some other form 
(e.g. centralrepository text file). 

See :ref:`plugin-api`.

ConE command line interface introduction
----------------------------------------
The main purpose of ConE is to offer the above APIs, but ConE installation as tool
offers also set of command line utilities that can used to modify, read and utilize (generate other output files 
with implementation plugins) from a Configuration project. These utilities lie on the cone-script package and 
are described in the ConE command line interface section. 

See :ref:`cone-cli`

Installation
------------

Requirements
^^^^^^^^^^^^

ConE installation requires:
 
* Python 2.5 (though 2.6 probably works too)
* Ant (Required for installing from source)
* Python setuptools - http://pypi.python.org/pypi/setuptools. (Required to install ConE as part of python)

ConE can be installed in two different ways:

1. In the Python environment under site-packages like any other Python package

  - Makes it possible to use the ConE API from Python scripts

2. As a standalone installation in a separate directory

  - Contains the CLI and a set of plug-ins

Installing from source
^^^^^^^^^^^^^^^^^^^^^^

In order to install from source, you obviously need to first get the ConE sources:

* Clone the Mercurial repository:

  * ``hg clone https://developer.symbian.org/sfl/MCL/sftools/depl/swconfigmdw/``
  
* -- or -- checkout from SVN (if you are in Nokia intranet):

  * ``svn checkout https://trace1.isource-nokia.nokia.com/isource/svnroot/cone/trunk cone_src``

**Installing under site-packages**

Simply install using ``setup.py`` like for any Python package:
  
* ``cd cone_src/source``
* ``python setup.py install``

This will install the ConE core module into your Python environment. To install a plug-in,
do the same in the desired plug-in's source directory (e.g. ``cone_src/plugins/common/ConeRulePlugin``).

**Installing the standalone ConE**

The normal installation in windows environment creates a directory containing the needed
libraries and ConE plug-ins, and a ``cone.cmd`` wrapper script. The directory can then
be added somewhere into your PATH, and then the CLI can be used by running ``cone``.

To install, run:

* <windows> ``install.cmd /path/to/install common``
* <linux> *Not available yet*

Notice the parameter ``common`` in the install command. This specifies the plug-in package to install.
It can be omitted, in which case it defaults to ``common``. Replace this with e.g. ``symbian`` to create
a Symbian-specific ConE installation.

.. note::
    Currently the standalone installation is Windows-specific in the sense that only a batch file
    wrapper (``cone.cmd``) is included and some Symbian-specific plug-ins have dependencies to
    Windows applications and Python libraries with native components. However, the ``common``
    plug-in package should contain only pure Python, so it should work in Unix. Also, a ``cone.sh``
    script is available under ``source/``, which can be used to replace ``cone.cmd`` in Unix.

Install from ZIP
^^^^^^^^^^^^^^^^

Fetch the latest ConE build from our CruiseControl build server (works only in Nokia intranet):
  
* Goto https://trace1.isource-nokia.nokia.com/trac/cone/wiki/ConeReleases
* Download the release zip file from ConE releases.

The ZIP file should contain a pre-built standalone installation described in the previous section.
Simply unzip it where you please.


.. _installation-export-tests:

Standalone test set
^^^^^^^^^^^^^^^^^^^

A standalone ConE installation can be tested using an automated standalone test set, which tests the
ConE CLI functionality. Like the ``install`` command, exporting the test set also needs to
be given the plug-in package name (it wouldn't make much sense to test a Symbian ConE
installation using a Maemo-specific test set).

* Export the test set:

  * ``cd cone_src``
  * <windows> ``export_bat.cmd /path/to/tests common``
  * <linux> *Not available yet*


.. warning::
    The path specified as the target path will be cleared before the actual
    export takes place, so be sure not to pass anything like C:\\ there.

* Run the test set:
  
  * Copy the ConE installation to test into ``/path/to/tests/cone/``
  * ``cd /path/to/tests``
  * ``runtests.cmd``

You can also run the tests so that a standalone ConE installation is built and then tested
with its corresponding test set:

  * ``cd cone_src``
  * <windows> ``run_bat.cmd /path/to/tests common``
  * <linux> *Not available yet*

If you simply want to test that ConE works correctly on your machine, you can
also run:

  * ``ant test``
  
This will export the test set, install ConE and run the tests inside a temporary
build directory in the working copy.
  
Build and install debian packages (Maemo)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  1. Install tools and cone dependencies, as root or with sudo.
  
    * ``sudo apt-get install dpkg-dev fakeroot python-setuptools python-central``
    
  2. Build python-cone and cone-tool. The packages are placed in parent directory.
   
    * ``cd cone/trunk``
    * ``dpkg-buildpackage -rfakeroot -b``
    
  3. Install the binary packages, as root or with sudo.
   
    * ``sudo dpkg -i ../python-cone*.deb ../cone-tool*.deb``

  4. Install Jinja2 (not part of all Debian-based distros)

    * ``sudo easy_install Jinja2``

    
