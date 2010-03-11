# Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

"""
This is the automated test framework, called Monty. It's not an acronym; just
a name. It is pure coincidence that it's a Python script, and is called
monty.py...

@author : Chris Haynes, (C)2007-2008 Symbian Software Ltd.
@date   : 03/09/2007 - present
@updated: 01/09/2008

To use the timeout function on Windows, you need to install PyWin32 from:
  http://sourceforge.net/project/showfiles.php?group_id=78018

This script will:
    - Read in the CSV file that contains the tests (with columns in the order
      as listed below, see docs for an example).
    - Delete the target files in the 'targets' array, if any.
    - Execute the command.
    - Check that the target files were created, if any.
    - Count the warnings and errors reported.

Each test is defined by:
    1) id:
       The test case identifier. It should be unique.
    2) note:
       A note about this test case, perhaps explaining what the test does.
    3) timed:
       1 or 0 to denote whether the test should be timed individually.
    4) display_output:
       1 or 0 to denote whether the output should be displayed on the screen.
    5) store_output:
       1 or 0 to denote whether the output should be stored in a file called
       "<id>_log.txt".
    6) command:
       The command to run. To use the unix_path variable (and others) use:
       command" + variable name + "rest of command. Do NOT put quotes around the
       entire string; just where you want to insert the variable.
    7) targets:
       An array of target files that should get built.
    8) expected_output:
       An array of text lines that should be seen in the output - in the order
       they appear.
    9-12) expected:
       A list of the number of missing files, warnings, errors and exceptions
       expected.
    13) return_code:
       The return code from the given command. Python will return zero for no
       return code. For no return code, or to ignore it, leave it at 0.
    14) os_types:
       The operating systems that the test can execute on. Currently, u (unix)
       and w (windows) are valid. You can have one or the other, or both. When
       executing the test suite, any test matching the OS type will be executed.

You can use environment variables, e.g. $ ( EPOCROOT ), $ ( USER ) etc.
(These variables have spaces here to avoid being interpreted.)

Tests can be commented out in the CSV file by starting the id with a hash,
e.g. #my_test_case...
Tests that you do not want to contribute to results, such as setup steps, should
end with a hash, e.g. my_setup_test#

You can also stop Monty from deleting the target files by ending your test case 
id with an 'at' symbol, e.g. test_targets_still_exist@

The script locates internal errors in the application you are testing and
    reports on them. You can specify the string to search for, e.g. "sbs.py",
    and it should be something which is only ever seen in internal errors. You
    can use the 'exceptions' value, but this will not report specific errors you
    are expecting.

TESTING MONTY:
- Using pylint, run the following command:
pylint monty.py --max-line-length=600 --max-module-lines=5000 --disable-msg=E1101 --disable-msg=W0603 --disable-msg=W0122 --disable-msg=C0103 --disable-msg=R0911 --disable-msg=R0912 --disable-msg=R0913 --disable-msg=R0914 --disable-msg=R0915
- You should get a score of ten. Perfection.
- This will mask the reporting of certain warning messages that do not apply, but which cause the score to fall.
"""

import csv
import datetime
import os
import re
import shutil
import sys
import time
import types
from optparse import OptionParser

# Simple setup variables
monty_version = '1.13 [2008-08-21]'
line_dash_count = 120
line_separator = '=' * line_dash_count
line_separator_dash = '-' * line_dash_count
current_mode = 'header'
output_mode = 0

# Return codes - These are overridden in the monty_cfg.py file
monty_returncode_if_config_error = 1
monty_returncode_if_test_suite_error = 2
monty_returncode_if_file_error = 3
monty_returncode_if_test_failure = 4
monty_returncode_if_test_failure_conditional = 5

# Simple check for the OS we're running on
os_type = 'unix'
if sys.platform.lower().startswith('win'):
    os_type = 'windows'

# Set up the variables for the required command line values
execute_file = ''
output_log_path = ''
test_path = ''
unix_path = ''
unix_test_path = ''
win_path = ''
win_test_path = ''

# Set up some defaults
path = ''                                         # The drive where the monty.py script is located
store_all_output = 1                              # Should all output be written to a file? (0 = no, 1 = yes)
store_csv_results = 1                             # Should we store test results in a CSV file? (0 = no, 1 = yes)
internal_error_string = ''                        # The string to find in internal error output
copy_log = 1                                      # If a logfile is generated, store it in the output_log_path?
run_test = ''                                     # Set a test to run on its own
run_group_test = ''                               # Set a group of tests to run on their own
job_section = ''                                  # Execute a job section from the test suite
allow_missing_commands_to_fail_test = 0           # If a command cannot be found, specific text is displayed in the output, such as "command not found".
                                                  # If you want this to fail a test, set this to 1. (0 = no, 1 = yes)
timeout_secs = 0                                  # The length in seconds for a command to execute before it is killed
                                                  # NOTE: To use the process timeout function on Windows, you need to install PyWin32 from:
                                                  # http://sourceforge.net/project/showfiles.php?group_id=78018
                                                  # ***NOTE***: Timeout functionality is not yet working. Leave at zero for now.
capture_stderr = 0                                # Capture output on stderr? If set to 1, errors will be output at the end of the normal stdout output
log_file_output_name = '.*in (.*\.log).*'         # A VALID regular expression for the location of the log file produced, if any.
zip_results = 1                                   # Zip up successful results?
output_mode = 0                                   # Force Monty to restrict its screen output to one of seven modes:
                                                  # 0 = Output all text
                                                  # 1 = Output tests and results but not the header
                                                  # 2 = Output header and results only
                                                  # 3 = Output tests only
                                                  # 4 = Output results only
                                                  # 5 = Output header and tests only
                                                  # 6 = Output nothing at all - just run the tests and create the logs
                                                  # Notes: Errors and warnings will always be displayed on-screen unless in mode 6. Log output is unaffected by any mode and will continue to be written in full.
determine_warning = "(.*warning:.*)"              # A VALID regular expression of what must be contained within a line of output on stdout to be interpreted as a warning
determine_warning_in_log = "(^<warning>.*)"       # A VALID regular expression of what must be contained within a line in the log file to be interpreted as a warning
determine_error = "(.*error:.*)"                  # A VALID regular expression of what must be contained within a line of output on stdout to be interpreted as an error
determine_error_in_log = "(^<error>.*)"           # A VALID regular expression of what must be contained within a line in the log file to be interpreted as an error
determine_traceback = '.*(Traceback).*'           # A VALID regular expression of what must be contained within a line of output to be interpreted as a traceback/internal error
results_date_format = "%Y-%m-%d %H-%M-%S"         # Valid Python datetime string for the results output

# Check for Python version
if sys.version_info[0:2] < (2, 4):
    print 'WARNING: Monty requires Python 2.4 or later for accurate process control.'
    if os_type == 'windows' and timeout_secs > 0:
        print 'ERROR: Aborting because Windows cannot cope.'
        sys.exit(monty_returncode_if_config_error)
else:
    import subprocess

# Now get the root drive so we don't need to alter the default locations. Use \\ for one \ in "" strings, e.g. "D:\\"
prog_path = sys.path[0]
if os_type == 'windows':
    root_drive = prog_path[0:2]
    usage_slashes = '\\'
else:
    root_drive = '~/'
    usage_slashes = '/'

# Get current working directory for when the current test's command is 'monty_restore_cwd'
original_cwd = os.getcwd()

# Make sure there's a MONTY_HOME variable set
if not 'MONTY_HOME' in os.environ:
    print 'WARNING: MONTY_HOME environment variable not set. Defaulting to current working directory...'
    os.environ['MONTY_HOME'] = os.getcwd()

# List the internal variables that Monty allows the user to use in CSV files.
# Note: 'path' MUST go at the end, or it will render the other '<xxx>_path' variables useless.
vars_from_monty = ['root_drive', 'usage_slashes', 'win_path', 'win_test_path', 'unix_path', 'unix_test_path', 'test_path', 'path']
monty_config_py = 'monty_cfg'

# Overriding the tests to execute based on OS type. Default is to adhere to the specified OS type execution.
override_os_types = ''
override_os_types_dict = {'u': 'Unix', 'w': 'Windows', 'all': 'all'}
override_os_types_usage = ''
for x in override_os_types_dict.keys():
    override_os_types_usage = override_os_types_usage + " '" + x + "' for " + override_os_types_dict[x] + ','
override_os_types_usage = override_os_types_usage[0:-1]

# ------------------------------------------------------------------------------

# The following variables are used for the compiler change commands:
# Set up a list of valid compilers:
valid_compilers = {'arm2_2': 'ARM 2.2', 'arm3_1': 'ARM 3.1', 'gcce3_4_3': 'GCCE 3.4.3', 'gcce4_2_3': 'GCCE 4.2.3'}

# Set up a list of variables to set for each compiler:
compiler_vars = {
'arm2_2': {'ARMVER': '2.2[616]', 'ARMV5VER': 'ARM/Thumb C/C++ Compiler, RVCT2.2 [Build 616]', 'ARMROOT': 'C:\\APPS\\ARM\\RVCT2.2', 'RVCT22BIN': 'C:\\Apps\\ARM\\RVCT\\Programs\\2.2\\349\\win_32-pentium', 'RVCT22INC': 'C:\\APPS\\ARM\\RVCT\\Data\\2.2\\349\\include\windows', 'RVCT22LIB': 'C:\\APPS\\ARM\\RVCT\\Data\\2.2\\349\\lib', 'PATH': 'C:\\APPS\\ARM\\RVCT\\Programs\\2.2\\349\\win_32-pentium;' + os.environ['PATH']}, 
'arm3_1': {'ARMVER': '3.1[674]', 'ARMV5VER': 'ARM/Thumb C/C++ Compiler, RVCT3.1 [Build 674]', 'ARMROOT': 'C:\\APPS\\ARM\\RVCT3.1', 'RVCT31BIN': 'C:\\Apps\\ARM\\RVCT\\Programs\\3.1\\3.1.674\\bin', 'RVCT31INC': 'C:\\APPS\\ARM\\RVCT\\Programs\\3.1\\3.1.674\\inc', 'RVCT31LIB': 'C:\\APPS\\ARM\\RVCT\\Programs\\3.1\\3.1.674\\lib', 'PATH': 'C:\\Apps\\ARM\\RVCT\\Programs\\3.1\\3.1.674\\bin;' + os.environ['PATH']}, 
'gcce3_4_3': {'PATH': 'C:\\Apps\\gcce.x\\2005q1-c\\bin;' + os.environ['PATH']}, 
'gcce4_2_3': {'PATH': 'C:\\Apps\\gcce.x\\2008q1-102\\bin;' + os.environ['PATH']}
}

# ------------------------------------------------------------------------------

def correct_slashes(value):
    """
    This module corrects slashes in pathnames supplied to it.
    """

    while value.find('\\\\') != -1:
        value = value.replace('\\\\', '\\')
        continue

    while value.find('//') != -1:
        value = value.replace('//', '/')
        continue
    if os_type == 'windows' and '/' in value:
        while value.find('/') != -1:
            value = value.replace('/', '\\')
            continue

    return value


################################################################################
# Determine the available command line arguments
################################################################################
if __name__ == '__main__':
    monty_parser = OptionParser(prog = 'monty.py', \
        usage = "%prog -h | -e <test suite csv file> -l <log path> [options]\n\nNotes: Internal commands (cd, monty_restore_cwd, etc.) in the CSV test file are executed but not counted.\n       Ensure you add trailing slashes to all directories entered on the command line.")
    monty_parser.add_option('-e', '--execute', action='store', dest='execute_file',
        help='REQUIRED: The location and filename of the CSV file containing the tests to execute (the test suite)')
    monty_parser.add_option('-t', '--testpath', action='store', dest='test_path',
        help="Directory for relative paths in the tests, e.g. '" + correct_slashes(root_drive + usage_slashes) + 'test' + usage_slashes + "'")
    monty_parser.add_option('-l', '--logpath', action='store', dest='output_log_path',
        help="REQUIRED: Where to store the log output, e.g. '" + correct_slashes(root_drive + usage_slashes) + 'logs' + usage_slashes + "'")
    monty_parser.add_option('-p', '--path', action='store', dest='path',
        help="Root directory of drive used, e.g. '" + correct_slashes(root_drive + usage_slashes) + "'")
    monty_parser.add_option('-s', '--storeoutput', action='store', dest='store_output',
        help='Store all output in a file within the logs directory. Use 1 for yes, 0 for no. Default is 1.')
    monty_parser.add_option('-i', '--interr', action='store', dest='internal_error_string',
        help="The text string to look for in output when an internal error is encountered, e.g. 'Line number:' or filename 'the_app.py'")
    monty_parser.add_option('-r', '--run', action='store', dest='run_test',
        help='The id of a test to run (in lowercase). Only this test case will be executed. You may need to use double-quotes. Cannot be used with -g.')
    monty_parser.add_option('-g', '--run_group', action='store', dest='run_group_test',
        help='A group of tests to run (in lowercase). Only test cases beginning with this text will be executed. You may need to use double-quotes. Cannot be used with -r.')
    monty_parser.add_option('-j', '--run_job', action='store', dest='run_job',
        help='The name of a job section to run (in lowercase). Can be combined with -r or -g but not both.')
    monty_parser.add_option('-c', '--csv', action='store', dest='store_csv_results',
        help='Write test results to a CSV file with id, date, result. Use 1 for yes, 0 for no. Default is 1.')
    monty_parser.add_option('-k', '--copy_log', action='store', dest='copy_log',
        help='If a logfile is generated, store it for every test? Use 1 for yes, 0 for no. Default is 1.')
    monty_parser.add_option('-x', '--config', action='store', dest='monty_config_py',
        help='The path and name of an external configuration file. Default is monty_cfg.py in the current working directory. You must supply the .py extension.')
    monty_parser.add_option('-o', '--override_os_types', action='store', dest='override_os_types',
        help='Tests can be specified to execute on certain operating systems. Set to:' + override_os_types_usage + '.')
    monty_parser.add_option('-z', '--zip_results', action='store', dest='zip_results',
        help='Zip up the results upon *successful* execution? Use 1 for yes, 0 for no. Default is 1.')
    monty_parser.add_option('-m', '--mode', action='store', dest='output_mode',
        help='Force Monty to restrict its screen output to one of seven modes: 0 = Output all text (Default), 1 = Output tests and results but not the header, 2 = Output header and results only, 3 = Output tests only, 4 = Output results only, 5 = Output header and tests only, 6 = Output nothing at all - just run the tests and create the logs. Notes: Errors and warnings will always be displayed on-screen unless in mode 6. Log output is unaffected by any mode and will continue to be written in full.')
    #monty_parser.add_option('-a', '--capture_stderr', action='store', dest='capture_stderr',
    #    help='Capture output on stderr? If set to 1, errors will be output at the end of the normal stdout output. Use 1 for yes, 0 for no. Default is 0.')
    # Parse the arguments passed to the function in args
    (monty_options, leftover_args) = monty_parser.parse_args(sys.argv[1:])

