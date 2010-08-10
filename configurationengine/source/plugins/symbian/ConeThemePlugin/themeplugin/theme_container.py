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

import os
import unzip
import shutil
import logging
from themeplugin import theme_function
from theme_resource import ThemeResource
from cone.storage import filestorage
from cone.public import plugin

class ThemeContainer:
    """
    This class provides extracts *.tpf files, convertts to *.mbm,*.pkg, ... files and set UID(PID)
    to the setting values in the model 
    """
    
    def __init__(self, list_tpf, configuration):
        self.list_tpf=list_tpf
        self.configuration=configuration
        self.list_theme=[]
        self.logger = logging.getLogger('cone.thememl')
        self.carbide = None

    def create_themes(self):
        """
        extractes tpf file to the temporary directory and creates Theme objects
        """

        for tpf in self.list_tpf:
            logging.getLogger('cone.thememl').info("Creating temp folder for %s" % tpf)
            theme = Theme()
            theme.set_tpf_path(tpf)
            
            temp_tdf = os.tempnam("Theme")
            os.mkdir(temp_tdf)
            temp_theme = os.path.join(temp_tdf,"__temp__")
            os.mkdir(temp_theme)
            theme.set_temp_theme(temp_theme)
            theme.set_temp_tdf(temp_tdf)

            self.list_theme.append(theme)
        

        
    def build_theme(self, theme_version):
        """
        converts *.tpf files to *.mbm, *.skn, ...
        """
        for theme in self.list_theme:
            self.make_theme(theme, theme_version)

            
    def prepare_active_themes(self,list_active_theme):
        """
        goes through the active themes and sets theme in the list of all themes as active {set the name and
        the uid number of the platform setting}
        """
        default_view = self.configuration.get_default_view()
        for active_theme in list_active_theme:
            if active_theme.get_setting_ref():
                path=active_theme.get_setting_ref().replace("/",".")
                setting = default_view.get_feature(path+".localPath").get_data()
                if setting != None and setting.get_value():
                    setting_value = setting.get_value()
                    self.set_settinguid_to_theme(active_theme,setting_value)

    def set_settinguid_to_theme(self,active_theme, path):
        """
        finds out the active theme and set the name and the uid of the platform setting
        """
        path = "/content/"+path
        for theme in self.list_theme:
            tpf_path = theme.get_tpf_path()
            
            if tpf_path.endswith(path):
                 for setting_uid in active_theme.get_setting_uids():
                    setting_uid_value = setting_uid.replace("/",".")
                    theme.set_setting_uids(setting_uid_value)
                    theme.set_uid(active_theme.get_uid())
                    
    def set_active_PID_to_model(self):
        """
        finds active theme, gets PID from pkg file, convert PID from hexadecimal to decimal formal
        and set decimal PID to the aknskins setting in the model
        """
        l = len (self.list_theme)

        
        
        for theme in self.list_theme:
            

            default_view = self.configuration.get_default_view()
            
            for setting_uid in theme.get_setting_uids():
                aknskins_setting = default_view.get_feature(setting_uid)
                if(theme.get_uid()):
                    uid = int(theme.get_uid(),16)
                    aknskins_setting.set_value(str(uid))
                else:
                    PID = theme_function.find_text_in_file(os.path.join(theme.get_temp_theme(), "themepackage.pkg"), "!:\\resource\\skins\\", "\\")
                    dec_PID = theme_function.convert_hexa_to_decimal(PID)
                    if dec_PID and aknskins_setting:
                        dec_PID = theme_function.convert_hexa_to_decimal(PID)
                        aknskins_setting.set_value(str(dec_PID))
           
    def make_theme(self, theme, theme_version):
        """
        converts the *tdf, *. svg files to *.mbm, *.pkg files, ...
        The first this method extracts tpf file and then calls carbide.ui command-line
        which converts theme.
        """
        output_path = theme.get_temp_theme()
        
        if not os.path.exists(output_path): 
            os.makedirs(output_path)
        
        storagepath = self.configuration.get_storage().get_path()

        input_path =  theme.get_tpf_path().replace("/","\\")
        
        zip_output= theme.get_temp_tdf() + "\\"
        self.unzip_tpf(theme,zip_output)
        
        name_tdf = theme_function.get_tdf_file(zip_output)
        name_tdf = os.path.join(name_tdf,name_tdf+".tdf")
        input_tdf = os.path.join(zip_output,name_tdf)
       
        command_line = "makepackage -input " + input_tdf + " -output " + output_path
        
        if len(theme_version) != 0:
            command_line = command_line + " -ver "+ theme_version
        
        if theme.get_uid() != None:
            command_line = command_line + " -uid " + theme.get_uid()
            
        logging.getLogger('cone.thememl').info("Building theme: %s" % command_line)
        current_dir = os.getcwd()
        os.chdir(self.carbide)
        os.system(command_line)
        os.chdir(current_dir)
        
        
    def unzip_tpf(self, theme, zip_output):
        """
        unzip the tpf file to output directory
        """
        f_storage = filestorage.FileStorage(theme.get_temp_tdf(), 'wb')
        list=[]
        list.append(theme.get_tpf_path())
        storage = self.configuration.get_storage()
        storage.export_resources(list, f_storage)
        
        tpf_file = os.path.join(theme.get_temp_tdf(),theme.get_tpf_path().replace("/","\\"))
        
        unzip.unzip_file_into_dir(tpf_file,zip_output)

        
    def copy_resources_to_output(self,output):
        """
        copies *.mbm, *.skn ... to respective directories in the output directory
        """
        for theme in self.list_theme:
            #gets list of path where *.mbm, *.skn, ... will be copied
            theme_resource = ThemeResource()
            theme_resource.parse_pkg_file(os.path.join(theme.get_temp_theme(), "themepackage.pkg"))
                                          
            # copies *.mbm, *.skn ... to target paths
            theme_resource.copy_files_from_theme(theme.get_temp_theme(), output)
      
        
    def removeTempDirs(self):
        """
        remove temporary directories
        """

        for theme in self.list_theme:
            shutil.rmtree(theme.get_temp_tdf())
            
