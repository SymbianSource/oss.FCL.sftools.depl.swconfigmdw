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
## 
# @author <author>
'''
ConE plugin to run external applications/tools with given parameters in .commandml file. Notice that values can be also
fecthed from ConfML to maximize portability and minimize maintenance.
'''

import re
import os
import logging
import types
import pkg_resources

import subprocess

from cone.public import plugin,utils

def get_folder_set(folder):
    """
    Get a set object containing all files of given folder
    @param folder: the folder to create set for
    @return: a python set 
    """
    fileset = set()
    for (root, _, filenames) in os.walk(folder):
        for filename in filenames:
            fname = utils.relpath(os.path.join(root,filename), folder)
            fileset.add(fname)
    
    return fileset

class CommandImpl(plugin.ImplBase):
    """
    Plugin implementation class. 
    """
    
    IMPL_TYPE_ID = "commandml"
    
    
    def __init__(self,ref,configuration, reader):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)###3
        self.desc = ""
        self.logger = logging.getLogger('cone.commandml(%s)' % self.ref)
        self.reader = reader
        for element in self.reader.elements:
            element.set_logger(self.logger)
        

    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        
        self.create_output(context)
        return 
    
    def generate_layers(self,layers):
        """
        Generate the given Configuration layers.
        """
        self.logger.info('Generating layers %s' % layers)
        self.create_output(layers)
        return 
    
    def create_output(self, context, layers=None):
        """
        Function to generate output files.
        """
        self.context = context
        tmpDict = self.__create_helper_variables()
        # Get the contents of output folder before the generation
        outset_before = get_folder_set(context.output)
        for element in self.reader.elements:
            #Element can be either command or condition.
            element.set_logger(self.logger)
            element.execute(context, tmpDict)        
        
        # Get the contents of output folder after the generation 
        # and get the new files created by the set difference.
        # NOTE! this does not recognize files outside output folder!
        outset_after = get_folder_set(context.output)
        outset = outset_after - outset_before
        for outfile in outset:
            context.add_file(outfile, implementation=self)
        return

    def __create_helper_variables(self):
        """
        Internal function to create dictionary containing most often used ConE "environment" variables.
        """        
        tmp = {}
        tmp["%CONE_OUT%"] = os.path.join(self.context.output, self.output).rstrip('\\')
        tmp["%CONE_OUT_ABSOLUTE%"] = os.path.abspath(os.path.join(self.context.output, self.output)).rstrip('\\')
        return tmp    
    
    def has_ref(self, refs):
        """
        @returns True if the implementation uses the given ref as input value.
        Otherwise return False.
        """
                
        # return true for now so that content copying is not filtered 
        return None
    