################################################################################
# Set up default variables
################################################################################
using_defaults = [' (default)', ' (default)', ' (default)', ' (default)', ' (default)', ' (default, will not report internal errors)', ' (default)', ' (default)', ' (default)', ' (default)', ' (default)']

unix_path = root_drive
win_path = root_drive + usage_slashes

# If the user has set the test_path in the config file, use that instead of the defaults created above
if test_path != '':
    win_test_path = correct_slashes(test_path)
    unix_test_path = correct_slashes(test_path)

# ------------------------------------------------------------------------------

def log_screen(the_text, the_mode):
    """
    This module simply writes out a message to the screen. It can be extended to
    restrict what is being displayed, much like the error_level of most apps.

    There are seven modes currently available:
    0 = Output all text
    1 = Output tests and results but not the header
    2 = Output header and results only
    3 = Output tests only
    4 = Output results only
    5 = Output header and tests only
    6 = Output nothing at all - just run the tests and create the logs
    """

    printed = False
    if output_mode == 0:
        print the_text
        printed = True
    elif output_mode == 1 and current_mode != 'header':
        print the_text
        printed = True
    elif output_mode == 2 and current_mode != 'run_tests':
        print the_text
        printed = True
    elif output_mode == 3 and current_mode == 'run_tests':
        print the_text
        printed = True
    elif output_mode == 4 and current_mode == 'results':
        print the_text
        printed = True
    elif output_mode == 5 and current_mode != 'results':
        print the_text
        printed = True
    elif output_mode == 6:
        # Do nothing, but need a line, or Python throws a barny
        printed = True

    if (current_mode == '' or the_mode != '') and printed == False:
        if the_mode == 'error' or the_mode == 'warning':
            # This can be changed in future to cope with different requirements for the output
            print the_text


################################################################################
# Functions for the command line arguments
################################################################################

def set_path(args):
    """
    This module sets the root path for the tests.
    """

    global win_path, unix_path

    if len(args[0:]) > 0:
        using_defaults[0] = ''
        if args[len(args) - 1:(len(args))] != usage_slashes:
            win_path = correct_slashes(args[0:] + usage_slashes)
            unix_path = correct_slashes(args[0:] + usage_slashes)
        else:
            win_path = correct_slashes(args[0:] + usage_slashes)
            unix_path = correct_slashes(args[0:] + usage_slashes)

        if ':' in unix_path:
            unix_path = unix_path.replace('\\', '/')
            unix_path = unix_path.replace(':', '')
            unix_path = '/' + unix_path[0].lower() + unix_path[1:]

# ------------------------------------------------------------------------------

def set_test_path(args):
    """
    This module sets the path for the tests to be executed.
    """

    global win_test_path, unix_test_path, test_path

    if len(args[0:]) > 0:
        using_defaults[1] = ''
        if args[len(args) - 1:(len(args))] != usage_slashes:
            test_path = correct_slashes(args[0:] + usage_slashes)
            win_test_path = correct_slashes(args[0:] + usage_slashes)
            unix_test_path = correct_slashes(args[0:] + usage_slashes)
        else:
            test_path = correct_slashes(args[0:] + usage_slashes)
            win_test_path = correct_slashes(args[0:] + usage_slashes)
            unix_test_path = correct_slashes(args[0:] + usage_slashes)

        if ':' in unix_test_path:
            unix_test_path = unix_test_path.replace('\\', '/')
            unix_test_path = unix_test_path.replace(':', '')
            unix_test_path = '/' + unix_test_path[0].lower() + unix_test_path[1:]

# ------------------------------------------------------------------------------

def set_execute_file(args):
    """
    This module sets the file CSV containing the tests to execute.
    """

    global execute_file

    if len(args[0:]) > 0:
        using_defaults[2] = ''
        execute_file = args[0:]
        if os_type == 'unix':
            execute_file = execute_file.replace('\\', '/')
            execute_file = execute_file.replace(':', '')
            execute_file = execute_file[0].lower() + execute_file[1:]
        execute_file = correct_slashes(execute_file[0:])

# ------------------------------------------------------------------------------

def set_store_output(args):
    """
    This module sets the variable that determines whether output is stored in a
    file or not.
    """

    global store_all_output

    if args[0:] == '0':
        using_defaults[3] = ''
        store_all_output = 0
    elif args[0:] == '1':
        store_all_output = 1

# ------------------------------------------------------------------------------

def set_output_log_path(args):
    """
    This module sets the path of the output log files.
    """

    global output_log_path

    if len(args[0:]) > 0:
        using_defaults[4] = ''
        if args[len(args) - 1:(len(args))] != usage_slashes:
            output_log_path = correct_slashes(args[0:] + usage_slashes)
        else:
            output_log_path = correct_slashes(args[0:] + usage_slashes)

        if os_type == 'windows':
            if ':' not in output_log_path:
                log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
                log_screen('ERROR: output_log_path must be in Windows DOS format', 'error')
                sys.exit(monty_returncode_if_config_error)
        else:
            if ':' in output_log_path:
                log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
                log_screen('ERROR: output_log_path must be in Unix format', 'error')
                sys.exit(monty_returncode_if_config_error)

# ------------------------------------------------------------------------------

def set_internal_error_string(args):
    """
    This module sets the internal error string to look for.
    """

    global internal_error_string

    if len(args[0:]) > 0:
        using_defaults[5] = ''
        internal_error_string = args[0:]

# ------------------------------------------------------------------------------

def set_run_this_test(args):
    """
    This module sets the variable containing a single test to execute.
    """

    global run_test

    if len(args[0:]) > 0:
        run_test = args[0:]

# ------------------------------------------------------------------------------

def set_run_group_test(args):
    """
    This module sets the variable containing a group of tests to execute. If a
    group test is set, it will override the single run test value.
    """

    global run_group_test, run_test

    if len(args[0:]) > 0:
        run_group_test = args[0:]
        run_test = ''

# ------------------------------------------------------------------------------

def set_run_job_section(args):
    """
    This module sets the variable containing a test job to execute.
    """

    global job_section

    if len(args[0:]) > 0:
        job_section = args[0:]

# ------------------------------------------------------------------------------

def set_store_csv_results(args):
    """
    This module sets the variable that determines whether results are stored in
    a CSV file or not. This is useful for importing results into a test
    management system.
    """

    global store_csv_results

    if args[0:] == '0':
        using_defaults[6] = ''
        store_csv_results = 0
    elif args[0:] == '1':
        store_csv_results = 1

# ------------------------------------------------------------------------------

def set_copy_log(args):
    """
    This module sets the variable that determines whether the make logfiles are
    copied or not.
    """

    global copy_log

    if args[0:] == '0':
        using_defaults[7] = ''
        copy_log = 0
    elif args[0:] == '1':
        copy_log = 1

# ------------------------------------------------------------------------------

def set_monty_config_py(args):
    """
    This module sets the monty_cfg path and filename for importing external
    configuration settings and new variables.
    """

    global monty_config_py

    if len(args[0:]) > 0:
        monty_config_py = args[0:]

# ------------------------------------------------------------------------------

def set_override_os_types(args):
    """
    This module determines whether the tests are forced to execute on the
    current OS or not.
    """

    global override_os_types

    if args[0:].lower() == 'u' or args[0:].lower() == 'w' or args[0:].lower() == 'all':
        using_defaults[8] = ''
        override_os_types = args[0:].lower()

# ------------------------------------------------------------------------------

def set_capture_stderr(args):
    """
    This module sets the variable that determines whether stderr output is
    captured separately or not.
    """

    global capture_stderr

    if args[0:] == '1':
        using_defaults[9] = ''
        capture_stderr = 1

# ------------------------------------------------------------------------------

def set_zip_results(args):
    """
    This module sets the variable that determines whether results are zipped up
    upon successful completion or not.
    """

    global zip_results

    if args[0:] == '0':
        using_defaults[10] = ''
        zip_results = 0

# ------------------------------------------------------------------------------

def set_output_mode(args):
    """
    This module sets the level at which information is output to the screen.
    """

    global output_mode

    if args[0:] == '0':
        output_mode = 0
    elif args[0:] == '1':
        output_mode = 1
    elif args[0:] == '2':
        output_mode = 2
    elif args[0:] == '3':
        output_mode = 3
    elif args[0:] == '4':
        output_mode = 4
    elif args[0:] == '5':
        output_mode = 5
    elif args[0:] == '6':
        output_mode = 6
    elif args[0:] != '0' and args[0:] != '1' and args[0:] != '2' and args[0:] != '3' and args[0:] != '4' and args[0:] != '5' and args[0:] != '6':
        log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
        log_screen('ERROR: The output mode you supplied is invalid (-m). Use 0-6.', 'error')
        sys.exit(monty_returncode_if_config_error)

# ------------------------------------------------------------------------------

def display_stuff():
    """
    This module displays stuff to the screen.
    """

    print "Cookies:\n\n\
This actually did happen to a real person, and the real person is me. I had gone to catch a train. This was April 1976, in Cambridge, U.K. I was a bit early for the train. I'd gotten the time of the train wrong. I went to get myself a newspaper to do the crossword, and a cup of coffee and a packet of cookies. I went and sat at a table. I want you to picture the scene. It's very important that you get this very clear in your mind. Here's the table, newspaper, cup of coffee, packet of cookies. There's a guy sitting opposite me, perfectly ordinary-looking guy wearing a business suit, carrying a briefcase. It didn't look like he was going to do anything weird. What he did was this: he suddenly leaned across, picked up the packet of cookies, tore it open, took one out, and ate it.\n\n\
Now this, I have to say, is the sort of thing the British are very bad at dealing with. There's nothing in our background, upbringing, or education that teaches you how to deal with someone who in broad daylight has just stolen your cookies. You know what would happen if this had been South Central Los Angeles. There would have very quickly been gunfire, helicopters coming in, CNN, you know... But in the end, I did what any red-blooded Englishman would do: I ignored it. And I stared at the newspaper, took a sip of coffee, tried to do a clue in the newspaper, couldn't do anything, and thought, What am I going to do?\n\n\
In the end I thought 'Nothing for it, I'll just have to go for it', and I tried very hard not to notice the fact that the packet was already mysteriously opened. I took out a cookie for myself. I thought, 'That settled him'. But it hadn't because a moment or two later he did it again. He took another cookie. Having not mentioned it the first time, it was somehow even harder to raise the subject the second time around. 'Excuse me, I couldn't help but notice'... I mean, it doesn't really work.\n\n\
We went through the whole packet like this. When I say the whole packet, I mean there were only about eight cookies, but it felt like a lifetime. He took one, I took one, he took one, I took one. Finally, when we got to the end, he stood up and walked away. Well, we exchanged meaningful looks, then he walked away, and I breathed a sigh of relief and sat back.\n\n\
A moment or two later the train was coming in, so I tossed back the rest of my coffee, stood up, picked up the newspaper, and underneath the newspaper were my cookies. The thing I like particularly about this story is the sensation that somewhere in England there has been wandering around for the last quarter-century a perfectly ordinary guy who's had the same exact story, only he doesn't have the punch line.\n\n\
-Douglas Adams, The Salmon of Doubt"
    sys.exit(0)


################################################################################
# Interpret the command line arguments
################################################################################
functions = {'path': set_path,
             'test_path': set_test_path,
             'execute_file': set_execute_file,
             'store_output': set_store_output,
             'output_log_path': set_output_log_path,
             'internal_error_string': set_internal_error_string,
             'run_test': set_run_this_test,
             'run_group_test': set_run_group_test,
             'run_job': set_run_job_section,
             'store_csv_results': set_store_csv_results,
             'copy_log': set_copy_log,
             'monty_config_py': set_monty_config_py,
             'override_os_types': set_override_os_types,
             'zip_results': set_zip_results,
             'output_mode': set_output_mode,
             'capture_stderr': set_capture_stderr}

