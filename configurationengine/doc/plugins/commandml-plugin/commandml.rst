User guide for Command Plugin
-----------------------------

Introduction
'''''''''''''
This page describes how to use ConE command plugin. Command plugin is a ConE plugin, 
which purpose is to run external tools and scripts to generate files to target image.
Command plugin is configured in CommandML files that describes tools that are run 
and options that are used.

CommandML files are executed by default in **normal** :ref:`invocation phase <implml-common-invocation-phase>`.

CommandML
'''''''''

The CommandML syntax is a extension of Configuration markup language (confml). The term in confml for this extension 
is implementation method language (implml), which in CommandML case is a xml file. 

All input values can be given as ConfML refs or as plain text. Also mixing text and ConfML ref information
is supported. 

  * Namespace: ``http://www.s60.com/xml/commandml/1``
  * File extension: ``commandml``

.. note::

   More information about :ref:`file extensions <implml-file-extensions>`. 

CommandML Elements
..................

The CommandML model is drawn out as a uml model in below picture.

  .. image:: commandml.jpg

.. note::

   CommandML supports also common ImplML elements. More information about :ref:`ImplML elements <implml-common-elements>`. 

<commandml> Element
**************************

The ``commandml`` element is the root element of the configuration, and acts as a container to the rest of the elements.

Child Elements
++++++++++++++++++++++++++

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
condition             0 .. *                  Defines a group of commands that are run only if command is evaluated as True.
command               0 .. *                  Defines properties for one executable.
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

  <commandml xmlns="http://www.s60.com/xml/commandml/1">
 
<condition> Element
**************************

``Condition`` element defines a group of commands that are run only if command is evaluated as True. 


Child Elements
++++++++++++++++++++++++++

Condition can contain arbitrary number of commands and they are run in definition order so that next command is executed
only after the previous has ended.

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
command               0 .. *                  Defines properties for one executable.
====================  ======================  ===============================================================================

Attributes
++++++++++++++++++++++++++

Condition has only one attribute ``value`` which can contains any Python code and ConfML refs. Refs are first expanded
and then the value is evaluated using Python eval function.

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
value                 Yes                     Defines a condition value that can contain any Python code and ConfML refs.
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

  <condition value="${runconfig.notepad} != ''">
    <command executable="notepad.exe"/>
  </condition>
	
This will run notepad.exe only if value in ConfML ref ``runconfig.notepad`` is not empty.

<command> Element
**************************

``Command`` element defines properties for one executable. Basically it provides same features that Python subprocess 
module. Commands can be defined either inside condition elements and directly under ``commandml``. Running order of 
commands is the same that is defined in commandml file. Definition of those can be found from 
`Python subprocess documentation <http://docs.python.org/library/subprocess.html>`_.

Child Elements
++++++++++++++++++++++++++

Command element can have arguments, pipes and filters as sub-elements.

====================  ======================  ===============================================================================
Element               Cardinality             Description
====================  ======================  ===============================================================================
argument              0 .. *                  Defines argument for executable.
pipe                  0 .. *                  Defines pipe for executable.
filter                0 .. *                  Defines filter for executable.
====================  ======================  ===============================================================================


Attributes
++++++++++++++++++++++++++

Command element has one mandatory argument ``executable`` and four optional attributes: ``shell``, ``env``, ``cwd``, ``bufsize``.

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
executable            Yes                     Defines a program to execute. Value can contain any Python code and ConfML refs.
shell                 No                      Defines is the specified command executed through the shell. 
env                   No                      Defines the environment variables for the new process. 
cwd                   No                      Defines the current directory that will be changed to cwd before command is
                                              executed. Note that this directory is not considered when searching the
                                              executable, so you can't specify the program's path relative to cwd. 
bufsize               No                      Defines the pipe buffering: 0 means unbuffered, 1 means line buffered, 
                                              any other positive value means use a buffer of (approximately) that size. 
                                              A negative bufsize means to use the system default, which usually means
                                              fully buffered. The default value for bufsize is 0 (unbuffered). 
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

	<command executable="\Preinstallation\preinstallation.exe" cwd="x:\" shell="true" env="{'MYVAR':'123'}">



<argument> Element
**************************

``Argument`` element defines one command line argument for it's parent command.


Attributes
++++++++++++++++++++++++++

Value is given in attribute ``value`` and can contain any string value. When executing the command all attributes are 
combined to be a single string that is passed as a parameter to executable.

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
value                 Yes                     Defines a one command line argument for it's parent command.
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

	<argument value="-o output/content" />
	<argument value="--add-setting-file=c:\temp.txt" />
	<argument value="${preinstallmeta.product}"/>

NOTE! In CommandML localPath is handled as any other string, so don't expect the localPaths of file and folder settings
to work directly. A localPath is just a string that references files and folders under the configuration project content
(e.g. 'somedir/somefile.txt', which could physically be located under 'somelayer/content/somedir/somefile.txt').
If you need an absolute path to the actual file, you need to obtain that yourself using the ConE API. You may
also need to write the file to a temporary folder, since we might be generating from a CPF.

<pipe> Element
**************************

Pipes are used to specify executed program's standard input, output and error file handles.    

Attributes
++++++++++++++++++++++++++

``Pipe`` has two mandatory arguments ``name`` and ``value``.

====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
name                  Yes                     Defines the name of the pipe. Possible values are: "stdin", "stdout" and 
                                              "stderr". That are executed programs' standard input, standard output and 
                                              standard error file handles, respectively.
value                 Yes                     Value can be either PIPE to indicate that new should be defined or then 
                                              filename. Stderr additionally can have also value STDOUT, which indicates that 
                                              the stderr data from the applications should be captured into the same file 
                                              handle as for stdout.
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

	<pipe name="stdout" value="x:\\logia.txt"/>
	<pipe name="stderr" value="STDOUT"/>

<filter> Element
**************************

Filters are used to analyse output of executed command and report the findings to ConE log file. This enables that 
executed program's errors are easily available for users. 

Attributes
++++++++++++++++++++++++++

``Filter`` element has four attributes: ``severity``, ``condition``, ``input`` and ``formatter``.
 
====================  ======================  ===============================================================================
Attribute             Required                Description
====================  ======================  ===============================================================================
severity              Yes                     Defines logging level e.g. "info" means that possible findings are reported as
                                              info elements. Other options for severity are "warning", "debug", "exception",
                                              "error" and "critical". Default value is "info".
condition             Yes                     Defines a Python regexp pattern that is used to match lines from the 
                                              defined input pipe. Notice that you can use named groups to get some relevant 
                                              information stored for formatter use.
input                 Yes                     Input can be either "stdout" or "stderr". 
formatter             No                      Formatter defines how the findings are reported in ConE output. It is 
                                              sprintf-style string which can contain named groups from condition. If 
                                              formatter is empty found line is printed as such. See examples below.
====================  ======================  ===============================================================================

Example
++++++++++++++++++++++++++

.. code-block:: xml

	<filter severity="info" condition="\s*\'(?P&lt;name&gt;.*)\' => \'(?P&lt;uid&gt;.*)\'" input="stdout" formatter="Installed %(name)s using UID: %(uid)s"/>
	<filter severity="debug" condition=".*successfully.*" input="stdout"/>
	<filter severity="error" condition="Installation of \'(?P&lt;name&gt;.*)\' failed! See the log for details and contact Delevopment team." input="stdout" formatter="Install manually %(name)s!"/>
			
The first one defines that findings are reported as info elements. Condition element defines two named groups "name" and
"uid" which are also used in formatter when printing information to ConE's log file. 
The second one tries to find any line containing word "successfully" and prints the whole line as debug element.
The last one print all failed cases as errors and uses again named groups to extract data from input stream. 


Full example files
''''''''''''''''''

.. literalinclude:: preinstall.commandml
   :language: xml
 

XSD
'''

.. note::

   This will be added later.


FAQ
'''''''''''''

This will be updated based on the questions.