class CommandImplReader(plugin.ReaderBase):
    """
    Parses a single commandml file
    """ 
    NAMESPACE = 'http://www.s60.com/xml/commandml/1'
    NAMESPACE_ID = 'commandml'
    ROOT_ELEMENT_NAME = 'commandml'
    FILE_EXTENSIONS = ['commandml']
    
    def __init__(self):
        """
        Constructor
        """
        self.output_dir = None
        self.input_dir = None
        self.namespaces = [self.NAMESPACE]
        self.dview = None
        self.elements = []
        self.tags = None
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = CommandImplReader()
        reader.set_default_view(configuration.get_default_view())
        reader.from_etree(etree)
        impl = CommandImpl(resource_ref, configuration, reader)
        if reader.tags:
            impl.set_tags(reader.tags)
        return impl
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('commandplugin', 'xsd/commandml.xsd')
    
    def set_default_view(self, dview):
        """
        Function to set default view that is needed when solving out ConfML reference information
        """        
        self.dview = dview
            
    def from_etree(self, etree):
        """
        Parser function for commandml element.
        """
        self.parse_tree(etree)

    def parse_tree(self, etree):
        """
        General parse function for condition and command elements.
        """        
        elements = list(etree)
        for element in elements:
            if element.tag == "{%s}condition" % self.namespaces[0]:
                self.elements.append(self.parse_condition(element))
            elif element.tag == "{%s}command" % self.namespaces[0]:
                self.elements.append(self.parse_command(element))
            else:
                pass
        self.tags = self.parse_tags(etree)

    def parse_condition(self, etree):
        """
        Parse function for condition element.
        """        
        condition = Condition()
        condition.set_condition(etree.get("value"))
        condition.set_commands(self.parse_commands(etree))
        condition.set_default_view(self.dview)
        return condition                                   
        
    def parse_commands(self,etree):
        """
        Parser function for commands.
        """
        commands = []
        for com_elem in etree.findall("{%s}command" % self.namespaces[0]):
            commands.append(self.parse_command(com_elem))
        return commands
         
    def parse_command(self,etree):
        """
        Parser function for single command.
        """
        cmd = Command()
        cmd.set_executable(etree.get("executable"))
        cmd.set_shell(etree.get("shell"))
        cmd.set_bufsize(etree.get("bufsize"))
        cmd.set_cwd(etree.get("cwd")) 
        cmd.set_all_envs(etree.get("env"))
        cmd.set_all_arguments(self.parse_arguments(etree))
        cmd.set_all_pipes(self.parse_pipes(etree))
        cmd.set_filters(self.parse_filters(etree))
        cmd.set_default_view(self.dview)
        return cmd
    
    def parse_arguments(self,etree):
        """
        Parser function for command's arguments.
        """
        arguments = []
        for argument in etree.findall("{%s}argument" % self.namespaces[0]):
            value = argument.get("value")
            if value:
                arguments.append(value)
        return arguments
    
    def parse_pipes(self,etree):
        """
        Parser function for command's pipes.
        """
        pipes = {}
        for argument in etree.findall("{%s}pipe" % self.namespaces[0]):
            name = argument.get("name")
            value = argument.get("value")
            if name:
                pipes[name] = value        
        return pipes

    def parse_filters(self,etree):
        """
        Parser function for command's filters.
        """
        filters = []
        for argument in etree.findall("{%s}filter" % self.namespaces[0]):
            f = Filter()
            f.set_severity(argument.get("severity"))
            f.set_condition(argument.get("condition"))
            f.set_input(argument.get("input"))
            f.set_formatter(argument.get("formatter"))
            filters.append(f)
        return filters
    
    def parse_tags(self,etree):
        tags = {}
        for tag in etree.getiterator("{%s}tag" % self.namespaces[0]):
            tagname = tag.get('name','')
            tagvalue = tag.get('value')
            values = tags.get(tagname,[])
            values.append(tagvalue)
            tags[tagname] = values
        return tags


class Condition(object):
    """
    Condition class is a simple wrapper class for commands so that commands are executed
    only if condition is True. Otherwise class does nothing. Class has similar interface 
    than Command class so that they can be used similar way from plugin perspective. 
    """
    
    def __init__(self):
        self.condition = None
        self.commands = []
        self.logger = None
        self.dview = None

    def set_condition(self, condition):
        self.condition = condition

    def set_default_view(self, dview):
        self.dview = dview

    def set_commands(self, commands):
        self.commands = commands

    def set_logger(self, logger):
        self.logger = logger
        for cmd in self.commands:
            cmd.set_logger(logger)        

    def add_command(self, command):
        self.commands.append(command)

    def execute(self, context, replaceDict=None):
        if self._solve_condition(self.condition, context):
            #Condition is true -> running command
            for command in self.commands:                
                command.execute(context, replaceDict)
        else:
            self.logger.info("Ignoring %s because it is evaluated as False." % self.condition)

    def _solve_condition(self, condition_str, context):
        """
        Internal function to handle condition
        """
        if condition_str != "":
            #Expanding ConfML information
            modstr = utils.expand_delimited_tokens(
                condition_str,
                lambda ref, index: repr(context.configuration.get_default_view().get_feature(ref).get_value()))
            return eval(modstr)
        else:
            #Empty condition is true always.
            return True

