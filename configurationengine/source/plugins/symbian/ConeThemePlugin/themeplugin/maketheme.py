#
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description: 
#

import re
import os
import sys
import logging
import xml.parsers.expat
import unzip
import shutil
import pkg_resources

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree


from cone.public import exceptions,plugin,utils,api
from themeplugin import theme_function
from theme_resource import ThemeResource
from theme_container import ThemeContainer, ActiveTheme

class ThemeImpl(plugin.ImplBase):
    """
    This class provides converting *.tpf files to target device
    
    
    Building process:
    1. All tpf files are founded in the cpf file according to "preinstalled directories" 
       and "CVC settings" which are defined in the thememl file.
       
    2. The tpf files are extracted to temporary directories. Every tpf file has self temporary directory
    
    3. *.tdf, *.svg files are builded to *.mbm, *.skn,... by using Carbide.UI command-line.
       The path of Carbide.UI is defined in the thememl file.
       
       Here is two possible cases:
         3a) The theme has defined UID number in thememl file.
             The Carbide.UI is run with parameter -uid %number%.
             Then this UID number (after converting to decimal format) is saved to
             platform setting in the step 5
    
          3b) The theme has not defined UID number
              The Carbide.UI is run without parameter -uid %number% and then
              the PID number is getted from *.pkg file and setted to platform setting in the decimal format
              in the step 5

    4. *.mbm, *.skn,... are copied to output directory according to content of the pkg file. 
       The *.pkg file contains the record where the *.mbm, *.skn,... are be copied.
       Sample: "themepackage.mbm" - "private\10207114\import\99d49b086e6097b8\themepackage.mbm"

    5. UID or PID number are saved to platform setting which is defined in the thememl file
    6. Temporary directories are removed
    """

    
    IMPL_TYPE_ID = "thememl"
    DEFAULT_INVOCATION_PHASE = 'pre'
    
    
    def __init__(self,ref,configuration):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.logger = logging.getLogger('cone.thememl')
        
    def build(self, context):
        """
        Building process of themes
        """
        # Get absolute path so that copying works correctly
        # despite working directory changing
        abs_output = os.path.abspath(os.path.join(context.output, self.output, "content"))
        
        # get *.tpf files from the configuration
        list_tpf = self.list_tpf_files(self.list_active_theme, self.list_theme_dir)
        
        theme_container = ThemeContainer(list_tpf,self.configuration)
        theme_container.carbide = self.carbide
        theme_container.create_themes()
        theme_container.prepare_active_themes(self.list_active_theme)
        theme_container.build_theme(self.theme_version)
        theme_container.copy_resources_to_output(abs_output)
        theme_container.set_active_PID_to_model()
        theme_container.removeTempDirs()
        
      

    def list_tpf_files(self,list_active_theme, list_theme_dir):
        """
        returns the list of tpf files which are in the configuration
        """
        list_tpf=[]
        default_view = self.configuration.get_default_view()
        
        for active_theme in list_active_theme:
            path=active_theme.get_setting_ref().replace("/",".")
            feature = default_view.get_feature(path+".localPath")
            setting = feature.get_data()
            if setting != None:
                list_tpf.append(setting.get_value())    
        
        for theme_dir in list_theme_dir:
            theme_dir=theme_dir.replace("/",".")
            feature = default_view.get_feature(theme_dir+".localPath")
            setting = feature.get_data()
            if setting != None:
                list_tpf.append(setting.get_value())
           

        return self.find_tpf_files(list_tpf) 

    
    def find_tpf_files(self, list_tpf_path):
        """
        finds *.tpf files in the data container
        """
        list_tpf={}
        
        datacontainer = self.configuration.layered_content()
        contentfiles = datacontainer.flatten()
        for reskey in contentfiles.keys():
            respath = contentfiles[reskey]
            
            if  respath.endswith(".tpf"):
                # Strip file name from the resource path
                respath_basename = os.path.split(respath)[0]
                
                for tpf_path in list_tpf_path:
                    # os.path.split() strips trailing slash, so do that here too

                    tpf_path = "/content/" + tpf_path 
                    if tpf_path.endswith(".tpf"):
                        if respath.endswith(tpf_path):
                            list_tpf[respath]=0
                            break
                    
                    if tpf_path.endswith('/'):
                        tpf_path = tpf_path.rstrip('/')
                    if respath_basename.endswith(tpf_path):
                        list_tpf[respath]=0
                        break

                        
                        
                        
                    
        return list_tpf.keys()    
               

    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        # Make sure autoconfig is the last layer, since theme conversion
        # may change the values of some settings
        autoconfig = plugin.get_autoconfig(self.configuration)
        
        self.build(context)
        
        # Add changed refs if necessary
        if context:
            context.add_changed_refs(autoconfig.list_leaf_datas())
        
        return 
    
    def generate_layers(self,layers):
        """
        Generate the given Configuration layers.
        """
        self.logger.info('Generating layers %s' % layers)
        self.create_output(layers)
        return 
    
    def has_ref(self,ref):
        """
        @returns True if the implementation uses the given ref as input value.
        Otherwise return False.
        """
        return None
    
    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        # What to return if the output files cannot be known in advance?
        return []
    

