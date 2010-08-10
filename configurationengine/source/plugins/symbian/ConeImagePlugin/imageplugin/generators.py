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
'''
Generator classes
'''


import re
import os
import logging
import subprocess
import shutil

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
from cone.public import utils

class InvalidInputFileException(RuntimeError):
    """
    Exception thrown in case of an invalid input file list.
    """
    pass

class OutputGenerator(object):
    def __init__(self,outputpath,**kwargs):
        self._configuration = None
        self._subpath = ''
        self._contentpath = ''
        self._command = ''
        self._inputs = []
        for arg in kwargs.keys():
            setattr(self, arg, kwargs[arg])
        self._outputpath = outputpath

    def __str__(self):
        return "Generator for output %s: %s"  % (self.path,self.get_command())

    def generate(self, context=None):
        command = self.get_command()
        if command:
            return command.execute()
        else:
            return 0

    def get_outputpath(self):
        """
        Get the confml ref value from configuration if the outputpath is actually a ref
        """
        if self._outputpath and ConfmlRefs.is_confml_ref(self._outputpath):
            oref = ConfmlRefs.get_confml_ref(self._outputpath)
            opath = self.configuration.get_default_view().get_feature(oref).get_value()
            if opath == None: 
                logging.getLogger('cone.imageml').warning('Output path not set.')
                return self._outputpath 
                #raise exceptions.NotBound("Output path reference has no value %s" % oref)
            (drive,opath) = os.path.splitdrive(opath)
            opath = utils.resourceref.norm(opath)
            opath = utils.resourceref.remove_begin_slash(opath)
            return opath
        else:
            return self._outputpath

    def set_outputpath(self, value): 
        self._outputpath = value

    def del_outputpath(self): 
        self._outputpath = None

    def get_subpath(self):
        return self._subpath

    def set_subpath(self, value): 
        self._subpath = value

    def del_subpath(self): 
        self._subpath = None

    def get_inputs(self): 
        return self._inputs

    def set_inputs(self, value): 
        self._inputs = value

    def del_inputs(self): 
        self._inputs = []

    def get_configuration(self): 
        return self._configuration

    def set_configuration(self, value): 
        self._configuration= value
        for input in self.inputs:
            input.configuration = self.configuration

    def del_configuration(self): 
        self._configuration= None

    @property
    def path(self):
        return utils.resourceref.join_refs([self.subpath, self.outputpath])

    def get_command(self):
        (_,ext) = os.path.splitext(self.path)
        if ext == '.mbm':
            return BmconvCommand(self)
        elif ext == '.mif':
            return MifconvCommand(self)
        elif ext == '.gif':
            return CopyCommand(self)
        else:
            return None
    
    def get_refs(self):
        refs = []
        for input in self.inputs:
            refs.extend(input.get_refs())
        return refs

    configuration = property(get_configuration, set_configuration, del_configuration)
    inputs = property(get_inputs, set_inputs, del_inputs)
    outputpath = property(get_outputpath, set_outputpath, del_outputpath)
    subpath = property(get_subpath, set_subpath, del_subpath)

class Command(object):
    def __init__(self,generator):
        self._generator = generator
        self._workdir = 'conversion_workdir'
        self._extraparams = ""
        

    def execute(self):
        """ Execute this command """
        pass

    def get_command(self, input_files):
        """ return the command as an array """
        return []

    def create_workdir(self, input_files):
        """
        Extract the necessary input files from storage to a working directory
        @param input_files: The input files (a list of InputFile objects) 
        """
        if not os.path.exists(self._workdir):
            os.makedirs(self._workdir)
        
        for file in input_files:
            self.import_to_work(file.filename)

    def clean_workdir(self):
        """
        Clean up working directory 
        """
        if os.path.exists(self._workdir):
            shutil.rmtree(self._workdir)

    def import_to_work(self,storage_filename):
        """
        Convert a storage filename to a work filename
        """
        workfile = self.workfilename(storage_filename)
        res = self._generator.configuration.get_resource(storage_filename,"rb")
        workfile = open(workfile,"wb")
        workfile.write(res.read())
        res.close()
        workfile.close()

    def workfilename(self,filename):
        """
        Convert a storage filename to a work filename
        """
        (_,workname) = os.path.split(filename)
        return os.path.join(self.workdir,workname)

    def quote_needed(self,str):
        """
        Add quotes around str if it has spaces
        """
        if str.split(' ',1) > 1:
            return '"%s"' % str
        else:
            return str
        
    @property
    def tool(self):
        return ''

    @property
    def generator(self):
        return self._generator

    @property
    def workdir(self):
        return self._workdir

    @property
    def extraparams(self):
        if self._generator.extraparams and self._generator.configuration:
            dview = self._generator.configuration.get_default_view()
            return utils.expand_refs_by_default_view(self._generator.extraparams, dview)
        else:
            return self._generator.extraparams or ''
    
    def _get_filtered_input_files(self):
        """
        Get the list of InputFile objects and with ignored
        (optional empty or invalid files) entries filtered out.
        
        Raise InvalidInputFileException if the input file list is invalid.
        """
        # Get all input files
        input_files = []
        for input in self.generator.inputs:
            input_files.extend(input.files)
        
        # Check if all are empty
        all_empty = True
        for file in input_files:
            if not file.is_empty():
                all_empty = False
                break
        if all_empty:
            return []
        
        # Create the filtered list
        result = []
        for file in input_files:
            if file.is_empty():
                if file.is_optional():
                    # Optional file is empty: no error
                    pass
                else:
                    raise InvalidInputFileException("Input file empty but not optional")
            else:
                if not file.is_valid():
                    raise InvalidInputFileException("Invalid input file: '%s'" % file.path)
                else:
                    result.append(file)
        return result 