if __name__ == '__main__':
    for the_opt in monty_options.__dict__.items():
        call_function = functions[str(the_opt[0])]
        the_values = the_opt[1]
        if not the_values:
            pass
        else:
            # Check if the argument type is a List or a string.
            # If a List, iterate through it and set the values.
            if type(the_values) == types.ListType:
                for val in the_values:
                    call_function(val)
            else:
                call_function(the_values)

################################################################################
# Functions
################################################################################

# Include the config data - this will overwrite any existing values
vars_from_monty_cfg = []

if not os.path.basename(monty_config_py).lower().endswith('.py'):
    monty_config_py = monty_config_py + '.py'

if os.path.exists(monty_config_py):
    monty_len_of_cfg_filename = len(os.path.basename(monty_config_py))
    monty_cfg_location = monty_config_py[:-monty_len_of_cfg_filename]
    monty_config_py = os.path.basename(monty_config_py)
    # Add the config path to the sys.path
    sys.path.append(monty_cfg_location)
    if os.path.exists(monty_cfg_location + monty_config_py):
        if monty_cfg_location != '':
            cwd = os.chdir(monty_cfg_location)
        monty_cfg = __import__(monty_config_py[:-3])

        # Get the variables and remove the unnecessary ones
        vars_from_monty_cfg = monty_cfg.__dict__.keys()
        vars_from_monty_cfg.remove('__builtins__')
        vars_from_monty_cfg.remove('__file__')
        vars_from_monty_cfg.remove('__name__')
        vars_from_monty_cfg.remove('__doc__')

        # Go through the imported variables and get them into Monty.
        # Horrible way of doing this. This is the kind of dirty that don't wash clean.
        for var_idx in vars_from_monty_cfg:
            statement = var_idx + ' = monty_cfg.' + var_idx
            #abc = monty_cfg.abc
            exec statement
        # Return to the original working directory
        os.chdir(original_cwd)

    else:
        log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
        log_screen('ERROR: Sorry, but the config module you supplied (\'' + os.path.basename(monty_config_py) + '\') was not found. Please try again.', 'error')
        sys.exit(monty_returncode_if_config_error)

else:
    if monty_config_py != 'monty_cfg.py' and (os.path.basename(monty_config_py)[:-3] != 'monty_cfg' or not os.path.basename(monty_config_py).lower().endswith('.py')):
        log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
        log_screen('ERROR: Sorry, but the config module you supplied (\'' + os.path.basename(monty_config_py) + '\') was not found. Please try again.', 'error')
        sys.exit(monty_returncode_if_config_error)

envRegex = re.compile("\$\((.+?)\)")

# Get the USERNAME or USER environment variable. Not necessary anymore?
if not 'USER' in os.environ:
    os.environ['USER'] = 'montyuser'

if not 'USERNAME' in os.environ:
    os.environ['USERNAME'] = 'montyuser'
else:
    os.environ['USERNAME'] = os.environ['USER']

# ------------------------------------------------------------------------------

def replace_envs(item):
    """
    This module substitutes environment variables specified in the command, into
    their actual values.
    """

    envs = envRegex.findall(item)

    for envvar in set(envs):
        try:
            item = item.replace("$(" + correct_slashes(envvar) + ")", os.environ[envvar])
        except KeyError:
            log_screen("ERROR: The environment variable '" + envvar + "' (within the test suite) is not set in the environment.", 'error')
            log_msg(the_output_file, "ERROR: The environment variable '" + envvar + "' (within the test suite) is not set in the environment.")
            sys.exit(monty_returncode_if_test_suite_error)

    return item

# ------------------------------------------------------------------------------

def remove_whitespace(value):
    """
    This module simply removes blank lines from the provided text. It must have
    been accessed with x.readlines() first.
    """

    new_contents = []
    for line in value:
        #print line.strip()
        if os_type == 'windows':
            new_contents.append(line.strip())
        else:
            new_contents.append(line)

    if os_type == 'windows':
        return "\n".join(new_contents)
    else:
        return ''.join(new_contents)

# ------------------------------------------------------------------------------

def normalise_filename(filename_to_normalise):
    """
    This module will convert invalid characters in a filename to those that can
    be used.
    """

    filename_to_normalise = filename_to_normalise.replace(' ', '_')
    filename_to_normalise = filename_to_normalise.replace('/', '_')
    filename_to_normalise = filename_to_normalise.replace('\\', '_')
    filename_to_normalise = filename_to_normalise.replace(':', '_')
    filename_to_normalise = filename_to_normalise.replace('*', '_')
    filename_to_normalise = filename_to_normalise.replace('#', '_')

    return filename_to_normalise

# ------------------------------------------------------------------------------

def simple_command(command):
    """
    This module executes the provided command and returns its output. It has no
    timeout functionality.
    """

    #sys.stdout = Unbuffered(sys.stdout)
    #sys.stderr = Unbuffered(sys.stderr)
    i, o = os.popen4(command)
    i.close()
    out = o.read()
    return_code = o.close()

    simple_command_return_list = ['SUCCESS', None, out, None, return_code]
    return simple_command_return_list

# ------------------------------------------------------------------------------