class ThemeImplReader(plugin.ReaderBase):
    """
    Parses a single thememl file
    """ 
    NAMESPACE = 'http://www.s60.com/xml/thememl/1'
    NAMESPACE_ID = 'thememl'
    ROOT_ELEMENT_NAME = 'thememl'
    FILE_EXTENSIONS = ['thememl']
    
    def __init__(self):
        self.namespaces = [self.NAMESPACE]
        self.list_theme_dir = []
        self.list_active_theme = []
        self.theme_version = ""
        self.logger = logging.getLogger('cone.thememl')
        self.carbide = r"C:\Program Files\Nokia\Carbide.ui Theme Edition 3.4"
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = ThemeImplReader()
        reader.parse_thememl(etree)
        
        impl = ThemeImpl(resource_ref, configuration)
        impl.list_theme_dir     = reader.list_theme_dir
        impl.list_active_theme  = reader.list_active_theme
        impl.theme_version      = reader.theme_version
        impl.carbide            = reader.carbide
        return impl
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('themeplugin', 'xsd/thememl.xsd')
    
    def fromstring(self, xml_as_string):
        etree = ElementTree.fromstring(xml_as_string)
        self.parse_thememl(etree)
         
    def parse_thememl(self,etree):
        
        list_setting_uid={}
        
        #parses the version of the theme
        el_theme_version= etree.find("{%s}themeVersion" % self.namespaces[0])
        if el_theme_version != None:
            self.theme_version = el_theme_version.text

        car= etree.find("{%s}carbideuiPath" % self.namespaces[0])
        envpattern = ".*(%(.*)%).*"
        if car != None:
            mo = re.match(envpattern, car.text)
            if mo:
                if os.environ.has_key(mo.group(2)):
                    self.carbide = car.text.replace(mo.group(1), os.environ[mo.group(2)])
                else:
                    self.carbide = car.text 
            else:
                self.carbide = car.text

        
        #parses the path of directories where are tpf files
        el_list_theme_dir = etree.findall("{%s}themeDir" % self.namespaces[0])
        for el_theme_dir in el_list_theme_dir:
            if el_theme_dir != None:
                self.list_theme_dir.append(el_theme_dir.text)
            
        #parses the active themes and theirs ref setting and platform settings
        el_list_active_theme = etree.findall("{%s}activeTheme" % self.namespaces[0])
        for el_active_theme in el_list_active_theme:
            uid = el_active_theme.get("uid")
            active_theme = ActiveTheme()
            
            active_theme.set_uid(uid)
            for el_ref_setting in  el_active_theme.getiterator("{%s}refSetting" % self.namespaces[0]):
                active_theme.set_setting_ref(el_ref_setting.text)
            
            
            for el_setting_uid in el_active_theme.getiterator("{%s}platformUID" % self.namespaces[0]): 
                setting_uid = el_setting_uid.text
                if list_setting_uid.has_key(setting_uid):
                    raise exceptions.ParseError('The file contains duplicate setting uid: %s' % setting_uid)
                else:
                    list_setting_uid[setting_uid]=0
                    active_theme.set_setting_uids(setting_uid)
            
            self.list_active_theme.append(active_theme)