class BmconvCommand(Command):
    def __init__(self,generator):
        super(BmconvCommand, self).__init__(generator)

    def execute(self):
        """
        Execute the command in the current working directory
        """
        input_files = self._get_filtered_input_files()
        if len(input_files) == 0: return 0
        self.create_workdir(input_files)
        
        opath = self.generator.path
        odir = os.path.dirname(opath)
        if odir and not os.path.exists(odir):
            os.makedirs(odir)
        
        command = self.get_command(input_files)
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        
        # Wait for the process to return
        out, err = [ e.splitlines() for e in p.communicate() ]
        for outl in out:
            if outl not in err:
                logging.getLogger('cone.bmconv').info(outl)
        for outl in err:
            logging.getLogger('cone.bmconv').error(outl)
        if p.returncode != 0:
            logging.getLogger('cone.bmconv').error("Command returned with returncode %s: %s" % (p.returncode, ' '.join(command)))
        else:
            logging.getLogger('cone.bmconv').info("Command returned with returncode %s: %s" % (p.returncode, ' '.join(command)))
        if p.returncode == 0:
            self.clean_workdir()
        return p.returncode 

    def get_command(self, input_files):
        command = [self.tool]
        
        """ Add extraparams """
        if hasattr(self._generator,'extraparams'):
            command.append(self.extraparams)
        
        """ Add palette file """
        if hasattr(self._generator,'palette'):
            command.append('/p%s' % os.path.abspath(self.generator.palette))
        
        """ Add output file """
        """ Add output file as compressed if needed """
        if self.rom:
            if self.compress:
                command.append('/s')
            else:
                command.append('/r')
        else:
            pass
        command.append(os.path.normpath(self.generator.path))
        
        
        for inputfile in input_files:
            depth = ''
            if inputfile.depth:
                depth = '/%s' % inputfile.depth
            command.append('%s%s' % (depth,self.workfilename(inputfile.filename)))
        return command

    @property
    def tool(self):
        if hasattr(self._generator,'tool'):
            return os.path.abspath(self._generator.tool)
        elif hasattr(self._generator, 'tooldir'):
            return os.path.abspath(os.path.join(self._generator.tooldir, 'bmconv'))
        else:
            return 'bmconv'

    @property
    def rom(self):
        if hasattr(self._generator,'rom') and self._generator.rom.lower() == 'true':
            return True
        else:
            return False

    @property
    def compress(self):
        if hasattr(self._generator,'compress') and self._generator.compress.lower() == 'true':
            return True
        else:
            return False

class MifconvCommand(Command):
    def __init__(self,generator):
        super(MifconvCommand, self).__init__(generator)

    def execute(self):
        """
        Execute the command in the current working directory
        """
        input_files = self._get_filtered_input_files()
        if len(input_files) == 0: return 0
        self.create_workdir(input_files)
        
        runenv = None
        runshell = True
        if os.path.dirname(self.tool):
            runenv = {}
            runenv['path'] = os.path.dirname(self.tool)
            runshell = True
        if not os.path.exists(os.path.dirname(self.generator.path)):
            os.makedirs(os.path.dirname(self.generator.path))
        
        command = self.get_command(input_files)
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=runenv,
                             shell=runshell)
        
        # Wait for the process to return
        out, err = [ e.splitlines() for e in p.communicate() ]
        for outl in out:
            if outl not in err:
                logging.getLogger('cone.mifconv').info(outl)
        for outl in err:
            logging.getLogger('cone.mifconv').error(outl)
        if p.returncode != 0:
            logging.getLogger('cone.mifconv').error("Command returned with returncode %s: %s" % (p.returncode, ' '.join(command)))
        else:
            logging.getLogger('cone.mifconv').info("Command returned with returncode %s: %s" % (p.returncode, ' '.join(command)))
        if p.returncode == 0:
            self.clean_workdir()
        return p.returncode 

    def get_command(self, input_files):
        command = [self.tool]
        
        """ Add output file """
        command.append(os.path.normpath(self.generator.path))
        
        """ Add extraparams """
        if hasattr(self._generator,'extraparams'):
            command.append(self.extraparams)
        
        """ Add temp_path """
        command.append("/t%s" % self.temppath)
        
        # Add tool directory if given
        if hasattr(self._generator,'tooldir'):
            command.append('/S%s' % os.path.abspath(self.generator.tooldir))
        
        """ Get input files """
        for inputfile in input_files:
            depth = 'c8'
            if inputfile.depth:
                depth = inputfile.depth
            command.append('/%s' % depth)
            command.append( '%s' % self.workfilename(inputfile.filename))
        return command

    @property
    def tool(self):
        if hasattr(self._generator,'tool'):
            return os.path.abspath(self._generator.tool)
        elif hasattr(self._generator, 'tooldir'):
            return os.path.abspath(os.path.join(self._generator.tooldir, 'mifconv'))
        else:
            return 'mifconv'

    @property
    def temppath(self):
        if hasattr(self._generator,'temp'):
            return os.path.abspath(self._generator.temp)
        else:
            return self.workdir

