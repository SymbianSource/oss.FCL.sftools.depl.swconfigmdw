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

import sys, os, re, unittest, shutil, zipfile, filecmp, subprocess

class BaseTestCase(unittest.TestCase):
    def set_modification_reference_time(self, path):
        """
        Set modification reference time for a subsequent call to assert_modified()
        or assert_not_modified().
        @param path: The path to use, can be a file or a directory.
        """
        if not hasattr(self, '_mod_refs'):
            self._mod_refs = {}
        
        if os.path.isdir(path):
            self._mod_refs[path] = self._get_dir_modtime_dict(path)
        elif os.path.isfile(path):
            self._mod_refs[path] = os.stat(path).st_mtime
        else:
            self.fail("'%s' does not exist" % path)
    
    def assert_modified(self, path):
        """
        Assert that a given file or directory has been modified since the last
        call to set_modification_reference_time() with the same path.
        """
        self._assert_modification(path, assert_not_modified=False)
    
    def assert_not_modified(self, path):
        """
        Assert that a given file or directory has NOT been modified since the last
        call to set_modification_reference_time() with the same path.
        """
        self._assert_modification(path, assert_not_modified=True)
    
    def remove_if_exists(self, path_or_paths):
        """Remove files or directories if they exist.
        @param path_or_paths: The path to remove. Can also be a list of paths."""
        if isinstance(path_or_paths, list):
            paths = path_or_paths
        else:
            paths = [path_or_paths]
        
        for path in paths:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
    
    def create_dir(self, path):
        """Create the given directory if it doesn't exist."""
        if not os.path.exists(path):
            os.makedirs(path)
    
    def recreate_dir(self, path):
        """Remove the given directory if it exists, and recreate it."""
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    
    def create_dir_for_file_path(self, path):
        """Create the directories for the given file"""
        dir = os.path.dirname(path)
        if dir != '' and not os.path.exists(dir):
            os.makedirs(dir)
    
    def assert_exists_and_contains_something(self, path):
        """
        Assert that the given path is a file or a directory and contains some data.
        """
        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                self.fail("Path '%s' exists (is a directory) but does not contain anything)" % path)
        elif os.path.isfile(path):
            if os.stat(path).st_size == 0:
                self.fail("Path '%s' exists (is a file) but does not contain anything)" % path)
        else:
            self.fail("Path '%s' does not exist" % path)
    
    def assert_dir_contents_equal(self, dir1, dir2, ignore=[], custom_comparison_functions={}, current_root_dir=''):
        """
        Assert recursively that the contents of two directories are equal.
        @param ignore: List containing names that should be ignored in the comparison (e.g. '.svn').
            The entries can either be relative, e.g. 'file.txt', which would ignore 'file.txt'
            in any directory, or they can be absolute, e.g. '/some/dir/file.txt', which would
            ignore 'file.txt' only under 'some/dir/', relative to the comparison root.
        @param custom_comparison_functions: Dictionary containing custom comparison functions
            for files. Each entry in the dict should contain the following contents:
                Key: The relative path of the file under the directories, e.g.
                    'some/path/file.txt'
                Value: The function used to compare the file contents. The function should
                    take as parameters the raw binary data of the files, and should return
                    True if the contents are equal.
        @param current_root_dir: For internal use.
        """
        msg = "Directory contents are not equal ('%s' vs. '%s')\n" % (dir1, dir2)
        
        ignore_list = []
        for entry in ignore:
            if entry.startswith('/'):
                dirname, entryname = entry.rsplit('/', 1)
                dirname = dirname.lstrip('/')
                #print "dirname = %r" % dirname
                #print "entryname = %r" % entryname
                #print "current_root_dir = %r" % current_root_dir
                if dirname == current_root_dir.rstrip('/'):
                    ignore_list.append(entryname)
            else:
                ignore_list.append(entry)

        # Compare files with the custom comparison functions if necessary
        for path, func in custom_comparison_functions.iteritems():
            dirname  = os.path.dirname(path).replace('\\', '/')
            filename = os.path.basename(path)
            
            filepath1 = os.path.join(dir1, filename)
            filepath2 = os.path.join(dir2, filename)
            
            # Compare if the file is in the current path and they both exist
            if dirname == current_root_dir and \
                os.path.isfile(filepath1) and \
                os.path.isfile(filepath2):
                comp_result = func(
                    self.read_data_from_file(filepath1),
                    self.read_data_from_file(filepath2))
                if not comp_result:
                    # The files are not equal -> fail
                    self.fail(msg + "File '%s' differs" % filename)
                else:
                    # The files are equal -> ignore from dircmp comparison
                    ignore_list.append(filename)
        
        dcmp = filecmp.dircmp(dir1, dir2, ignore=ignore_list)
        self.assertEquals(0, len(dcmp.left_only), msg + "Files only on left: %s" % dcmp.left_only)
        self.assertEquals(0, len(dcmp.right_only), msg + "Files only on right: %s" % dcmp.right_only)
        self.assertEquals(0, len(dcmp.diff_files), msg + "Differing files: %s" % dcmp.diff_files)
        self.assertEquals(0, len(dcmp.funny_files), msg + "Funny files: %s" % dcmp.funny_files)
        # Recurse into sub-directories
        for d in dcmp.common_dirs:
            if current_root_dir:    cr = current_root_dir + '/' + d
            else:                   cr = d
            self.assert_dir_contents_equal(
                os.path.join(dir1, d), os.path.join(dir2, d),
                ignore, custom_comparison_functions, cr)
    
    def assert_file_contents_equal(self, file1, file2, ignore_patterns=[]):
        """
        Assert the the given two files exist and their contents are equal.
        @param ignore_patterns: List of regular expressions for portions of the
            file content to ignore in the comparison. The ignored parts are
            deleted from the files before actual comparison.
        """
        self.assertTrue(os.path.exists(file1), "File '%s' does not exist!" % file1)
        self.assertTrue(os.path.exists(file2), "File '%s' does not exist!" % file2)
        
        data1 = self.read_data_from_file(file1)
        data2 = self.read_data_from_file(file2)
        
        def remove_ignored(data, pattern_list):
            for i, pattern in enumerate(pattern_list):
                data = re.sub(pattern, '{{{ignore_%d}}}' % i, data)
            return data
        data1 = remove_ignored(data1, ignore_patterns)
        data2 = remove_ignored(data2, ignore_patterns)
        
        if data1 != data2:
            if len(ignore_patterns) > 0:
                self.write_data_to_file(file1 + '.comparetemp', data1)
                self.write_data_to_file(file2 + '.comparetemp', data2)
                self.fail("Data of the files '%s' and '%s' are not equal\nSee *.comparetemp files for the actual data that was compared." % (file1, file2))
            else:
                self.fail("Data of the files '%s' and '%s' are not equal" % (file1, file2))
    
    def assert_file_content_equals(self, filepath, expected_data):
        """
        Assert that the content of the given file is equals to the given expected data.
        """
        self.assertTrue(os.path.exists(filepath), "'%s' does not exist!" % filepath)
        self.assertTrue(os.path.isfile(filepath), "'%s' is not a file!" % filepath)
        
        f = open(filepath, "rb")
        try:        filedata = f.read()
        finally:    f.close()
        
        if filedata != expected_data:
            msg = ("The content of the file '%s' is not what was expected!\n" % filepath) +\
                  ("Expected: %r\nActual: %r" % (expected_data, filedata))
            self.fail(msg)
    
    def assert_file_contains(self, filepath, data, encoding=None):
        """
        Assert that the given file contains the given text somewhere in its contents.
        @param filepath: Path to the file to check.
        @param data: The data the file is expected to contain.
        @param encoding: Encoding used to decode the contents of the file.
            If None, noe decoding is done.
        """
        self.assertTrue(os.path.exists(filepath), "'%s' does not exist!" % filepath)
        self.assertTrue(os.path.isfile(filepath), "'%s' is not a file!" % filepath)
        
        f = open(filepath, "rb")
        try:        filedata = f.read()
        finally:    f.close()
        
        if encoding is not None:
            filedata = filedata.decode(encoding)
        
        if not isinstance(data, list):
            data = [data]
        
        for entry in data:
            if not filedata.find(entry) != -1:
                self.fail("The file '%s' does not contain the data '%s'" % (filepath, entry))

    def assert_file_does_not_contain(self, filepath, data, encoding=None):
        """
        Assert that the given file doesn't contain the given text somewhere in its contents.
        @param filepath: Path to the file to check.
        @param data: The data the file is expected to not contain.
        @param encoding: Encoding used to decode the contents of the file.
            If None, noe decoding is done.
        """
        self.assertTrue(os.path.exists(filepath), "'%s' does not exist!" % filepath)
        self.assertTrue(os.path.isfile(filepath), "'%s' is not a file!" % filepath)
        
        f = open(filepath, "rb")
        try:        filedata = f.read()
        finally:    f.close()
        
        if encoding is not None:
            filedata = filedata.decode(encoding)
        
        if not isinstance(data, list):
            data = [data]
        
        for entry in data:
            if not filedata.find(entry) == -1:
                self.fail("The file '%s' contains the data '%s'" % (filepath, entry))
    
    def read_data_from_file(self, path):
        """Read the raw binary data from the given file."""
        f = open(path, "rb")
        try:        return f.read()
        finally:    f.close()
    
    def read_data_from_zip_file(self, path, entry):
        """Read the raw binary data from the given ZIP file with the given ZIP entry."""
        zf = zipfile.ZipFile(path, "r")
        try:        return zf.read(entry)
        finally:    zf.close()
    
    def write_data_to_file(self, path, data):
        """Write raw binary data into the given file."""
        f = open(path, "wb")
        try:        f.write(data)
        finally:    f.close()
    
    def run_command(self, command, expected_return_code=0):
        """
        Run the given command, asserting that it returns the expected value.
        @param command: The command to run.
        @param expected_return_code: The expected return code. Can be None if the return
            code doesn't matter.
        @return: The command output.
        """
        # Using shell=True on windows uses
        #    cmd.exe /c <command>
        # to run the actual command, and if cmd.exe sees that the first
        # character in the command is ", it strips that and a trailing ".
        # For this reason we add quotes to the command to prevent e.g.
        #   "C:\some\command.cmd" --some-arg "xyz"
        # from becoming
        #   C:\some\command.cmd" --some-arg "xyz
        if sys.platform == 'win32' and command.startswith('"'):
            command = '"' + command + '"'
        
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        out, err = p.communicate()
        if expected_return_code is not None:
            self.assertTrue(p.returncode == expected_return_code,
                            "Could not execute command (%s)\n"\
                            "Return code is not what was expected (expected %d, got %d)\n"\
                            "Output: \n%s" % (command, expected_return_code, p.returncode, out))
        return out
    
    # =====================================================
    # Private helper methods
    # =====================================================
    
    def _get_dir_modtime_dict(self, dir_path):
        """
        Return a dictionary of all files and directories and their last
        modification times in a given directory.
        """
        refdict = {}
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                path = os.path.join(root, f)
                refdict[path] = os.stat(path).st_mtime
            for d in dirs:
                path = os.path.join(root, d)
                refdict[path] = os.stat(path).st_mtime
        return refdict
    
    def _assert_modification(self, path, assert_not_modified=True):
        if os.path.isdir(path):
            if assert_not_modified:
                self._assert_dir_not_modified(path)
            else:
                self.assert_dir_modified(path)
        elif os.path.isfile(path):
            if assert_not_modified:
                self._assert_file_not_modified(path)
            else:
                self._assert_file_modified(path)
        else:
            self.fail("'%s' does not exist" % path)
    
    def _assert_dir_not_modified(self, dir_path):
        refdict = self._mod_refs[dir_path]
        curdict = self._get_dir_modtime_dict(dir_path)
        
        # If the keys of the dicts are not the same, the contents of the
        # dir have been modified (added or removed files/subdirs)
        self.assertEquals(curdict.keys(), refdict.keys())
        
        # Compare manually so that assertion error output shows the specific file/dir
        for path in curdict.iterkeys():
            self.assertEquals(curdict[path], refdict[path], "File or dir '%s' modified" % path)
    
    def assert_dir_modified(self, dir_path):
        refdict = self._mod_refs[dir_path]
        curdict = self._get_dir_modtime_dict(dir_path)
        
        self.assertNotEqual(curdict, refdict, "Directory '%s' has not been modified when it was expected to be" % dir_path)
    
    def _assert_file_not_modified(self, file_path):
        time1 = self._mod_refs[file_path]
        time2 = os.stat(file_path).st_mtime
        self.assertEquals(time1, time2,
            ("File '%s' was modified when it should not have been "+\
            "(mod time %f vs. %f)") % (file_path, time1, time2))
    
    def _assert_file_modified(self, file_path):
        time1 = self._mod_refs[file_path]
        time2 = os.stat(file_path).st_mtime
        self.assertNotEqual(time1, time2,
            ("File '%s' was modified not when it should have been "+\
            "(mod time %f vs. %f)") % (file_path, time1, time2))
