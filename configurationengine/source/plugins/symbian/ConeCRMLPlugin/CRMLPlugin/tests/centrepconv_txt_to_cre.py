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
#   Helper script for running CentRepConv.exe to convert .txt files to
#   .cre files. The script is given a drive where an S60 environment is
#   substed and it handles all necessary input/output file moving and
#   command running to do the conversion.
#   
#   The .txt files for which the conversion fails are reported at the end
#   of the conversion.
#

import sys, os, subprocess, shutil, re
import logging
from optparse import OptionParser, OptionGroup

log = logging.getLogger()

# Paths to the temporary directories on the environment level
TEMP_INPUT_DIR = r'\epoc32\WINSCW\C\cenrepconv_temp\input'
TEMP_OUTPUT_DIR = r'\epoc32\WINSCW\C\cenrepconv_temp\output'

# The same temporary directories in the form the emulator sees them
TEMP_INPUT_DIR_EMULATOR = r'C:\cenrepconv_temp\input'
TEMP_OUTPUT_DIR_EMULATOR = r'C:\cenrepconv_temp\output'

def recreate_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def find_cenrep_txt_files(dir):
    """
    Find all CenRep txt files in the given directory.
    @return: List of absolute paths to the files.
    """
    pattern = re.compile(r'^[a-fA-F0-9]{8}\.txt$')
    dir = os.path.abspath(dir)
    
    result = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if pattern.match(file) is not None:
                result.append(os.path.join(root, file))
    return result

def convert_txt_to_cre(file_path, output_dir):
    """
    Convert a CenRep .txt file into a .cre file using CentRepConv.exe.
    @param file_path: Path to the .txt file.
    @param output_dir: Directory where the resulting .cre file will be copied.
        If None, the output file will not be copied anywhere.
    @return: True if conversion was OK and the corresponding .cre file was
        created, False if not.
    """
    output_dir = os.path.abspath(output_dir)
    file_path = os.path.abspath(file_path)
    filename = os.path.basename(file_path)
    filename_out = filename[:-4] + '.cre'
    
    # Copy the input file into place
    temp_input_file = os.path.join(TEMP_INPUT_DIR, filename)
    shutil.copy2(file_path, temp_input_file)
    
    # Run the conversion
    cmd = r'\epoc32\release\WINSCW\udeb\centrepconv.exe -dNoGui -dtextshell -Mconsole -- -o %s %s' \
        % (os.path.join(TEMP_OUTPUT_DIR_EMULATOR, filename_out), os.path.join(TEMP_INPUT_DIR_EMULATOR, filename))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
        log.debug("Failed to execute command: %s" % cmd)
        log.debug("Command output:\n%s", out)
        return False
    
    temp_output_file = os.path.join(TEMP_OUTPUT_DIR, filename_out)
    if not os.path.exists(temp_output_file):
        log.debug("Expected output file '%s' does not exist" % temp_output_file)
        return False
    
    # Copy to output if necessary
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, os.path.basename(temp_output_file))
        log.debug("Copying output file to '%s'" % output_file)
        shutil.copy2(temp_output_file, output_file)
    
    log.debug("Removing temp output file '%s'" % temp_output_file)
    os.remove(temp_output_file)
    return True

def main():
    parser = OptionParser()
    
    parser.add_option("--env-drive",
                      help="Specifies the drive where the S60 environment containing CentRepConv.exe is located. Note that the drive needs to be writable, since input/output files need to be moved there in order to make the conversion work. Example: 'X:'",
                      metavar="DRIVE")
    
    parser.add_option("--input-file",
                      help="Specifies a single CenRep .txt file to convert.",
                      metavar="FILE")
    
    parser.add_option("--input-dir",
                      help="Specifies a directory containing the CenRep .txt files to convert. Only CenRep .txt files converted.",
                      metavar="FILE")
    
    parser.add_option("--output",
                      help="The directory where the resulting .cre files are generated",
                      metavar="DIR")
    
    parser.add_option("--validate",
                      action="store_true",
                      help="Don't copy output files to --output, only check if a .cre file is generated for each .txt file.",
                      default=False)
    
    parser.add_option("-v", "--verbose",
                      action="store_true",
                      help="Show debug information",
                      default=False)
    
    (options, args) = parser.parse_args()
    
    if not options.env_drive:
        parser.error("--env-drive must be specified")
    if re.match('^[A-Za-z]:$', options.env_drive) is None:
        parser.error("Invalid --env-drive '%s', should be e.g. 'X:'" % options.env_drive)
    if not os.path.exists(options.env_drive):
        parser.error("Specified --env-drive '%s' does not exist" % options.env_drive)
    
    if not options.input_file and not options.input_dir:
        parser.error("--input-file or --input-dir must be specified")
    if options.input_file and options.input_dir:
        parser.error("Only one for --input-file and --input-dir may be specified")
    if options.input_file and not os.path.isfile(options.input_file):
        parser.error("Specified --input-file does not exist or is not a file")
    if options.input_dir and not os.path.isdir(options.input_dir):
        parser.error("Specified --input-dir does not exist or is not a directory")
    
    if not options.output and not options.validate:
        parser.error("Either --output or --validate must be specified")
    
    if options.verbose: log_level = logging.DEBUG
    else:               log_level = logging.INFO
    logging.basicConfig(format="%(levelname)-8s: %(message)s", stream=sys.stdout, level=log_level)
    
    if options.output:  output_dir = os.path.abspath(options.output)
    else:               output_dir = None
    
    # Find input files
    log.info("Determining input files")
    if options.input_file:
        input_files = [os.path.abspath(options.input_file)]
    else:
        input_files = find_cenrep_txt_files(options.input_dir)
    log.info("%d input file(s)" % len(input_files))
    
    if len(input_files) == 0:
        log.info("No input files")
        return
    
    log.debug("Changing working directory to '%s'" % options.env_drive)
    os.chdir(options.env_drive)
    
    log.debug("Creating/cleaning temporary output directory '%s'" % TEMP_OUTPUT_DIR)
    recreate_dir(TEMP_OUTPUT_DIR)
    log.debug("Creating/cleaning temporary input directory '%s'" % TEMP_INPUT_DIR)
    recreate_dir(TEMP_INPUT_DIR)
    
    log.info("Running conversion")
    failed_files = []
    PROGRESS_STEP_PERCENTAGE = 5.0
    ratio = 100.0 / float(len(input_files))
    last_percentage = 0
    for i, file in enumerate(input_files):
        percentage = ratio * float(i)
        if percentage - last_percentage > PROGRESS_STEP_PERCENTAGE:
            log.info("%d%%" % percentage)
            last_percentage = percentage
        
        log.debug("Converting '%s'" % file)
        ok = convert_txt_to_cre(file, output_dir)
        if not ok:
            log.debug("Conversion of '%s' failed" % file)
            failed_files.append(file)
    
    if failed_files:
        print "Conversion failed for %d file(s)" % len(failed_files)
        prefix = os.path.commonprefix(failed_files)
        print "Common prefix: %s" % prefix
        for file in failed_files:
            print file[len(prefix):]

if __name__ == "__main__":
    main()
