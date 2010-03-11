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

import os, shutil

def _filter_list(lst, filters):
    """
    Filter a list in-place.
    
    @param lst: The list to filter.
    @param ignore_functions: List of functions used to check whether an entry
        should be filtered or not. Each function is given a list entry and
        should return True or False.
    """
    del_entries = []
    for entry in lst:
        for func in filters:
            if func(entry):
                del_entries.append(entry)
                break
    for entry in del_entries:
        lst.remove(entry)

def copy_dir(source_dir, target_dir, dir_ignore_functions=[], file_ignore_functions=[]):
    """
    Copy a directory tree with the possibility of ignoring certain files or directories.
    
    @param source_dir: The source directory to copy.
    @param target_dir: The target directory. If the directory already exists, already
        files will be overwritten.
    @param dir_ignore_functions: List of filter functions applied on dirs.
    @param file_ignore_functions: List of filter functions applied on files.
    """
    if not os.path.exists(source_dir):
        raise RuntimeError("Source dir '%s' does not exist!!" % source_dir)
    
    source_parts_num = len(source_dir.replace('\\', '/').split('/'))
    target_parts = target_dir.replace('\\', '/').split('/')
    
    for root, dirs, files in os.walk(source_dir, topdown=True):
        _filter_list(dirs, dir_ignore_functions)
        _filter_list(files, file_ignore_functions)
        
        # Form the target root path
        current_dir_parts = root.replace('\\', '/').split('/')
        current_dir_parts = current_dir_parts[source_parts_num:]
        target_root_parts = [x for x in target_parts]
        target_root_parts.extend(current_dir_parts)
        
        # Create the target directory if necessary
        target_root = '/'.join(target_root_parts)
        if not os.path.exists(target_root):
            os.makedirs(target_root)
        elif not os.path.isdir(target_root):
            os.remove(target_root)
            os.makedirs(target_root)

        # Copy files
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)
            
            # Remove if exists
            if os.path.exists(dst_file):
                if os.path.isdir(dst_file): shutil.rmtree(dst_file)
                else:                       os.remove(dst_file)
            
            shutil.copy2(src_file, dst_file)