class Theme:
    """
    This class has information about theme. It contains path of tpf file and temporary directories
    where the theme was extracted and builded
    Ans also it contains information about the name of setting which has value as UID. The theme 
    hasn't to have this the name of setting.
    """
    def __init__(self):
        #where the theme was extracted
        self.temp_tdf = ""
        #where the theme was builded
        self.temp_theme = ""
        #the path of tpf file
        self.tpf_path = ""
        # the name of the setting which contains UID
        self.setting_uids = []
        self.uids = []
        self.uid = None
        
    def set_tpf_path(self, tpf_path):
        self.tpf_path = tpf_path
    
    def get_tpf_path(self):
        return self.tpf_path
    
    def set_temp_tdf(self, temp_tdf):
        self.temp_tdf = temp_tdf
        
    def get_temp_tdf(self):
        return self.temp_tdf
    
    def set_temp_theme(self, temp_theme):
        self.temp_theme = temp_theme
        
    def get_temp_theme(self):
        return self.temp_theme
    
    def set_setting_uids(self, setting_uid):
        self.setting_uids.append(setting_uid)
        
    def get_setting_uids(self):
        return self.setting_uids
    
    def set_uid(self, uid):
        self.uid = uid
        
    def get_uid(self):
        return self.uid
    
class ActiveTheme(object):
    """
    This class performs information from thememl file. 
    It contains the name of settig (its value contains the path of tpf file) and
    the name of setting which contains UID
     
    """

    def __init__(self):
        self.ref_setting = None
        self.setting_uids = []
        self.uid = None
    
    def set_setting_ref(self, ref_setting):
        self.ref_setting  = ref_setting
        
    def set_setting_uids(self, setting_uid):
        self.setting_uids.append(setting_uid)
        
    def get_setting_ref(self):
        return self.ref_setting
        
    def get_setting_uids(self):
        return self.setting_uids
    
    def get_uid(self):
        return self.uid
    
    def set_uid(self,uid):
        self.uid = uid