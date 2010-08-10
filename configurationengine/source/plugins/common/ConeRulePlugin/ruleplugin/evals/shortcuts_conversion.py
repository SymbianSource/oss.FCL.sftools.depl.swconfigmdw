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

def get_fixed_target_path(feature, setting):
    type_ref = setting + '_type'
    type = feature.get_feature(type_ref)
    type_value = type.get_value()
    ret = ""
    if type_value == '1':
        None
    elif type_value == '2':
        icon = feature.get_feature(setting + '_icon')
        if icon != None:
            ret = get_fixed_icon_target(icon)
    else:
        None
        
    return ret

def get_fixed_icon_target(icon):
    targetPath = icon.get_feature('targetPath').get_value()
    localPath = icon.get_feature('localPath').get_value()
    target = get_target_without_extension(targetPath)
    extension = get_correct_extension(localPath)
    fixed = ""
    if extension != None:
        if len(target) > 0 and len(extension) > 0:
            fixed = target + extension
    return fixed

def get_target_without_extension(targetPath):
    (target,_) = os.path.splitext(targetPath)
    return target

def get_correct_extension(localPath):
    
    if localPath != None:
        (_,extension) = os.path.splitext(localPath)
        if extension == '.bmp':
            return '.mbm'
        elif extension == '.svg':
            return '.mif'
        else:
            return extension
    else:
        return None

def get_shortcut_string(feature, setting):
    type_ref = setting + '_type'
    type_value = feature.get_feature(type_ref).get_value()
    ret = ""
    if type_value == '1':
        app_ref = setting + '_app'
        application = feature.get_feature(app_ref).get_value()
        ret = application
    elif type_value == '2':
        url = feature.get_feature(setting+'_URL').get_value()
        title = feature.get_feature(setting+'_title').get_value()

        if title == None:
            title = ""
        else:
            title = 'customtitle=' + title
        
        icon = feature.get_feature(setting + '_icon')
        image_path = icon.get_feature('targetPath').get_value()
        
        icon_str = ""
        
        if image_path != None and image_path != "":
            icon_str = 'iconmifpath='
            if image_path.endswith('.mif'): index = '16384'
            else:                           index = '0'
            icon_str = icon_str + image_path + ';' + index + '&'
            
        ret = url + '?custom?' + icon_str + title
    return ret

#print get_shortcut_string('1', '2', '3')
#http://www.nokia2.com?custom?iconmifpath=Z:\\resource\\apps\\icon2.mbm;1&amp;customtitle=Nokia2