def timeout_command(command):
    """
    This module executes the provided command and either returns its output or
    kills it if it doesn't normally exit within the timeout seconds, and returns
    None.
    """

    import signal

    try:
        process_start = datetime.datetime.now()
        cmd = command.split()

        if os_type == 'windows':
            use_shell = True
        else:
            use_shell = False

        if capture_stderr == 1:
            process = subprocess.Popen(cmd, bufsize=0, shell=use_shell, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        else:
            process = subprocess.Popen(cmd, bufsize=0, shell=use_shell, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

        (child_stdin, child_stdout, child_stderr) = (process.stdin, process.stdout, process.stderr)
        # We don't care about stdin
        child_stdin = None

        # Poll the process to check its returncode. None means it's still running
        timeout_return_code = process.poll()
        while timeout_return_code is None:
            timeout_return_code = process.poll()
            #print 'Polled... Returncode = ' + str(timeout_return_code) + ', time = ' + str((datetime.datetime.now() - process_start).seconds)
            time.sleep(0.2)
            # Have we hit the timeout limit?
            if(datetime.datetime.now() - process_start).seconds > timeout_secs:
                if os_type == 'windows':
                    # If using Windows, we need to use a different method to kill the task - win32api from PyWin32
                    try:
                        import win32api
                        handle = win32api.OpenProcess(1, 0, process.pid)
                        if not win32api.TerminateProcess(handle, 0):
                            # Return a timeout notification
                            return ['TIMEOUT', None, None, None, None]
                    except ImportError:
                        # Return a timeout error notification
                        return ['TIMEOUT-ERROR', None, None, None, None]
                else:
                    # Kill the task on Unix and return a timeout notification
                    os.kill(process.pid, signal.SIGKILL)
                    os.waitpid(-1, os.WNOHANG)
                    return ['TIMEOUT', None, None, None, None]
    except OSError,err:
        # Return an error with id numebr and error string
        return ['ERROR', str(err.errno) + ': ' + err.strerror, None, None, None, None]

    # The task completed successfully within the timeout, so return a success notification
    timeout_command_return_list = ['SUCCESS', child_stdin, child_stdout, child_stderr, timeout_return_code]
    return timeout_command_return_list

# ------------------------------------------------------------------------------

def run_a_test(test_to_run):
    """
    This module actually runs the test and determines the result.
    """

    global total_time_taken, current_test_number, prev_test_id, prev_test_failed

    test_id = test_to_run['test_id']

    # Is the test commented out?
    if test_id.startswith('#'):
        return 'SKIP'

    # When running a job section, only the relevant jobs are in the dictionary, so we don't need to do anything here
    if job_section == '':
        # We're not running a job section
        # Are we running only one test?
        if run_test != '' and test_id.lower() != run_test.lower() and test_id.lower() != run_test.lower() + '#' and test_id.lower() != run_test.lower() + '@':
            return 'SKIP'
        # Are we running a group of tests?
        if run_group_test != '' and not test_id.lower().startswith(run_group_test.lower()):
            return 'SKIP'

    # Fail the test suite execution if the previous test failed?
    if test_id.lower() == 'monty_end_if_failed' and prev_test_failed:
        return 'MONTY_END_IF_FAILED'

    # Do not execute the start or end of a job section
    if test_id.lower().startswith('--job'):
        return 'SKIP'

    # Should this test be executed on this OS?
    test_os_type = test_to_run['os_types']
    if override_os_types == '':
        if not os_type[0:1] in test_os_type:
            return 'SKIP'
    elif override_os_types == 'u':
        if not 'u' in test_os_type:
            return 'SKIP'
    elif override_os_types == 'w':
        if not 'w' in test_os_type:
            return 'SKIP'

    current_test_number = current_test_number + 1
    note = test_to_run['note']
    timed = test_to_run['timed']
    display_output = test_to_run['display_output']
    store_output = test_to_run['store_output']
    command = replace_envs(test_to_run['command'])
    targets = []

    # Is this a monty_set_env command?
    if command.lower().startswith('monty_set_env '):
        meta_test_step_executed.append(test_id)
        temp = command
        temp = temp.replace('monty_set_env ', '')
        temp = temp.replace(' ', '')
        split_temp = temp.split('=')
        os.environ[split_temp[0]] = split_temp[1]
        log_screen('INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Setting environment variable: '" + split_temp[0] + "' to: " + split_temp[1], '')
        log_msg(the_output_file, 'INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Setting environment variable: '" + split_temp[0] + "' to: " + split_temp[1])
        return 'SKIP'

    # Is this a monty_set_compiler command?
    if command.lower().startswith('monty_set_compiler '):
        meta_test_step_executed.append(test_id)
        if os_type == 'windows':
            # Get the compiler specified
            chosen_compiler = command
            chosen_compiler = chosen_compiler.replace('monty_set_compiler ', '')
            chosen_compiler = chosen_compiler.replace(' ', '')
            if not valid_compilers.has_key(chosen_compiler):
                log_screen("WARNING: Unknown compiler chosen: '" + chosen_compiler + "'. Should be arm2_2, arm3_1, gcce3_4_3 or gcce4_2_3.", 'warning')
                log_screen('       : Tests relying on this compiler *may* fail.', 'warning')
                log_msg(the_output_file, "WARNING: Unknown compiler chosen: '" + chosen_compiler + "'. Should be arm2_2, arm3_1, gcce3_4_3 or gcce4_2_3.")
                log_msg(the_output_file, '       : Tests relying on this compiler *may* fail.')
                return 'SKIP'

            # Set the compiler variables to use the specified compiler
            log_screen('INFO: [' + str(current_test_number) + '/' + str(total_tests) + '] Setting compiler to ' + valid_compilers[chosen_compiler], '')
            log_msg(the_output_file, 'INFO: [' + str(current_test_number) + '/' + str(total_tests) + '] Setting compiler to ' + valid_compilers[chosen_compiler])
            for key, value in compiler_vars.items():
                if key == chosen_compiler:
                    for key2, value2 in value.items():
                        os.environ[key2] = value2
            return 'SKIP'

    # Restore the original directory?
    if command.lower() == 'monty_restore_cwd':
        meta_test_step_executed.append(test_id)
        log_screen('INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Changing directory back to: '" + original_cwd + "'", '')
        log_msg(the_output_file, 'INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Changing directory back to: '" + original_cwd + "'")
        try:
            os.chdir(original_cwd)
            return 'SKIP'
        except OSError:
            log_screen('WARNING: Failed to change directory back to: ' + original_cwd, 'warning')
            log_screen('       : Tests dependent upon this change *may* fail or produce incorrect results.', 'warning')
            log_msg(the_output_file, "WARNING: Failed to change directory back to: '" + original_cwd + "'")
            log_msg(the_output_file, "       : The next test *may* fail or produce incorrect results.\n")
            return 'SKIP'

    # Is this the 'cd' command?
    if command.lower().startswith('cd '):
        meta_test_step_executed.append(test_id)
        log_screen('INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Changing directory to: '" + command[3:] + "'", '')
        log_msg(the_output_file, 'INFO: [' + str(current_test_number) + '/' + str(total_tests) + "] Changing directory to: '" + command[3:] + "'")
        try:
            os.chdir(command[3:])
            return 'SKIP'
        except OSError:
            log_screen('WARNING: Failed to change directory to: ' + command[3:], 'warning')
            log_screen('       : Tests dependent upon this change *may* fail or produce incorrect results.', 'warning')
            log_msg(the_output_file, "WARNING: Failed to change directory to: '" + command[3:] + "'")
            log_msg(the_output_file, "       : The next test *may* fail or produce incorrect results.")
            return 'SKIP'

    # Is this a special case test?
    test_id_out = test_id
    test_id_note = ''
    if test_id.endswith('#'):
        test_id_out = test_id[:-1]
        test_id_note = ' (does not contribute to results)'
        meta_test_step_executed.append(test_id_out)
    elif test_id.endswith('@'):
        test_id_out = test_id[:-1]
        test_id_note = ' (targets will not be deleted prior to execution)'

    # Go through the specified targets and delete them so the environment is clean
    for t in test_to_run['targets']:
        the_actual_target = replace_column_variables(os.path.normpath(replace_envs(t)), 1)
        targets.append(the_actual_target)
        if not test_id.endswith('@'):
            if os.path.exists(the_actual_target):
                try:
                    os.remove(the_actual_target)
                    log_msg(the_output_file, "INFO: Removed target: '" + the_actual_target + "'")
                except OSError:
                    try:
                        os.rmdir(the_actual_target)
                        log_msg(the_output_file, "INFO: Removed target dir: '" + the_actual_target + "'")
                    except OSError:
                        log_screen("WARNING: Could not remove '" + the_actual_target + "' before test", 'warning')
                        log_msg(the_output_file, "WARNING: Could not remove '" + the_actual_target + "' before test")

    log_screen('', '')
    if test_id.endswith('#'):
        test_id_step_text = 'TEST STEP  : '
    else:
        test_id_step_text = 'TEST ID    : '
        meta_test_case_executed.append(test_id)
    log_screen(test_id_step_text + '[' + str(current_test_number) + '/' + str(total_tests) + '] ' + test_id_out + test_id_note, '')
    log_screen('NOTE       : ' + note, '')
    log_screen('COMMAND    : ' + command, '')

    # Execute the command and capture its output, and time taken, if required
    start_time = time.time()
    if timeout_secs > 0:
        # Timeout is set to more than zero seconds, so use the timeout function.
        timeout_results = timeout_command(command)
    else:
        #timeout_results = timeout_command(command)
        timeout_results = simple_command(command)
    end_time = time.time()

    process_result = timeout_results[0]
    child_stdin = timeout_results[1]
    child_stdout = timeout_results[2]
    child_stderr = timeout_results[3]
    return_code = timeout_results[4]

    # Check for timeouts, exceptions and no output
    if process_result == 'TIMEOUT-ERROR':
        child_stdout = "ERROR: To use the process timeout function on Windows, you need to install PyWin32 from:\n"
        child_stdout = child_stdout + "http://sourceforge.net/project/showfiles.php?group_id=78018\n"
        child_stdout = child_stdout + 'ERROR: The task could not be terminated and may still be running...'
    elif process_result == 'TIMEOUT':
        child_stdout = 'ERROR: The command did not complete within the specified timeout period (' + str(timeout_secs) + ' seconds).'
    elif process_result == 'ERROR':
        child_stdout = "ERROR: The command caused the following exception and terminated:\n       #" + child_stdin
    elif process_result is None:
        child_stdout = ''
    elif process_result == 'SUCCESS':
        if timeout_secs > 0:
            child_stdout = remove_whitespace(child_stdout)#.readlines())
    if child_stderr is not None:
        if timeout_secs > 0:
            child_stderr = remove_whitespace(child_stderr)#.readlines())
        child_stdout = child_stdout + child_stderr

    # Count the targets that were built
    found = 0
    missing = []
    if targets:
        for t in targets:
            the_actual_target = replace_column_variables(t, 1)
            if os.path.exists(the_actual_target):
                found = found + 1
            else:
                missing.append(the_actual_target)

    # Count the errors and warnings
    warn = 0
    error = 0
    exception = 0
    expected_output_count = 0
    lines = child_stdout.split("\n")
    dest_log_file_name = ''

    for line in lines:
        if determine_warning_Regex.search(line) != None:
            warn = warn + 1
        elif determine_error_Regex.search(line) != None:
            error = error + 1
        elif determine_traceback_Regex.search(line) != None:
            exception = exception + 1
        else:
            log_found = None
            try:
                logRegex = re.compile(log_file_output_name)
                log_found = logRegex.search(line)
            except re.error:
                log_screen("WARNING: The regular expression used for the 'log_file_output_name' variable is invalid. Check your '..._cfg.py' file.", 'warning')
                log_msg(the_output_file, "WARNING: ")

            if log_found != None:
                # Copy the log file to the output_log_path
                log_file_name = log_found.group(1)

                if os.path.exists(log_file_name):
                    # Normalise the name and filename
                    normalised_name = normalise_filename(test_id)
                    dest_log_file_name = normalise_filename(log_file_name)
                    dest_log_file_name = log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + "_" + normalised_name + "---" + dest_log_file_name

                    # Increment the filename if it already exists
                    if os.path.exists(dest_log_file_name):
                        log_file_name_count = 0
                        while os.path.exists(dest_log_file_name + '_' + str(log_file_name_count)):
                            log_file_name_count = log_file_name_count + 1
                        dest_log_file_name = dest_log_file_name + '_' + str(log_file_name_count)

                    # Copy the file so that we have some readable output
                    shutil.copy(log_file_name, dest_log_file_name)

                    if not os.path.isfile(dest_log_file_name):
                        log_screen('WARNING: Could not copy command output log file for this test', 'warning')
                    else:
                        # Now search through the log file for warnings and errors
                        try:
                            output_log_check_lines_file = open(dest_log_file_name, 'r')
                            output_log_check_lines = output_log_check_lines_file.readlines()
                            for output_log_check_line in output_log_check_lines:
                                if determine_warning_Regex.search(output_log_check_line) != None:
                                    warn = warn + 1
                                elif determine_error_Regex.search(output_log_check_line) != None:
                                    error = error + 1
                        except IOError:
                            log_screen("WARNING: Couldn't open log file: '" + dest_log_file_name + "' for reading.", 'warning')
                            log_screen('       : Warnings and errors *may* be incorrect.', 'warning')

    # Send output to the screen
    if display_output == 1:
        log_screen('', '')
        log_screen(centre_line_niceness('START OF OUTPUT OF THIS TEST', '-', line_dash_count), '')
        log_screen(child_stdout, '')
        log_screen(centre_line_niceness('END OF OUTPUT OF THIS TEST', '-', line_dash_count), '')
        if child_stderr is not None and child_stderr != '' and capture_stderr == 1:
            log_screen('', '')
            log_screen(centre_line_niceness('START OF STDERR OUTPUT OF THIS TEST', '-', line_dash_count), '')
            log_screen(child_stderr, '')
            log_screen(centre_line_niceness('END OF STDERR OUTPUT OF THIS TEST', '-', line_dash_count), '')

    # If there was anything in child_stderr, output it to a file
    child_stderr_output_file = ''
    if child_stderr is not None and child_stderr != '' and store_output == 1 and capture_stderr == 1:
        if ' ' in test_id:
            ourPattern = re.compile('(.*?)(\s)')
            result = ourPattern.match(test_id)
            filename = result.group(0)
        else:
            filename = test_id[:25]
        filename = normalise_filename(filename)
        log_screen('SAVE STDERR: ' + log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_stderr_log.txt', '')

        try:
            child_stderr_output_file = open(log_dir + filename + "_" + d.strftime("%Y-%m-%d_%H-%M-%S") + '_stderr_log.txt', 'wt')
            log_msg(child_stderr_output_file, test_id_step_text + '[' + str(current_test_number) + '/' + str(total_tests) + '] ' + test_id_out + test_id_note + "\nNOTE       : " + note + "\nCOMMAND    : " + command + "\nSTDERR OUT :")
            log_msg(child_stderr_output_file, centre_line_niceness('START OF STDERR OUTPUT OF THIS TEST', '-', line_dash_count))
            log_msg(child_stderr_output_file, child_stderr)
            log_msg(child_stderr_output_file, centre_line_niceness('END OF STDERR OUTPUT OF THIS TEST', '-', line_dash_count))
        except IOError:
            show_error(log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_stderr_log.txt', 'The file could not be created.', child_stderr_output_file, 0)

    # Redirect all output to a file?
    output_file = ''
    output_file_exists = False
    if store_output == 1:
        if ' ' in test_id:
            ourPattern = re.compile('(.*?)(\s)')
            result = ourPattern.match(test_id)
            filename = result.group(0)
        else:
            filename = test_id[:25]
        filename = normalise_filename(filename)
        log_screen('SAVING LOG : ' + log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_log_<RESULT>.txt', '')

        try:
            output_file = open(log_dir + filename + "_" + d.strftime("%Y-%m-%d_%H-%M-%S") + '_log_IN_PROGRESS.txt', 'wt')
            log_msg(output_file, test_id_step_text + '[' + str(current_test_number) + '/' + str(total_tests) + '] ' + test_id_out + test_id_note + "\nNOTE       : " + note + "\nCOMMAND    : " + command + "\nOUTPUT     :")
            log_msg(output_file, centre_line_niceness('START OF OUTPUT OF THIS TEST', '-', line_dash_count))
            log_msg(output_file, child_stdout)
            log_msg(output_file, centre_line_niceness('END OF OUTPUT OF THIS TEST', '-', line_dash_count))
            output_file_exists = True
        except IOError:
            show_error(log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_log_IN_PROGRESS.txt', 'The file could not be created.', output_file, 0)
            output_file_exists = False

    log_msg(the_output_file, "\n" + test_id_step_text + '[' + str(current_test_number) + '/' + str(total_tests) + '] ' + test_id_out + test_id_note)
    log_msg(the_output_file, "NOTE       : " + note + "\nCOMMAND    : " + command + "\nOUTPUT     :\n" + child_stdout)

    # Was this test timed?
    if timed == 1:
        time_difference = end_time - start_time
        total_time_taken = total_time_taken + time_difference
        log_screen(str("TIME TAKEN : %.2f" % (time_difference, ) + ' seconds'), '')
        log_msg(the_output_file, str("TIME TAKEN : %.2f" % (time_difference, )) + ' seconds')
        log_msg_if_exists(output_file, str("TIME TAKEN : %.2f" % (time_difference, )) + ' seconds', store_output, output_file_exists)

    # Set up the results for checking later on
    expected = test_to_run['expected']
    result = {'missing': len(missing),
              'warnings': warn,
              'errors': error,
              'exceptions': exception}
    success = True

    # Check the results
    success = check_results(targets, found, missing, warn, error, exception, expected, the_output_file, output_file, store_output, output_file_exists)

    # Check for internal errors. Only reports the first occurrence of 'internal_error_string' in the output
    found_internal_error = False
    if internal_error_string != "":
        for line in lines:
            if line.find(internal_error_string) != -1:
                if not found_internal_error:
                    found_internal_error = True
                    log_screen('INTERNAL ERROR. Check output (last 20 lines shown):', '')
                    log_screen(centre_line_niceness('START OF INTERNAL ERROR OUTPUT', '-', line_dash_count), '')
                    log_screen('', '')
                    log_msg(the_output_file, 'INTERNAL ERROR. Check output (last 20 lines shown):')
                    log_msg(the_output_file, centre_line_niceness('START OF INTERNAL ERROR OUTPUT', '-', line_dash_count) + "\n")
                    log_msg_if_exists(output_file, 'INTERNAL ERROR. Check output (last 20 lines shown):', store_output, output_file_exists)
                    log_msg_if_exists(output_file, centre_line_niceness('START OF INTERNAL ERROR OUTPUT', '-', line_dash_count) + "\n", store_output, output_file_exists)

                    line_count = len(lines) - 20
                    if line_count <= 20:
                        line_count = len(lines) - 1
                    for line_index in range(len(lines) - line_count + 1, len(lines) - 1):
                        log_screen(lines[line_index], '')
                        log_msg(the_output_file, str(lines[line_index]))
                        log_msg_if_exists(output_file, str(lines[line_index]), store_output, output_file_exists)

                    log_screen('', '')
                    log_screen(centre_line_niceness('END OF INTERNAL ERROR OUTPUT', '-', line_dash_count), '')
                    log_msg(the_output_file, "\n" + centre_line_niceness('END OF INTERNAL ERROR OUTPUT', '-', line_dash_count))
                    log_msg_if_exists(output_file, "\n" + centre_line_niceness('END OF INTERNAL ERROR OUTPUT', '-', line_dash_count), store_output, output_file_exists)
                    success = False

    # Are we expecting some text in the output?
    expected_output = test_to_run['expected_output']
    expected_output_len = len(expected_output)
    expected_output_loop = expected_output_len - 1
    if expected_output_loop >= 0:
        expected_output_index = 0
        expected_output_count = 0

        # If the log was copied, we need to read that log so we can check for expected output
        if copy_log == 1 and os.path.exists(dest_log_file_name):
            log_file_contents = open(dest_log_file_name, 'r')
            lines = lines + log_file_contents.readlines()

        for line in lines:
            if line.find(replace_column_variables(expected_output[expected_output_index], 1)) != -1:
                expected_output_count = expected_output_count + 1
                if expected_output_index < expected_output_loop:
                    expected_output_index = expected_output_index + 1

        log_screen(str("EXP.OUTPUT : %d, expected %d" % (expected_output_count, expected_output_len)), '')
        log_msg(the_output_file, str("EXP.OUTPUT : %d, expected %d" % (expected_output_count, expected_output_len)))
        log_msg_if_exists(output_file, str("EXP.OUTPUT : %d, expected %d" % (expected_output_count, expected_output_len)), store_output, output_file_exists)
        if expected_output_count != expected_output_len:
            success = False

    # Any known errors?
    if allow_missing_commands_to_fail_test == 1:
        for line in lines:
            if os_type == "windows" and line.find("is not recognized as an internal or external command") != -1:
                # This output means that the command entered was not found on Windows - fail the test
                success = False
            if os_type == "unix" and line.find("command not found") != -1:
                # This output means that the command entered was not found on Unix - fail the test
                success = False

    # Check the return code
    test_return_code = test_to_run['return_code']
    if return_code is None:
        return_code = 0
    if os_type == 'windows':
        if test_return_code != 0 or (test_return_code == 0 and return_code != 0):
            log_screen(str("RETURNCODE : %d, expected %d" % (return_code, test_return_code)), '')
            log_msg(the_output_file, str("RETURNCODE : %d, expected %d" % (return_code, test_return_code)))
            log_msg_if_exists(output_file, str("RETURNCODE : %d, expected %d" % (return_code, test_return_code)), store_output, output_file_exists)
        if (test_return_code != 0 and return_code != test_return_code) or (test_return_code == 0 and return_code != 0):
            success = False

    # Determine the success, and mark the test appropriately
    if success:
        log_screen('RESULT     : Pass', '')
        log_msg(the_output_file, 'RESULT     : Pass')
        log_msg_if_exists(output_file, 'RESULT     : Pass', store_output, output_file_exists)
        result_csv = 'Passed'
    else:
        log_screen('RESULT     : Failed', '')
        log_msg(the_output_file, 'RESULT     : Failed')
        log_msg_if_exists(output_file, 'RESULT     : Failed', store_output, output_file_exists)
        if found_internal_error:
            internal_error_failures.append(test_id)
        else:
            failures.append(test_id + ' --- ' + note)
        result_csv = 'Failed'

    # Write the result to the CSV results file?
    # If the id ends with a '#' it will not be written as a CSV result
    csv_indiv_file_exists = False
    if store_csv_results == 1 and not test_id.endswith('#'):
    	ts = d.fromtimestamp(start_time)
    	te = d.fromtimestamp(end_time)
    #Here is the implementation of adding microseconds in the end in ':000' format
    	start_microseconds = ts.microsecond/1000
    	end_microseconds = te.microsecond/1000
    
    	if start_microseconds == 0:
                start_microseconds = "000"
        elif start_microseconds < 10:
                start_microseconds = "00" + str(start_microseconds)
        elif start_microseconds < 100:
                start_microseconds = "0" + str(start_microseconds)
                
        if end_microseconds == 0:
                end_microseconds = "000"
        elif end_microseconds < 10:
                end_microseconds = "00" + str(end_microseconds)
        elif end_microseconds < 100:
                end_microseconds = "0" + str(end_microseconds)
                
                
        csv_results_file.write(test_id_out + ",'" + str(ts.strftime(results_date_format)+":"+str(start_microseconds)) + ",'" + str(te.strftime(results_date_format)+":"+str(end_microseconds)) + ',' + result_csv + "\n")
        if store_output == 1:
            try:
                csv_indiv_results_file = open(log_dir + test_id_out + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv', 'wt')
                csv_indiv_results_file.write("TestCaseId,StartTime,EndTime,Result\n")
                csv_indiv_results_file.write(test_id_out + ",'" + str(ts.strftime(results_date_format)) + ",'" + str(te.strftime(results_date_format)) + ',' + result_csv + "\n")
                csv_indiv_file_exists = True
                csv_indiv_results_file.close()
            except OSError:
                log_screen("WARNING: Couldn't write CSV results file for test case: '" + test_id + "'.", 'warning')

    log_screen(line_separator_dash, '')
    log_msg(the_output_file, line_separator_dash)
    log_msg_if_exists(output_file, line_separator_dash, store_output, output_file_exists)

    # Rename the output files?
    if store_output == 1 and output_file_exists:
        output_file.close()
        output_filename_result = '_PASS'
        if not success:
            output_filename_result = '_FAIL'
        if found_internal_error:
            output_filename_result = output_filename_result + '_WITH_INTERNAL_ERROR'

        old_output_filename = log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_log_IN_PROGRESS.txt'
        new_output_filename = log_dir + filename + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_log' + output_filename_result + '.txt'
        try:
            os.rename(old_output_filename, new_output_filename)
            log_screen("INFO       : The output file has been renamed to: '" + new_output_filename + "'", '')
        except OSError:
            log_screen("WARNING: Couldn't rename the output log file for test case: " + old_output_filename, 'warning')

        if csv_indiv_file_exists:
            old_output_filename = log_dir + test_id_out + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv'
            new_output_filename = log_dir + test_id_out + '_' + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results' + output_filename_result + '.csv'
            try:
                os.rename(old_output_filename, new_output_filename)
                log_screen("INFO       : The CSV results file has been renamed to: '" + new_output_filename + "'", '')
            except OSError:
                log_screen("WARNING: Couldn't rename the CSV results file for test case: " + test_id_out + ' (' + old_output_filename + ').', 'warning')

        log_screen(line_separator_dash, '')

    # Decide how to exit the module
    if success:
        prev_test_failed = False
        return 'TRUE'
    else:
        prev_test_id = test_id
        prev_test_failed = True
        if found_internal_error:
            return 'FALSE-INTERNAL_ERROR'
        elif test_id.endswith('#'):
            return 'FALSE-STEP'
        else:
            return 'FALSE'

# ------------------------------------------------------------------------------

def check_results(the_targets, found, the_missing, the_warn, the_error, the_exception, expected_items, in_the_output_file, in_output_file, store_output, output_file_exists):
    """
    This module checks whether the targets expected are present or missing, and
    whether there are any errors, warnings or exceptions.
    """

    this_test_success = True

    # Any targets?
    if len(the_targets) > 0:
        if len(the_targets) == expected_items['missing']:
            log_screen(str("TARGETS    : %d, all are expected to be missing" % (len(the_targets))), '')
            log_msg(in_the_output_file, str("TARGETS    : %d, all are expected to be missing" % (len(the_targets))))
            log_msg_if_exists(in_output_file, str("TARGETS    : %d, all are expected to be missing" % (len(the_targets))), store_output, output_file_exists)
        else:
            if expected_items['missing'] > 0:
                log_screen(str("TARGETS    : %d, expected %d" % (found, len(the_targets) - expected_items['missing'])), '')
                log_msg(in_the_output_file, str("TARGETS    : %d, expected %d" % (found, len(the_targets) - expected_items['missing'])))
                log_msg_if_exists(in_output_file, str("TARGETS    : %d, expected %d" % (found, len(the_targets) - expected_items['missing'])), store_output, output_file_exists)
                if (len(the_targets) - expected_items['missing']) != found:
                    this_test_success = False
            else:
                log_screen(str("TARGETS    : %d, expected %d" % (found, len(the_targets))), '')
                log_msg(in_the_output_file, str("TARGETS    : %d, expected %d" % (found, len(the_targets))))
                log_msg_if_exists(in_output_file, str("TARGETS    : %d, expected %d" % (found, len(the_targets))), store_output, output_file_exists)
                if (len(the_targets) - expected_items['missing']) != found:
                    this_test_success = False

    # Any missing items?
    if expected_items['missing'] != 0 or len(the_missing) != 0:
        log_screen(str("MISSING    : %d, expected %d" % (len(the_missing), expected_items['missing'])), '')
        log_msg(in_the_output_file, str("MISSING    : %d, expected %d" % (len(the_missing), expected_items['missing'])))
        log_msg_if_exists(in_output_file, str("MISSING    : %d, expected %d" % (len(the_missing), expected_items['missing'])), store_output, output_file_exists)
    if len(the_missing) != expected_items['missing']:
        this_test_success = False
        for the_file in the_missing:
            log_screen(str("           : %s" % (the_file)), '')
            log_msg(in_the_output_file, str("           : %s" % (the_file)))
            log_msg_if_exists(in_output_file, str("           : %s" % (the_file)), store_output, output_file_exists)

    # Any warnings?
    if expected_items['warnings'] != 0 or the_warn != 0:
        log_screen(str("WARNINGS   : %d, expected %d" % (the_warn, expected_items['warnings'])), '')
        log_msg(in_the_output_file, str("WARNINGS   : %d, expected %d" % (the_warn, expected_items['warnings'])))
        log_msg_if_exists(in_output_file, str("WARNINGS   : %d, expected %d" % (the_warn, expected_items['warnings'])), store_output, output_file_exists)
    if the_warn != expected_items['warnings']:
        this_test_success = False

    # Any errors?
    if expected_items['errors'] != 0 or the_error != 0:
        log_screen(str("ERRORS     : %d, expected %d" % (the_error, expected_items['errors'])), '')
        log_msg(in_the_output_file, str("ERRORS     : %d, expected %d" % (the_error, expected_items['errors'])))
        log_msg_if_exists(in_output_file, str("ERRORS     : %d, expected %d" % (the_error, expected_items['errors'])), store_output, output_file_exists)
    if the_error != expected_items['errors']:
        this_test_success = False

    # Any exceptions?
    if expected_items['exceptions'] != 0 or the_exception != 0:
        log_screen(str("EXCEPTIONS : %d, expected %d" % (the_exception, expected_items['exceptions'])), '')
        log_msg(in_the_output_file, str("EXCEPTIONS : %d, expected %d" % (the_exception, expected_items['exceptions'])))
        log_msg_if_exists(in_output_file, str("EXCEPTIONS : %d, expected %d" % (the_exception, expected_items['exceptions'])), store_output, output_file_exists)
    if the_exception != expected_items['exceptions']:
        this_test_success = False

    # Return the result
    return this_test_success

# ------------------------------------------------------------------------------

def replace_column_variables(column, stripslashes):
    """
    This module replaces any occurences of internal Monty variables and those
    variables within the monty_cfg module in test case fields with the value of
    that variable.
    """

    column = replace_envs(column)

    # Replace internal Monty variables
    value_of_idx = ''
    for loop_idx in vars_from_monty:
        statement_to_run = 'value_of_idx = str(' + loop_idx + ')'
        try:
            if os_type == 'windows' and loop_idx == 'root_drive':
                # Change drive letters to uppercase
                value_of_idx = value_of_idx.upper()
            exec statement_to_run
            column = column.replace('" + ' + loop_idx + ' + "', value_of_idx)
            column = column.replace('" + ' + loop_idx, value_of_idx)
            column = column.replace(loop_idx + ' + "', value_of_idx)
        except NameError:
            log_screen("ERROR: The internal variable '" + loop_idx + "' used in the test suite is undefined.", 'error')
            log_msg(the_output_file, "ERROR: The internal variable '" + loop_idx + "' used in the test suite is undefined.")
            sys.exit(monty_returncode_if_test_suite_error)

    # Replace the variables from the monty_cfg module
    for loop_idx in vars_from_monty_cfg:
        statement_to_run = 'value_of_idx = str(' + loop_idx + ')'
        try:
            exec statement_to_run
            column = column.replace('" + ' + loop_idx + ' + "', value_of_idx)
            column = column.replace('" + ' + loop_idx, value_of_idx)
            column = column.replace(loop_idx + ' + "', value_of_idx)
        except NameError:
            log_screen("ERROR: The variable '" + loop_idx + "' used in the test suite is undefined. Check your '..._cfg.py' file.", 'error')
            log_msg(the_output_file, "ERROR: The variable '" + loop_idx + "' used in the test suite is undefined. Check your '..._cfg.py' file.")
            sys.exit(monty_returncode_if_test_suite_error)

    # Strip any invalid slashes
    if stripslashes == 1:
        column = column.replace('\\\\', '\\')
    else:
        if os_type == "unix":
            column = column.replace(':\\', '\\')
            column = column.replace('\\', '/')

    return column

# ------------------------------------------------------------------------------

def get_tests(file_handle):
    """
    This module reads in the test case CSV file and returns a List variable
    containing the test cases to execute.
    """

    global internal_command_count, total_tests, test_cases, test_steps, meta_test_step_id, meta_test_case_id

    row_line_number = 0
    line_errors = 0
    tests_common = []
    rows = 0
    skipped_rows = 0
    actual_rows = 0
    found_run_test = False
    run_test_dict = {}
    found_run_group_test = False
    run_group_test_dict = {}
    tests_in_group = 0
    found_job_section = False
    run_job_test_dict = {}
    in_job_section = False
    number_of_columns = 14
    have_reset_tests_common = False

    for row in file_handle:
        actual_rows += 1
        row_line_number += 1
        row_dict = {}
        exp_dict = {'missing': 0, 'warnings': 0, 'errors': 0, 'exceptions': 0}
        dict_index = 0
        skip_test = False
        internal_command = False

        for column in row:
            if not skip_test:
                if dict_index == 0:
                    try:
                        row_dict['test_id'] = replace_column_variables(column, 0)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: id', 'warning')
                        log_screen("       : Defaulting to: 'TEST-" + str(row_line_number) + "'", 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: id')
                        log_msg(the_output_file, "       : Defaulting to: 'TEST-" + str(row_line_number) + "'")
                        row_dict['test_id'] = 'TEST-' + str(row_line_number)
                        line_errors += 1
                    if row_dict['test_id'] == 'id':
                        # User has not removed the header row from the csv file; just ignore this row
                        dict_index = number_of_columns - 1
                        actual_rows -= 1
                        skip_test = True

                    if job_section != '' and not skip_test:
                        # Check to see if this job section is the one we're looking for
                        if row_dict['test_id'].lower() == '--job start: ' + job_section.lower() and found_job_section == False:
                            # Yes, so ignore the row
                            actual_rows -= 1
                            dict_index = number_of_columns - 1
                            skip_test = True
                            found_job_section = True
                            in_job_section = True

                        if row_dict['test_id'].lower() == '--job end: ' + job_section.lower() and found_job_section == True:
                            # This is the end of the selected job section, so ignore the row
                            actual_rows -= 1
                            dict_index = number_of_columns - 1
                            skip_test = True
                            in_job_section = False

                        if not in_job_section:
                            # We aren't currently in a job section, so these are tests that might be the selected individual or group
                            if row_dict['test_id'].lower() != '--job end: ' + job_section.lower():
                                if run_test != '' and (row_dict['test_id'].lower() != run_test.lower() and row_dict['test_id'].lower() != run_test.lower() + '#' and row_dict['test_id'].lower() != run_test.lower() + '@'):
                                    if row_dict['test_id'].lower().startswith('--job'):
                                        actual_rows -= 1
                                    row_dict['test_id'] = '#' + row_dict['test_id']

                                elif run_group_test != '' and not row_dict['test_id'].lower().startswith(run_group_test.lower()):
                                    if row_dict['test_id'].lower().startswith('--job'):
                                        actual_rows -= 1
                                    row_dict['test_id'] = '#' + row_dict['test_id']

                                elif row_dict['test_id'].startswith('#') or row_dict['test_id'].lower().startswith('--job'):
                                    actual_rows -= 1

                            skip_test = True

                        # Running a single test or a group of tests is possible with a job section
                        if run_test != '' and (row_dict['test_id'].lower() == run_test.lower() or row_dict['test_id'].lower() == run_test.lower() + '#' or row_dict['test_id'].lower() == run_test.lower() + '@'):
                            found_run_test = True
                            skip_test = False

                        if run_group_test != '' and row_dict['test_id'].lower().startswith(run_group_test.lower()):
                            found_run_group_test = True
                            skip_test = False

                    else:
                        if not skip_test:
                            if run_test != '' and (row_dict['test_id'].lower() == run_test.lower() or row_dict['test_id'].lower() == run_test.lower() + '#' or row_dict['test_id'].lower() == run_test.lower() + '@'):
                                found_run_test = True
                            if run_group_test != '' and row_dict['test_id'].lower().startswith(run_group_test.lower()):
                                found_run_group_test = True
                            if row_dict['test_id'].startswith('#') or row_dict['test_id'].lower().startswith('--job'):
                                actual_rows -= 1
                                skip_test = True

                elif dict_index == 1:
                    try:
                        row_dict['note'] = replace_column_variables(column, 0)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: note', 'warning')
                        log_screen("       : Defaulting to: 'TEST-" + str(row_line_number) + "'", 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: note')
                        log_msg(the_output_file, "       : Defaulting to: 'TEST-" + str(row_line_number) + "'")
                        line_errors += 1
                        row_dict['note'] = 'TEST-' + str(row_line_number) + "' - Note"

                elif dict_index == 2:
                    try:
                        row_dict['timed'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: timed', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: timed')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['timed'] = 0

                elif dict_index == 3:
                    try:
                        row_dict['display_output'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: display_output', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: display_output')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['display_output'] = 0

                elif dict_index == 4:
                    try:
                        row_dict['store_output'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: store_output', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: store_output')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['store_output'] = 0

                elif dict_index == 5:
                    try:
                        row_dict['command'] = replace_column_variables(column, 0)
                    except ValueError:
                        log_screen('ERROR  : Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: command', 'error')
                        log_screen('       : Id: ' + row_dict['test_id'] + ' - This test will NOT be executed', 'error')
                        log_msg(the_output_file, 'ERROR  : Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: command')
                        log_msg(the_output_file, '       : Id: ' + row_dict['test_id'] + ' - This test will NOT be executed')
                        line_errors += 1
                        row_dict['command'] = ''
                        skip_test = True
                    # Don't count internal commands in the test count
                    if row_dict['command'].lower() == 'monty_restore_cwd' or row_dict['command'].lower().startswith('cd ') or row_dict['command'].lower().startswith('monty_set_env ') or row_dict['command'].lower().startswith('monty_set_compiler '):
                        internal_command = True
                        internal_command_count += 1

                elif dict_index == 6:
                    try:
                        if column != '':
                            column = replace_column_variables(column, 0)
                            row_dict['targets'] = column.split(',')
                        else:
                            row_dict['targets'] = []
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: targets', 'warning')
                        log_screen("       : Defaulting to: '' (no targets)", 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: targets')
                        log_msg(the_output_file, "       : Defaulting to: '' (no targets)")
                        line_errors += 1
                        row_dict['targets'] = []

                elif dict_index == 7:
                    try:
                        if column != '':
                            column = replace_column_variables(column, 0)
                            row_dict['expected_output'] = column.split(',')
                        else:
                            row_dict['expected_output'] = []
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: expected_output', 'warning')
                        log_screen("       : Defaulting to: '' (no expected output)", 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: expected_output')
                        log_msg(the_output_file, "       : Defaulting to: '' (no expected output)")
                        line_errors += 1
                        row_dict['expected_output'] = ''

                elif dict_index == 8:
                    try:
                        exp_dict['missing'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: missing', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: missing')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['missing'] = 0

                elif dict_index == 9:
                    try:
                        exp_dict['warnings'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: warnings', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: warnings')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['warnings'] = 0

                elif dict_index == 10:
                    try:
                        exp_dict['errors'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: errors', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: errors')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['errors'] = 0

                elif dict_index == 11:
                    try:
                        exp_dict['exceptions'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: exceptions', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: exceptions')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['exceptions'] = 0
                    row_dict['expected'] = exp_dict

                elif dict_index == 12:
                    try:
                        row_dict['return_code'] = int(column)
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: return_code', 'warning')
                        log_screen('       : Defaulting to: 0', 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: return_code')
                        log_msg(the_output_file, '       : Defaulting to: 0')
                        line_errors += 1
                        row_dict['return_code'] = 0

                elif dict_index == 13:
                    try:
                        row_dict['os_types'] = column
                    except ValueError:
                        log_screen('WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: os_types', 'warning')
                        log_screen("       : Defaulting to: 'uw' (both Unix and Windows)", 'warning')
                        log_msg(the_output_file, 'WARNING: Invalid value in test suite CSV file, line: ' + str(row_line_number) + ', column: os_types')
                        log_msg(the_output_file, "       : Defaulting to: 'uw' (both Unix and Windows)")
                        line_errors += 1
                        row_dict['os_types'] = 'uw'
                    # Should this test be run?
                    if override_os_types == '':
                        if not os_type[0:1] in column:
                            skip_test = True
                            if internal_command == True:
                                internal_command_count -= 1
                    elif override_os_types == 'u':
                        if not 'u' in column:
                            skip_test = True
                            if internal_command == True:
                                internal_command_count -= 1
                    elif override_os_types == 'w':
                        if not 'w' in column:
                            skip_test = True
                            if internal_command == True:
                                internal_command_count -= 1

                dict_index += 1
                if dict_index == number_of_columns:
                    dict_index = 0

                    if row_dict['test_id'] == 'id':
                        # Don't do anything with this row, because it's the header row, but Python makes us do something here
                        row_dict['test_id'] == 'id'

                    elif job_section == '':
                        if run_test == '' and run_group_test == '' and not skip_test:
                            tests_common.append(row_dict)
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

                        elif run_test != '' and (row_dict['test_id'].lower() == run_test.lower() or row_dict['test_id'].lower() == run_test.lower() + '#' or row_dict['test_id'].lower() == run_test.lower() + '@') and not row_dict['test_id'].lower().startswith('--job') and not skip_test:
                            tests_common = []
                            tests_common.append(row_dict)
                            meta_test_step_id = []
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            meta_test_case_id = []
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

                        elif run_group_test != '' and row_dict['test_id'].lower().startswith(run_group_test.lower()) and not skip_test:
                            tests_in_group += 1
                            if not have_reset_tests_common:
                                have_reset_tests_common = True
                                meta_test_step_id = []
                                meta_test_case_id = []
                                tests_common = []
                            tests_common.append(row_dict)
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

                    else:
                        # We're running a job section
                        if run_test != '' and (row_dict['test_id'].lower() == run_test.lower() or row_dict['test_id'].lower() == run_test.lower() + '#' or row_dict['test_id'].lower() == run_test.lower() + '@') and not row_dict['test_id'].lower().startswith('--job') and not skip_test:
                            if not row_dict in tests_common:
                                tests_common.append(row_dict)
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

                        elif run_group_test != '' and row_dict['test_id'].lower().startswith(run_group_test.lower()) and not skip_test:
                            tests_in_group += 1
                            tests_common.append(row_dict)
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

                        elif in_job_section and not row_dict['test_id'].lower().startswith('--job') and not skip_test:
                            if not row_dict in tests_common:
                                tests_common.append(row_dict)
                            if internal_command or row_dict['test_id'].endswith('#'):
                                skipped_rows += 1
                                meta_test_step_id.append(row_dict['test_id'])
                            if not internal_command and not row_dict['test_id'].endswith('#') and not row_dict['test_id'].lower().startswith('--job'):
                                rows += 1
                                meta_test_case_id.append(row_dict['test_id'])

    if line_errors > 0:
        log_screen('*' * line_dash_count, 'warning')
        if line_errors == 1:
            csv_errors = 'was one error'
            csv_errors_2 = ' has'
        elif line_errors > 1:
            csv_errors = 'were ' + str(line_errors)+ ' errors'
            csv_errors_2 = 's have'
        log_screen('WARNING: There ' + csv_errors + ' recorded in the CSV test suite.', 'warning')
        log_screen('       : You should check that the test case' + csv_errors_2 +' been executed correctly.', 'warning')
        log_screen('*' * line_dash_count, 'warning')
        log_screen('', 'warning')

    if len(tests_common) == 0 and skipped_rows == 0 and job_section == '':
        log_screen(' ERROR: Found no executable tests in the test suite.', 'error')
        log_screen(' Automated test execution abandoned.', 'error')
        log_screen(line_separator, 'error')
        log_msg(the_output_file, ' Found no executable tests in the test suite.')
        log_msg(the_output_file, ' Automated test execution abandoned.')
        log_msg(the_output_file, line_separator + "\n")
        sys.exit(monty_returncode_if_test_suite_error)

    test_cases = len(meta_test_case_id)
    test_steps = len(meta_test_step_id)
    total_tests = test_cases + test_steps

    #print 'rows: ' + str(rows)
    #print 'skipped_rows: ' + str(skipped_rows)
    #print 'len of tests_common: ' + str(len(tests_common))
    #print 'actual_rows: ' + str(actual_rows)
    #print "test_cases = " + str(test_cases)
    #print "test_steps = " + str(test_steps)
    #print "total_tests = " + str(total_tests)

    nice_test_cases = ''
    if test_cases == 1:
        nice_test_cases = '1 test case'
    elif test_cases > 1:
        nice_test_cases = str(test_cases) + ' test cases'

    nice_test_steps = ''
    if test_steps == 1:
        nice_test_steps = '1 test step'
    elif test_steps > 1:
        nice_test_steps = str(test_steps) + ' test steps'

    test_cases_and = ''
    if test_cases > 0 and test_steps > 0:
        test_cases_and = ' and '

    nice_test_cases_count = str(nice_test_cases) + test_cases_and + nice_test_steps

    if run_test != '' and job_section == '':
        total_tests = 1
        log_screen(' Found ' + nice_test_cases_count + " in the test suite.\n Will execute only test: '" + run_test + "'.", '')
        log_msg(the_output_file, ' Found ' + nice_test_cases_count + " in the test suite.\n Will execute only test: '" + run_test + "'.")

        if not found_run_test:
            log_screen('', 'error')
            log_screen(" ERROR: Could not locate the test '" + run_test + "' in the test suite.", 'error')
            log_screen(" Automated test execution abandoned.", 'error')
            log_screen(line_separator, '')
            log_msg(the_output_file, " ERROR: Could not locate the test '" + run_test + "' in the test suite.")
            log_msg(the_output_file, " Automated test execution abandoned.")
            log_msg(the_output_file, line_separator)
            sys.exit(monty_returncode_if_test_suite_error)

        log_screen(line_separator, '')
        log_msg(the_output_file, line_separator + "\n")

    elif run_group_test != '' and job_section == '':
        # Go through the tests and get a count of the tests that match
        total_tests = 0
        for current_test in tests_common:
            if current_test['test_id'].lower().startswith(run_group_test.lower()):
                total_tests = total_tests + 1

        nice_test_count = ''
        if total_tests > 1:
            nice_test_count = 's'

        log_screen(' Found ' + nice_test_cases_count + " in the test suite.\n Will execute only tests beginning with: '" + run_group_test + "' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').', '')
        log_msg(the_output_file, ' Found ' + nice_test_cases_count + " in the test suite.\n Will execute only tests beginning with: '" + run_group_test + "' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').')

        if not found_run_group_test:
            log_screen('', 'error')
            log_screen(" ERROR: Could not locate tests beginning with '" + run_group_test + "' in the test suite.", 'error')
            log_screen(" Automated test execution abandoned.", 'error')
            log_screen(line_separator, '')
            log_msg(the_output_file, " ERROR: Could not locate tests beginning with '" + run_group_test + "' in the test suite.")
            log_msg(the_output_file, " Automated test execution abandoned.")
            log_msg(the_output_file, line_separator)
            sys.exit(monty_returncode_if_test_suite_error)

        log_screen(line_separator, '')
        log_msg(the_output_file, line_separator + "\n")

    elif job_section != '':
        nice_test_count = ''
        if found_job_section == False:
            # Couldn't find the job section
            log_screen('', 'error')
            log_screen(" ERROR: Could not locate job section '" + job_section + "' in the test suite.", 'error')
            log_screen(" Automated test execution abandoned.", 'error')
            log_screen(line_separator, '')
            log_msg(the_output_file, " ERROR: Could not locate job section '" + job_section + "' in the test suite.")
            log_msg(the_output_file, " Automated test execution abandoned.")
            log_msg(the_output_file, line_separator)
            sys.exit(monty_returncode_if_test_suite_error)

        if run_group_test == '' and run_test == '':
            # We're only running a job section
            log_screen(' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'", '')#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').', '')
            log_screen(line_separator, '')
            log_msg(the_output_file, ' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'")#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').')
            log_msg(the_output_file, line_separator + "\n")

        elif run_group_test != '' and run_test == '':
            # We're running a job section and a group of tests
            log_screen(' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'", '')#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').', '')
            log_msg(the_output_file, ' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'")#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').')
            if found_run_group_test:
                log_screen(" Will also execute tests beginning with: '" + run_group_test + "'", '')#"' (" + str(tests_in_group) + ' test' + nice_group_test_count + ' or step' + nice_group_test_count + ').', '')
                log_screen(line_separator, '')
                log_msg(the_output_file, " Will also execute tests beginning with: '" + run_group_test + "'")#"' (" + str(tests_in_group) + ' test' + nice_group_test_count + ' or step' + nice_group_test_count + ').')
                log_msg(the_output_file, line_separator + "\n")
            else:
                log_screen(" ERROR: Could not locate tests beginning with: '" + run_group_test + "' in the test suite.", 'error')
                log_screen(" Automated test execution abandoned.", 'error')
                log_screen(line_separator, '')
                log_msg(the_output_file, " ERROR: Could not locate tests beginning with: '" + run_group_test + "' in the test suite.")
                log_msg(the_output_file, " Automated test execution abandoned.")
                log_msg(the_output_file, line_separator)
                sys.exit(monty_returncode_if_test_suite_error)

        elif run_group_test == '' and run_test != '':
            # We're running a job section and a single test
            log_screen(' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'", '')#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').', '')
            log_msg(the_output_file, ' Found ' + nice_test_cases_count + " in the test suite.\n Will execute job section: '" + job_section + "'")#"' (" + str(total_tests) + ' test' + nice_test_count + ' or step' + nice_test_count + ').')
            if found_run_test:
                log_screen(" Will also execute the test case: '" + run_test + "'", '')
                log_screen(line_separator, '')
                log_msg(the_output_file, " Will also execute the test: '" + run_test + "'")
                log_msg(the_output_file, line_separator + "\n")
            else:
                log_screen(" ERROR: Could not locate the test '" + run_test + "' in the test suite.", 'error')
                log_screen(" Automated test execution abandoned.", 'error')
                log_screen(line_separator, '')
                log_msg(the_output_file, " ERROR: Could not locate the test '" + run_test + "' in the test suite.")
                log_msg(the_output_file, " Automated test execution abandoned.")
                log_msg(the_output_file, line_separator)
                sys.exit(monty_returncode_if_test_suite_error)

    else:
        log_screen(' Found ' + nice_test_cases_count + ' in the test suite. Commencing execution...', '')
        log_screen(line_separator, '')
        log_msg(the_output_file, ' Found ' + nice_test_cases_count + ' in the test suite. Commencing execution...')
        log_msg(the_output_file, line_separator)

    return tests_common

# ------------------------------------------------------------------------------

def show_error(resource, reason, file_handle, exit_app):
    """
    This module shows an error and, optionally, stops execution of Monty.
    """

    if resource != '' and resource != 'MONTY_END_IF_FAILED':
        log_screen(" ERROR: Error accessing the file/directory: '" + resource + "' because:", 'error')
    elif resource == 'MONTY_END_IF_FAILED':
        log_screen(" ERROR: The following required test case/step failed:", 'error')
    else:
        log_screen(" ERROR:", 'error')
    log_screen(' ' + str(reason) + "\n", 'error')
    log_screen(' Automated test execution failed.', 'error')
    log_screen(line_separator, 'error')

    if store_all_output == 1 and file_handle != None:
        log_msg(file_handle, " ERROR: Error accessing the file/directory: '" + resource + "' because:")
        log_msg(file_handle, ' ' + str(reason) + "\n")
        log_msg(file_handle, ' Automated test execution failed.')
        log_msg(file_handle, line_separator)
        file_handle.close()

	# Close and rename the output files
        old_filename = output_log_path + d.strftime("%Y-%m-%d_%H-%M-%S") + usage_slashes + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output_IN_PROGRESS.txt'
        new_filename = output_log_path + d.strftime("%Y-%m-%d_%H-%M-%S") + usage_slashes + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output_ERROR.txt'
        if os.path.exists(old_filename):
            try:
                os.rename(old_filename, new_filename)
                log_screen("INFO: The output file has been renamed to: '" + new_filename + "'", '')
            except OSError:
                log_screen("WARNING: Couldn't rename the output log file from: '" + old_filename + "' to '" + new_filename + "'.", 'warning')

        if store_csv_results == 1 and csv_results_file != None:
            csv_results_file.close()
            old_filename = output_log_path + d.strftime("%Y-%m-%d_%H-%M-%S") + usage_slashes + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv'
            new_filename = output_log_path + d.strftime("%Y-%m-%d_%H-%M-%S") + usage_slashes + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_ERROR.csv'
            if os.path.exists(old_filename):
                try:
                    os.rename(old_filename, new_filename)
                    log_screen("INFO: The csv results file has been renamed to: '" + new_filename + "'", '')
                except OSError:
                    log_screen("WARNING: Couldn't rename the CSV results file from: '" + old_filename + "' to '" + new_filename + "'.", 'warning')

    if exit_app > 0:
        sys.exit(exit_app)

# ------------------------------------------------------------------------------

def log_msg(file_handle, the_text):
    """
    This module simply writes out a message to the log file, if appropriate.
    """

    if store_all_output == 1:
        try:
            file_handle.write(the_text + "\n")
        except IOError:
            log_screen("WARNING: Couldn't write to the log file.", 'warning')

# ------------------------------------------------------------------------------

def log_msg_if_exists(file_handle, the_text, store_output, output_file_exists):
    """
    This module simply writes out a message to the log file, if it exists.
    """

    if store_output == 1 and output_file_exists:
        try:
            file_handle.write(the_text + "\n")
        except IOError:
            log_screen("WARNING: Couldn't write to the log file for this test case.", 'warning')

# ------------------------------------------------------------------------------

def centre_line_niceness(the_string, the_char, max_size):
    """
    This module simply returns a niced-up string with repeated chars to either
    side.
    """

    str_length = len(the_string)
    if str_length >= max_size:
        return the_string

    str_sides = (max_size - str_length) / 2
    nice_string = (the_char * str_sides) + the_string + (the_char * str_sides)
    if len(nice_string) < max_size:
        nice_string = nice_string + the_char

    return nice_string

# ------------------------------------------------------------------------------

def zipdir(the_zip_path, zip_file):
    """
    This module zips up the provided directory.
    """

    for each_file in os.listdir(the_zip_path):
        try:
            zip_file.write(the_zip_path + each_file)
        except IOError:
            log_screen("ERROR: Couldn't zip the results.", 'error')

# ------------------------------------------------------------------------------

################################################################################
# MAIN
################################################################################

# Check that the required command line options have been entered
if path == '':
    path = original_cwd + usage_slashes

if execute_file == '':
    log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen('ERROR: You must supply a test suite CSV file (-e)', 'error')
    sys.exit(monty_returncode_if_config_error)

if output_log_path == '':
    log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen('ERROR: You must supply a path for the logs (-l)', 'error')
    sys.exit(monty_returncode_if_config_error)

if os_type != 'unix' and os_type != 'windows':
    log_screen('Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen('WARNING: Unknown OS type! Will assume Unix-style pathnames...', 'error')
    os_type = 'unix'

# Correct the paths used in the commands
if ':' in unix_path:
    unix_path = unix_path.replace('\\', '/')
    unix_path = unix_path.replace(':', '')
    unix_path = '/' + unix_path[0].lower() + unix_path[1:]

if '\\' in unix_test_path or ':' in unix_test_path:
    unix_test_path = unix_test_path.replace('\\', '/')
    unix_test_path = unix_test_path.replace(':', '')
    unix_test_path = unix_test_path[0].lower() + unix_test_path[1:]

#if not win_path.endswith('\\'):
#    win_path = win_path + '\\'
if win_test_path:
	if not win_test_path.endswith('\\'):
		win_test_path = win_test_path + '\\'

if not unix_path.endswith('/'):
    unix_path = unix_path + '/'
if not unix_test_path.endswith('/'):
    unix_test_path = unix_test_path + '/'

# Check the regular expressions for the warnings, errors and tracebacks
try:
    logFileRegex = re.compile(log_file_output_name)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'log_file_output_name' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
try:
    determine_warning_Regex = re.compile(determine_warning)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'determine_warning' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
try:
    determine_warning_in_log_Regex = re.compile(determine_warning_in_log)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'determine_warning_in_log' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
try:
    determine_error_Regex = re.compile(determine_error)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'determine_error' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
try:
    determine_error_in_log_Regex = re.compile(determine_error_in_log)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'determine_error_in_log' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
try:
    determine_traceback_Regex = re.compile(determine_traceback)
except re.error:
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(" ERROR: The regular expression used for the 'determine_traceback' variable is invalid. Check your '..._cfg.py' file.", 'error')
    sys.exit(monty_returncode_if_config_error)
if determine_traceback == 'dna':
    display_stuff()

# Check to see if the group and individual test choices have both been set
if run_test != '' and run_group_test != '':
    log_screen(' Monty ' + str(monty_version) + ' - Type monty.py -h for usage', 'error')
    log_screen(' ERROR: Cannot use both the -g and -r command line options at the same time.', 'error')
    sys.exit(monty_returncode_if_config_error)

# Display the settings
current_mode = 'header'
d = datetime.datetime.now()
d.isoformat()
log_screen("\n" + line_separator, '')
log_screen(' Monty ' + str(monty_version) + ' - Automated test suite execution for ' + d.strftime("%Y-%m-%d %H:%M:%S") + ' commencing...', '')
log_screen(line_separator, '')
log_screen(' Using definitions:', '')

log_screen('               OS type = ' + os_type, '')
log_screen('            Test suite = ' + execute_file + using_defaults[2], '')

if os_type == 'windows':
    log_screen('                  Path = ' + win_path + using_defaults[0], '')
    log_screen('             Test path = ' + win_test_path + using_defaults[1], '')
else:
    log_screen('                  Path = ' + unix_path + using_defaults[0], '')
    log_screen('             Test path = ' + unix_test_path + using_defaults[1], '')

if store_all_output == 1:
    log_screen('        Storing output = Yes' + using_defaults[3], '')
else:
    log_screen('        Storing output = No' + using_defaults[3], '')

if store_csv_results == 1:
    log_screen('   Storing CSV results = Yes' + using_defaults[6], '')
else:
    log_screen('   Storing CSV results = No' + using_defaults[6], '')

if copy_log == 1:
    log_screen(' Copying make logfiles = Yes' + using_defaults[7], '')
else:
    log_screen(' Copying make logfiles = No' + using_defaults[7], '')

log_screen('       Output log path = ' + output_log_path + using_defaults[4], '')
log_screen(" Internal error string = '" + internal_error_string + "'" + using_defaults[5], '')

if run_test != '':
    log_screen("     Running only test = '" + run_test + "'", '')

if run_group_test != '':
    log_screen("    Running test group = '" + run_group_test + "'...", '')

if monty_config_py != '':
    log_screen(' Using external config = ' + monty_config_py, '')

if override_os_types != '':
    log_screen('    Overriding OS type = Yes: running ' + override_os_types_dict[override_os_types] + ' tests' + using_defaults[8], '')
else:
    log_screen('    Overriding OS type = No: running ' + override_os_types_dict[os_type[0:1]] + ' tests' + using_defaults[8], '')

if timeout_secs > 0:
    log_screen('   Tests timeout after = ' + str(timeout_secs) + ' seconds', '')

log_screen(line_separator, '')

# ------------------------------------------------------------------------------

# Check to see if the output log path exists
current_mode = 'logs'
if not os.path.exists(output_log_path):
    show_error(output_log_path, 'The output log path does not exist', None, monty_returncode_if_file_error)

# ------------------------------------------------------------------------------

# Set up some variables
passed = 0
script_time_taken = 0.0
total_time_taken = 0.0

# Create lists to store failed test case and step ids
failures = []
internal_error_failures = []
skipped_test_failures = []

# Create a log directory?
if store_all_output == 1 or store_csv_results == 1:
    # Check to see if the path to the log directory exists
    if not os.path.exists(output_log_path):
        log_screen("ERROR: The path to the logs directory doesn't exist - '" + output_log_path + "'.", 'error')
        log_screen("       Logs will be produced in: '" + path + "' instead.", 'error')
        output_log_path = path

    log_dir = output_log_path + d.strftime("%Y-%m-%d_%H-%M-%S")
    # Increment the filename if it already exists
    if os.path.exists(log_dir):
        log_dir_name_count = 0
        while os.path.exists(log_dir + '_' + str(log_dir_name_count)):
            log_dir_name_count = log_dir_name_count + 1
        log_dir = log_dir + '_' + str(log_dir_name_count)

    # Make the directory
    try:
        os.mkdir(log_dir)
        log_dir = log_dir + usage_slashes
    except IOError,e:
        log_screen(" ERROR: Error creating the log directory: '" + log_dir + "' because:\n " + e.strerror, 'error')
        log_screen(" INFO: Log results will be written in: '" + output_log_path + "'.", 'error')
        log_dir = output_log_path

# Redirect all output to a log file?
if store_all_output == 1:
    log_screen(' Copying all output to file:', '')
    log_screen(' ' + log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output_IN_PROGRESS.txt', '')
    try:
        the_output_file = open(log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output_IN_PROGRESS.txt', 'wt')
    except IOError:
        log_screen(" ERROR: Couldn't create a log file for this test run.", 'error')
        log_screen(' Automated test execution failed.', 'error')
        sys.exit(monty_returncode_if_file_error)

    log_msg(the_output_file, line_separator)
    log_msg(the_output_file, ' Monty ' + str(monty_version) + ' - Automated test output')
    log_msg(the_output_file, line_separator)

    log_msg(the_output_file, ' Using definitions:')
    log_msg(the_output_file, '               OS type = ' + os_type)
    log_msg(the_output_file, '            Test suite = ' + execute_file + using_defaults[2])

    if os_type == 'windows':
        log_msg(the_output_file, '                  Path = ' + win_path + using_defaults[0])
        log_msg(the_output_file, '             Test path = ' + win_test_path + using_defaults[1])
    else:
        log_msg(the_output_file, '                  Path = ' + unix_path + using_defaults[0])
        log_msg(the_output_file, '             Test path = ' + unix_test_path + using_defaults[1])

    log_msg(the_output_file, '        Storing output = Yes' + using_defaults[3])

    if store_csv_results == 1:
        log_msg(the_output_file, '   Storing CSV results = Yes' + using_defaults[6])
    else:
        log_msg(the_output_file, '   Storing CSV results = No' + using_defaults[6])

    if copy_log == 1:
        log_msg(the_output_file, ' Copying make logfiles = Yes' + using_defaults[7])
    else:
        log_msg(the_output_file, ' Copying make logfiles = No' + using_defaults[7])

    log_msg(the_output_file, '       Output log path = ' + output_log_path + using_defaults[4])
    log_msg(the_output_file, " Internal error string = '" + internal_error_string + "'" + using_defaults[5])

    if run_test != '':
        log_msg(the_output_file, "     Running only test = '" + run_test + "'")

    if run_group_test != '':
        log_msg(the_output_file, "    Running test group = '" + run_group_test + "'...")

    if monty_config_py != '':
        log_msg(the_output_file, ' Using external config = ' + monty_config_py)

    if override_os_types != '':
        log_msg(the_output_file, '    Overriding OS type = Yes: running ' + override_os_types_dict[override_os_types] + ' tests' + using_defaults[8])
    else:
        log_msg(the_output_file, '    Overriding OS type = No: running ' + override_os_types_dict[os_type[0:1]] + ' tests' + using_defaults[8])

    if timeout_secs > 0:
        log_msg(the_output_file, '   Tests timeout after = ' + str(timeout_secs) + ' seconds')
    log_msg(the_output_file, line_separator)

# ------------------------------------------------------------------------------

current_mode = 'test_suite'
# Open the test file to execute
if not os.path.exists(execute_file):
    csv_results_file = None
    show_error(execute_file, 'The test suite csv file does not exist', the_output_file, monty_returncode_if_file_error)
else:
    try:
        execute_file_handle = csv.reader(open(execute_file, 'rb'))
    except IOError:
        log_screen(" ERROR: Error accessing the file/directory: '" + execute_file + "' because:", 'error')
        log_screen(' The csv file with the tests to execute does not exist.', 'error')
        log_screen(' Automated test execution failed.', 'error')
        if store_all_output == 1:
            log_msg(the_output_file, " ERROR: Error accessing the file/directory: '" + execute_file + "' because:")
            log_msg(the_output_file, ' The csv file with the tests to execute does not exist.')
            log_msg(the_output_file, ' Automated test execution failed.')
            log_msg(the_output_file, line_separator)
        sys.exit(monty_returncode_if_file_error)

# ------------------------------------------------------------------------------

# Save results to a CSV file?
if store_csv_results == 1:
    log_screen(' Storing test results in CSV file:', '')
    log_screen(' ' + log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv', '')
    csv_results_file = open(log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv', 'wt')
    csv_results_file.write("TestCaseId,StartTime,EndTime,Result\n")

if store_all_output == 1 or store_csv_results == 1:
    log_screen(line_separator, '')

# ------------------------------------------------------------------------------

# Get the tests and put them into the 'theTests' list
current_mode = 'get_tests'
internal_command_count = 0
test_cases = 0
test_steps = 0
total_tests = 0
current_test_number = 0
# Create lists to store the meta data
meta_test_step_id = []
meta_test_case_id = []
meta_tests_in_job_section = []
meta_test_step_executed = []
meta_test_case_executed = []
# Get the tests
theTests = get_tests(execute_file_handle)


################################################################################
# RUN THE TESTS
################################################################################

current_mode = 'run_tests'
if output_mode == 3:
    log_screen(line_separator, '')
    log_screen('Monty ' + str(monty_version) + ' - Automated test suite execution for ' + d.strftime("%Y-%m-%d %H:%M:%S") + ' commencing...', '')
    log_screen(line_separator, '')
skipped = 0
skipped_count = 0
tests_not_counted = 0
prev_test_id = ''
prev_test_failed = False

# Start the timer
script_start_time = time.time()

# Run each test
for test in theTests:
    # Execute the test
    test_success = run_a_test(test)
    # Determine the success or failure
    if test_success == 'FALSE-STEP':
        # If the function returns "FALSE-STEP", this is a step and it failed.
        # Although it was executed, it doesn't contribute to the results
        skipped_test_failures.append(test['test_id'])
        skipped_count = skipped_count + 1

    if test_success != 'SKIP' and test_success != 'FALSE-INTERNAL_ERROR' and test['test_id'].endswith('#'):
        tests_not_counted = tests_not_counted + 1
    elif test_success == 'TRUE':
        passed = passed + 1
    elif test_success == 'SKIP' and run_group_test != '':
        skipped = skipped + 1

    # If the function returns "FALSE-INTERNAL_ERROR", the test failed due to
    # an internal error. Should not contribute to the results.

    # If the function returns "SKIP", the test was commented out in the
    # test suite and doesn't contribute to the results.

    # If the previous test failed, we have to end the loop and exit Monty.
    if prev_test_failed and test['test_id'].lower() == 'monty_end_if_failed':
        show_error('MONTY_END_IF_FAILED', "'" + prev_test_id + "'. Monty will now exit.", the_output_file, monty_returncode_if_test_failure_conditional)

# End the timer and calculate the script time taken
script_end_time = time.time()
script_time_taken = script_end_time - script_start_time


################################################################################
# CALCULATE THE RESULTS
################################################################################

# Calculate the final values and display them
current_mode = 'results'
passed_calc = passed + 0.0

test_count = len(meta_test_case_executed)

if test_count <= 0:
    test_count = 0
    pc_calculation = 0.0
else:
    pc_calculation = passed_calc / (test_count + 0.0)

monty_returncode = 0
log_screen('', '')
if output_mode == 4:
    log_screen(line_separator, '')
    log_screen('Monty ' + str(monty_version) + ' - Automated test suite execution results for ' + d.strftime("%Y-%m-%d %H:%M:%S") + '...', '')
log_screen(line_separator, '')
log_screen(str("  SCRIPT TIME : %.2f" % (script_time_taken, )) + ' seconds', '')
log_screen(str("  TIMED TESTS : %.2f" % (total_time_taken, )) + ' seconds', '')
log_screen(' TESTS PASSED : ' + str(passed) + ' / ' + str(test_count) + (" : %.2f" % (pc_calculation * (100 + 0.0), )) + ' percent', '')
log_msg(the_output_file, "\n" + line_separator)
log_msg(the_output_file, str("  SCRIPT TIME : %.2f" % (script_time_taken, )) + ' seconds')
log_msg(the_output_file, str("  TIMED TESTS : %.2f" % (total_time_taken, )) + ' seconds')
log_msg(the_output_file, ' TESTS PASSED : ' + str(passed) + ' / ' + str(test_count) + str(": %.2f" % (pc_calculation * (100 + 0.0), )) + ' percent')
if test_count == 0:
    monty_returncode = 0
    log_screen('              : There were no test cases that returned a result', '')
    log_msg(the_output_file, '              : There were no test cases that returned a result')

# Did all tests pass?
zip_results_type = '_tests_'
if passed == test_count:
    monty_returncode = 0
    if skipped_count == 0:
        if test_count > 0:
            filename_result = '_ALL_PASSED'
            log_screen('', '')
            log_screen(' *** Congratulations! All tests passed ***', '')
            log_msg(the_output_file, "\n *** Congratulations! All tests passed ***")
        else:
            filename_result = '_ALL_STEPS_PASSED'
            log_screen('', '')
            log_screen(' *** All test steps passed. There were no test cases. ***', '')
            log_msg(the_output_file, "\n *** All test steps passed. There were no test cases. ***")
            zip_results_type = '_steps_'
            test_count = total_tests
            pc_calculation = 1.0

    if len(skipped_test_failures) > 0:
        monty_returncode = monty_returncode_if_test_failure
        filename_result = '_SOME_STEP_FAILURES'
        log_screen("\n Some steps failed and may have affected the results:", 'warning')
        log_msg(the_output_file, "\n Some steps failed and may have affected the results:")
        for skipped_step in range(0, len(skipped_test_failures)):
            log_screen(' ' + skipped_test_failures[skipped_step], 'warning')
            log_msg(the_output_file, ' ' + str(skipped_test_failures[skipped_step]))

    if len(internal_error_failures) > 0:
        monty_returncode = monty_returncode_if_test_failure
        filename_result = '_PASSED_WITH_INTERNAL_ERRORS'
        log_screen(line_separator, 'warning')
        log_screen(' WARNING: ' + str(len(internal_error_failures)) + ' internal error(s) encountered. Please investigate the following:', 'warning')
        log_msg(the_output_file, line_separator)
        log_msg(the_output_file, ' WARNING: ' + str(len(internal_error_failures)) + ' internal error(s) encountered. Please investigate the following:')
        for failed_test in range(0, len(internal_error_failures)):
            log_screen(' ' + internal_error_failures[failed_test], 'warning')
            log_msg(the_output_file, ' ' + str(internal_error_failures[failed_test]))
else:
    # Some tests failed
    monty_returncode = monty_returncode_if_test_failure
    log_screen(line_separator, 'warning')
    log_msg(the_output_file, line_separator + "\n")
    filename_result = '_SOME_FAILURES'
    if len(failures) > 0:
        if len(failures) == 1:
            nice_failures = ' test or step has'
        else:
            nice_failures = ' tests or steps have'
        log_screen('', 'warning')
        log_screen(' WARNING: ' + str(len(failures)) + nice_failures + ' failed. Please investigate the following: (id --- note)', 'warning')
        log_msg(the_output_file, ' WARNING: ' + str(len(failures)) + nice_failures + ' failed. Please investigate the following: (id --- note)')
        for failed_test in range(0, len(failures)):
            log_screen(' ' + failures[failed_test], 'warning')
            log_msg(the_output_file, ' ' + str(failures[failed_test]))

    # Any internal errors?
    if len(internal_error_failures) > 0:
        filename_result = '_SOME_FAILURES_AND_INTERNAL_ERRORS'
        nice_failures = ' was'
        if len(failures) > 1:
            nice_failures = 's were'
        log_screen('', 'warning')
        log_screen(' WARNING: ' + str(len(internal_error_failures)) + ' internal error' + nice_failures + ' encountered. Please investigate the following:', 'warning')
        log_msg(the_output_file, " WARNING: " + str(len(internal_error_failures)) + ' internal error' + nice_failures + ' encountered. Please investigate the following:')
        for failed_test in range(0, len(internal_error_failures)):
            log_screen(' ' + internal_error_failures[failed_test], 'warning')
            log_msg(the_output_file, ' ' + str(internal_error_failures[failed_test]))

log_screen(line_separator, '')
log_screen('', '')
log_msg(the_output_file, line_separator)

# Close and rename the output files
if store_all_output == 1:
    the_output_file.close()
    the_old_filename = log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output_IN_PROGRESS.txt'
    the_new_filename = log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_output' + filename_result + '.txt'
    try:
        os.rename(the_old_filename, the_new_filename)
        log_screen('INFO: The output file has been renamed to:', '')
        log_screen(' ' + the_new_filename, '')
    except OSError:
        log_screen("WARNING: Couldn't rename the output log file.", 'warning')

if store_csv_results == 1:
    csv_results_file.close()
    the_old_filename = log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results_IN_PROGRESS.csv'
    the_new_filename = log_dir + d.strftime("%Y-%m-%d_%H-%M-%S") + '_results' + filename_result + '.csv'
    try:
        os.rename(the_old_filename, the_new_filename)
        log_screen('INFO: The csv results file has been renamed to:', '')
        log_screen(' ' + the_new_filename, '')
    except OSError:
        log_screen("WARNING: Couldn't rename the CSV results file.", 'warning')

# Zip up the results?
if zip_results == 1:
    log_screen('', '')
    zip_filename = 'automated_results_' + d.strftime("%Y%m%d-%H%M%S") + '-' + str(test_count) + zip_results_type + os_type + '_' + str("%.2f" % (pc_calculation * (100 + 0.0), )) + '_percent_pass.zip'
    log_screen('Zipping results to:', '')
    log_screen(' ' + output_log_path + zip_filename, '')

    import zipfile
    the_zip_file = zipfile.ZipFile(output_log_path + zip_filename, 'w')
    for each in os.listdir(log_dir):
        try:
            the_zip_file.write(log_dir + each)
        except IOError:
            log_screen("ERROR: Couldn't zip the results.", 'error')
            the_zip_file.close()
            sys.exit(monty_returncode_if_file_error)
    the_zip_file.close()

# ------------------------------------------------------------------------------

# End Monty with an appropriate returncode
sys.exit(monty_returncode)

# ------------------------------------------------------------------------------
# END