class CopyCommand(object):
    def __init__(self,generator):
        self._generator = generator

    def execute(self):
        pass

    @property
    def tool(self):
        return 'copy'

class InputFile(object):
    def __init__(self,path,**kwargs):
        self.configuration = None
        self._depth = None
        for arg in kwargs.keys():
            if arg == 'depth':
                # Special handling for depth ('depth' is a property that
                # expands refs using '_depth' as the base)
                self._depth = kwargs[arg]
            else:
                setattr(self, arg, kwargs[arg])
        self._path= path

    def get_input(self): 
        """ 
        Get the confml ref value from configuration if the outputpath is actually a ref 
        """
        if self._path and self.configuration is not None:
            dview = self.configuration.get_default_view()
            def expand(ref, index):
                value = dview.get_feature(ref).get_original_value()
                if value is None:   return ''
                else:               return value
            return utils.expand_delimited_tokens(self._path, expand)
        else:
            return self._path

    def set_input(self, value): self._path = value

    def del_input(self): self._path = None

    @property 
    def type(self):
        return 'file'
    
    @property
    def depth(self):
        if self._depth and self.configuration:
            dview = self.configuration.get_default_view()
            return utils.expand_refs_by_default_view(self._depth, dview)
        else:
            return self._depth or ''

    @property 
    def files(self):
        """ 
        Return a list of file names 
        """
        return [self]
        
    @property 
    def filename(self):
        """ 
        Return a the path to the layer specific filename
        """ 
        if self.configuration and self.path:
            content = self.configuration.layered_content().flatten()
            inputpath = self.path
            return content.get(inputpath)
        else:
            return self.path

    path = property(get_input, set_input, del_input, "The input 'path'.")
    
    def is_valid(self):
        """
        Return whether the input file is valid (not empty
        and exists in project content).
        """
        return not self.is_empty() and self.filename
    
    def is_empty(self):
        """
        Return whether the input file is empty.
        """
        return self.path in ('', None)
    
    def is_optional(self):
        """
        Return whether the input file is optional.
        """
        return hasattr(self, 'optional') \
            and self.optional.lower() in ('1', 't', 'true', 'yes', 'y')
    
    def get_refs(self):
        return utils.extract_delimited_tokens(self._path)
    
    def __repr__(self):
        return "InputFile(path=%r, optional=%r)" % (self._path, self.is_optional())

class InputDir(InputFile):
    def __init__(self,path,**kwargs):
        super(InputDir,self).__init__(path,**kwargs)
        self._files = []
        self._include = None
        self._exclude = None

    def get_include(self): 
        return self._include.get('pattern',[])

    def set_include(self, value): 
        self._include = value

    def del_include(self): 
        self._include = None

    def get_exclude(self):
        return self._exclude.get('pattern',[])

    def set_exclude(self, value): 
        self._exclude = value

    def del_exclude(self): 
        self._exclude = None

    @property 
    def type(self): 
        return 'dir'

    @property 
    def files(self):
        """ 
        Return a list of file names under this directory definition
        """ 
        if self.configuration:
            inputlist = []
            content = self.configuration.layered_content().flatten()
            contentfiles = content.keys()
            
            folderfiles = utils.resourceref.filter_resources(contentfiles, "^%s" % self.path)
            for inputfilter in self.include:
                folderfiles = utils.resourceref.filter_resources(folderfiles, inputfilter)
            for excludefilter in self.exclude:
                folderfiles = utils.resourceref.neg_filter_resources(folderfiles, excludefilter)
            folderfiles.sort()
            for filename in folderfiles:
                inputlist.append(InputFile(filename, **self.__dict__))
            return inputlist
        else:
            return []

    include = property(get_include, set_include, del_include)
    exclude = property(get_exclude, set_exclude, del_exclude)



class ConfmlRefs(object):
    
    ref_pattern = re.compile('^\$\{(.*)\}$')

    @classmethod
    def is_confml_ref(cls, variableref):
        """
        
        Returns true if the given variable ref is a confml reference
        """
        return cls.ref_pattern.match(variableref) != None

    @classmethod
    def get_confml_ref(cls, variableref):
        """
        
        Returns true if the given variable ref is a confml reference
        """
        matchref = cls.ref_pattern.match(variableref)
        if matchref:
            return matchref.group(1)
        else:
            return None