class Command(object):
    """
    Command is a class that executes actual commands. It provides ways to handle input, output and error 
    streams and to control execution parameters.
    """
        
    def __init__(self):
        """
        Constructor
        """        
        self.executable = None
        self.shell = False
        self.bufsize = 0
        self.cwd = None
        self.envs = None
        self.arguments = []
        self.pipes = {}
        self.streams = {}
        self.filters = []
        self.logger = None
        self.dview = None
    
    def set_executable(self, executable):
        self.executable = executable
    
    def set_shell(self, shell):
        if shell and shell.lower() in ('true', 'yes', '1', 1, True):
            self.shell = True
        else:
            self.shell = False
        
    def set_bufsize(self, bufsize):
        if bufsize:
            self.bufsize = int(bufsize)
    
    def set_cwd(self, cwd):
        self.cwd = cwd
    
    def set_all_envs(self, envs):
        self.envs = envs
    def set_default_view(self, dview):
        self.dview = dview
        
    def set_env(self, name, value):
        self.envs[name] = value
    
    def set_all_arguments(self, args):
        self.arguments = args
    
    def get_arguments_string(self):
        """
        Function to return arguments as a string
        """
        arg_string = ""        
        for value in self.arguments:            
            arg_string += value
            arg_string += " "                
        return arg_string
    
    def get_pipe(self, name, mode='w'):
        """
        Function to return pipe based on the pipe name in requested mode.
        """
        if self.pipes.has_key(name) and isinstance(self.pipes[name], types.IntType):
        #Subprocess pipe
            return self.pipes[name]
        elif self.pipes.has_key(name) and isinstance(self.pipes[name], types.StringType):            
            return file(self.pipes[name], mode)
        else:
            return None
    
    def set_streams(self, stdin, stdout, stderr):
        self.streams["stdin"] = stdin
        self.streams["stdout"] = stdout
        self.streams["stderr"] = stderr
                        
    def get_streams(self, name, mode="r"):
        if self.streams.has_key(name) and self.streams[name]:
        #OK for streams set with subprocess.PIPE
            return self.streams[name]
        else:
        #For file objects
            return self.get_pipe(name, mode)
    
    def set_filters(self, filters):
        self.filters = filters
        for f in self.filters:
            f.set_command(self)
    
    def get_filters(self):
        return self.filters
        
    def set_argument(self, value):
        self.arguments.append(value)
    
    def set_all_pipes(self, pipes):
        for pipe in pipes.keys():
            self.set_pipe(pipe, pipes[pipe])
        
    def set_pipe(self, name, value):
        if value == "PIPE":
            #Creating new stream for this.
            self.pipes[name] = subprocess.PIPE
        elif value == "STDOUT":
            self.pipes[name] = subprocess.STDOUT
        else:
            #Setting filename
            self.pipes[name] = value
            #self.pipes[name] = file(value, 'w')
            
    def handle_filters(self):
        """
        """
        for filter in self.filters:
            filter.report(self.logger)

    def execute(self, context, replaceDict=None):
        self.dview = context.configuration.get_default_view()
        
        self.solve_refs()
        
        try:
            if self.envs:   env_dict = eval(self.envs)
            else:           env_dict = None
        except Exception, e:
            raise RuntimeError("Failed to evaluate env dictionary: %s: %s" % (e.__class__.__name__, e))
        
        exit_code = 0
        try:
            try:
                if self.cwd is not None:
                    cwd = self.__replace_helper_variables(self.cwd, replaceDict)
                else:
                    cwd = self.cwd
                command_str = self.executable + " " + self.__replace_helper_variables(self.get_arguments_string(), replaceDict)
                self.logger.info("Running command: \"%s\"" % command_str)
                self.logger.info("with args: shell=%s envs=%s cwd=%s bufsize=%s stdin=%s stdout=%s stderr=%s" \
                                 % (self.shell, self.envs, cwd, self.bufsize, \
                                    self.get_pipe("stdin", 'r'),self.get_pipe("stdout"), self.get_pipe("stderr")))
                pid = subprocess.Popen(command_str, shell=self.shell, env=env_dict, cwd=cwd,\
                                          bufsize=self.bufsize, stdin = self.get_pipe("stdin", 'r'),\
                                          stdout = self.get_pipe("stdout"), stderr = self.get_pipe("stderr"))
                #Waiting for process to complete
                retcode = pid.wait()
                #Storing stream information for possible further processing.
                self.set_streams(pid.stdin, pid.stdout, pid.stderr)
                
                if retcode < 0:
                    self.logger.error("Child was terminated by signal %s" % (-retcode))
                else:
                    self.logger.info("Child returned: %s" % retcode)
            except OSError, e:
                self.logger.error("Execution failed: %s", repr(e))            
            self.handle_filters()
        except Exception,e:
            utils.log_exception(self.logger, "Failed to execute command: %s" % e)

    def set_logger(self, logger):
        self.logger = logger        

    def __replace_helper_variables(self, inputstr, dictionary):
        retstr = inputstr
        for key in dictionary.keys():
            retstr = retstr.replace(key, dictionary[key])            
        return retstr

    def solve_refs(self):
        """
        Function to solve references just before generation.
        """
        
        self.executable = self.__solve_ref(self.executable)
        self.shell = self.__solve_ref(self.shell)
        self.bufsize = self.__solve_ref(self.bufsize)
        self.cwd = self.__solve_ref(self.cwd)
        self.envs = self.__solve_ref(self.envs)
        for argument in self.arguments:
            self.arguments[self.arguments.index(argument)] = self.__solve_ref(argument) 
        for pipe in self.pipes.keys():
            self.pipes[pipe] = self.__solve_ref(self.pipes[pipe])

    def __solve_ref(self, inputstr):
        """
        Internal function to solve whether input is ref or just normal input string. 
        For refs actual ConfML value is resolved and returned. Non-refs are returned 
        as such.
        """        
        if inputstr and isinstance(inputstr, types.StringType):
            return utils.expand_refs_by_default_view(inputstr, self.dview)
        else:
            return inputstr


        
