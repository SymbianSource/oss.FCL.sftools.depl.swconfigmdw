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

import os, re, zipfile

SVN_IGNORE_PATTERN = r'(.*/|.*\\|^)\.svn(/.*|\\.*|$)'

def zip_dir(source_dir, target_file, ignore_patterns=[]):
    """
    Archive the contents of a directory into a zip file.
    """
    if not os.path.isdir(source_dir):
        raise RuntimeError("'%s' does not exist or is not a directory" % dir)

    target_dir = os.path.dirname(target_file)
    if target_dir != '' and not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    def is_ignored(entry_name):
        for pat in ignore_patterns:
            if re.match(pat, entry_name) != None:
                return True
        return False
    
    zf = zipfile.ZipFile(target_file, 'w', compression=zipfile.ZIP_DEFLATED)
    try:
        source_dir = os.path.abspath(source_dir).replace('\\', '/')
        if not source_dir.endswith('/'): source_dir += '/'
        
        empty_dirs = []
        for root, dirs, files in os.walk(source_dir):
            # Construct the ZIP entry name of the current directory
            root_dir_zip_name = root.replace('\\', '/')[len(source_dir):] + '/'
            
            if is_ignored(root_dir_zip_name):
                continue
            
            # Create a dictionary of the files that should be written to the
            # ZIP file
            filtered_files = {}
            for fname in files:
                if root_dir_zip_name == '/':    zip_name = fname
                else:                           zip_name = root_dir_zip_name + fname
                if not is_ignored(zip_name):
                    filtered_files[zip_name] = os.path.join(root, fname)
            
            # If the current directory is a sub-directory of an empty directory candidate,
            # remove the base directory from the sub-directory candidates
            empty_dirs = filter(lambda n: not root_dir_zip_name.startswith(n), empty_dirs)
            
            if len(filtered_files) == 0:
                # If there are no files, the directory is possibly an empty directory
                # (though it can still contain sub-directories that contain something)
                empty_dirs.append(root_dir_zip_name)
            else:
                for zip_name, path in filtered_files.iteritems():
                    zf.write(path, zip_name, zipfile.ZIP_DEFLATED)
            
        # Write empty directories
        for zip_name in empty_dirs:
            zf.writestr(zip_name, '')
    finally:
        zf.close()