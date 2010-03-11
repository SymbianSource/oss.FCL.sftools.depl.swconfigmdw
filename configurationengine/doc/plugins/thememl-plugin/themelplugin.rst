User guide for Theme Plugin usage in ConE
-----------------------------------------

Introduction
'''''''''''''
This page describes how to use ConE Theme plugin. Theme plugin extracts the theme content from the
.cpf file. It needs a .thememl file in the implml folder


The thememl syntax is a extension of Configuration markup language (confml). The term in confml for this extension 
is implementation method language (implml), which in thememl case is a xml file. 


Theme elements
''''''''''''''

The root element of the theme file is always thememl, which defines the xml namespace (xmlns) 
to http://www.s60.com/xml/thememl/1 in the current version. 

Theme example
^^^^^^^^^^^^^
.. literalinclude:: theme.thememl
   :language: xml




carbideuiPath
^^^^^^^^^^^^^^

To create a the Theme plugin uses makepackage.bat file which is under the forder described in
carbideuiPath tag. If none is setted the default is then C:\Program Files\Nokia\Carbide.ui Theme Edition 3.4 



themeDir
^^^^^^^^
Theme plugin available themes from this directory setted as confml ref


activeTheme 
^^^^^^^^^^^

One may describe a theme in this tag. You may have them as many as you want.
It may hold one refSetting tag and several platformUID tags 

**activeTheme attributes**

Each flag attribute can have unique hexa values.

  * uid 
  

refSetting 
^^^^^^^^^^
A ref confml setting key that describes the name of the .tpf file. Tpf file must always locate in the 
content folder


platformUID 
^^^^^^^^^^^
Is a ref in conml it may contain some value, but it will be replaced in the theme plugin to value
given by the .pkg file and setted back to configuration. You may have more than one of these 


Note 
^^^^^
The current implementation of the theme plugin relays the the .tpf file contain a .project file and 
it contains themepackage.pkg file


XSD
'''

Download: :download:`thememl.xsd </xsd/thememl.xsd>`


FAQ
'''

Makepackage error
'''''''''''''''''

This problem is related to installation on Carbide.ui you can get it form
here http://www.forum.nokia.com/info/sw.nokia.com/id/bb173537-4e67-496f-9967-50917d5cfc47/S60_Theme_Studio_for_Symbian_OS.html
Install it. Goes by default to C:\Program Files\Nokia\Carbide.ui Theme Edition 3.4, but if you install it
to a different location then you need to set right path to carbideuiPath tag. Chek that your system supports java
programmin language. OPen command line editor and type java -version should be 1.5 or above 

My theme is not created to image
''''''''''''''''''''''''''''''''

Change the .tpf file extension to zip and extract it to some folder.
View the contents, there should be .project file and themepackage.pkg file, if not
then ConE cannot create you a theme to an image. 

 