class Filter(object):
    """
    Filter class handles printing information to ConE log using filtering information.
    Filtering severity, condition and the format of output can be configured in command ml. 
    """

    def __init__(self):
        self.severity = None
        self.condition = None
        self.input = None
        self.command = None
        self.formatter = None
        
    def set_severity(self, severity):
        self.severity = severity

    def set_condition(self, condition):
        self.condition = condition

    def set_input(self, input):
        self.input = input

    def set_command(self, command):
        self.command = command

    def set_formatter(self, formatter):
        self.formatter = formatter
        
    def report(self, logger):
        input_pipe = self.command.get_streams(self.input)
        if isinstance(input_pipe, types.FileType):
            #Subprocess.PIPE and file descriptors supported only.
            data = input_pipe.read()
            pattern = re.compile(self.condition)
            for line in data.splitlines():
                mo = pattern.match(line)
                if mo:
                    lf = self.__get_logger_function(logger)
                    if self.formatter:                        
                        lf(self.formatter % mo.groupdict())
                    else:
                        lf(line)

    def __get_logger_function(self, logger):
        if self.severity == "info":
            return logger.info
        elif self.severity == "warning":
            return logger.warning
        elif self.severity == "debug":
            return logger.debug
        elif self.severity == "exception":
            return logger.exception
        elif self.severity == "error":
            return logger.error
        elif self.severity == "critical":
            return logger.critical
        else:
            #Default
            return logger.info

        






