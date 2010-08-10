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
import sys
import re
import shutil
from optparse import OptionParser

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_PATH, '..'))
if sys.version_info[0] == 2 and (sys.version_info[1] == 5 or sys.version_info[1] == 6):
    cone_basedir = os.path.join(ROOT_PATH, 'configurationengine', 
                                 'win', '%s.%s' % (sys.version_info[0], sys.version_info[1]))
    cone_scriptdir = os.path.join(cone_basedir, 'scripts')
    cone_libdir = os.path.join(cone_basedir, 'lib')
    sys.path.append(cone_basedir)
    sys.path.append(cone_scriptdir)
    sys.path.append(cone_libdir)
else:
    print 'You are using an unsupported Python version: %s.%s' % (sys.version_info[0], sys.version_info[1])
    sys.exit(1)

print sys.path
print os.getenv('PATH')
    
try:
    import scripts.cone_common
except:
    import cone_common
from cone.public import api, plugin, utils, exceptions
from cone.storage.filestorage import FileStorage

CARBON_PROJECT_URL = 'http://carbon.nokia.com/extapi'

CONFIGS_FILE = os.path.join(ROOT_PATH, 'configs.txt')
ALL_FEATURES_FILE = os.path.join(ROOT_PATH, 'all_features_and_values.txt')
REPORT_FILE = os.path.join(ROOT_PATH, 'deprecated_features.txt')
EXPORT_STORAGE = os.path.join(ROOT_PATH, 'exported')


def get_list_of_configurations_from_carbon(carbon_prj):
    config_list = carbon_prj.list_configurations()
    config_list.sort()
    return config_list

def filter_configurations_from_file(cfilter=""):
    config_list = []
    fh = open(CONFIGS_FILE, 'r')
    config_list = fh.readlines()
    fh.close()
    if cfilter:
        return [elem.strip() for elem in config_list if match_filter(cfilter, elem)]
    else: 
        return config_list

def check_deprecated_features(config, depr_features):
    default_view = config.get_default_view()
    f = open(ALL_FEATURES_FILE, 'a')
    f.write('\n\n### %s ###\n\n' % config.get_name())
    for fea_ref in default_view.list_all_features():
        feature = default_view.get_feature(fea_ref)
        # If feature has subfeatures, skip it
        if len(feature.list_features()) > 0:
            f.write('%-15s # %s\n' % ('Has subs', fea_ref))
            continue
        fea_value = default_view.get_feature(fea_ref).get_value()
        f.write('%-15s # %s\n' % (fea_value, fea_ref))  
        # If the value is None and it is not on the list yet, append it to deprecated features
        if fea_value == None and depr_features.count(fea_ref) == 0:
            depr_features.append(fea_ref)
        # If the value is something else and the feature is on the list, remove it
        elif fea_value != None and depr_features.count(fea_ref) != 0:
            depr_features.remove(fea_ref)
    f.close()
    return depr_features

def save_report(depr_features):
    fh = open(REPORT_FILE, 'w')
    try: [fh.write(df + '\n') for df in depr_features]
    finally: fh.close()
    

def match_filter(cfilter, element):
    filters = cfilter.split(';')
    for f in filters:
        if f.strip().lower() == element.strip().lower():
            return True
        if re.match('.*' + f.strip().lower() + '.*', element.strip().lower()):
            return True
    return False

def create_options():
    #parser = OptionParser(usage="Sumthin")
    parser = OptionParser()
    parser.add_option("-f", "--filter",
                      action="store",
                      dest="filter",
                      help="Filter configurations. Multiple filters can be given, separated by \';\'. E.g. -f \"\(Vasco 01\);\(Vasco 06\)\"",
                      metavar="REGEX",
                      default="")
    parser.add_option("-l", "--list-configurations",
                      action="store_true",
                      dest="list_configs",
                      help="Only list available configurations in Carbon. When used with the -f option, preview the configurations which would be fetched from Carbon.",
                      default=False)
    parser.add_option("--force-carbon",
                      action="store_true",
                      dest="force_carbon",
                      help="Get configurations from Carbon even if they have already been fetched.",
                      default=False)
    return parser

def main():
    parser = create_options()
    (options, args) = parser.parse_args()
    configs = []
    carbon_prj = None
    local_prj = None
    
    if options.filter == "":
        selection = raw_input('No filter given! ALL the configs in Carbon will be fetched and it will take a loooong time. Are you ABSOLUTELY sure you want to continue (y/n)? ')
        if selection.lower() != 'y':
            print '\nGood choice :)'
            return 0
        else:
            print '\nOk...\n'
    
    try:
        os.remove(ALL_FEATURES_FILE)
    except Exception, e:
        pass
    
    print '\nOpening project in Carbon (%s)...' % CARBON_PROJECT_URL
    try:
        carbon_prj = api.Project(api.Storage.open(CARBON_PROJECT_URL,"r"))
    except Exception, e:
        print 'Unable to open Carbon project. %s' % e
        return 1
    
    if os.path.exists(EXPORT_STORAGE):
        print '\nOpening project on local disk (%s)...' % EXPORT_STORAGE
        try:
            local_prj = api.Project(api.Storage.open(EXPORT_STORAGE, 'r'))
        except Exception, e:
            print 'Unable to open local project. %s' % e
            return 1
    
    # Force script to get everything from Carbon again
    if options.force_carbon:
        try:
            os.remove(CONFIGS_FILE)
            shutil.rmtree(EXPORT_STORAGE, ignore_errors=True)
        except:
            pass
    
    # Only get available configs and exit
    if options.list_configs:
        print 'Getting available configurations from Carbon (%s)' % CARBON_PROJECT_URL
        configs = get_list_of_configurations_from_carbon(carbon_prj)
        print 'Saving configs to %s...' % CONFIGS_FILE
        fh = open(CONFIGS_FILE, 'w')
        try: [fh.write('%s\n' % c) for c in configs]
        finally: fh.close()
        print 'Filtered configs: '
        configs = filter_configurations_from_file(options.filter)
        for elem in configs: print elem.strip()
        return 0
        
        
    if not os.path.exists(CONFIGS_FILE):
        print 'Configurations file not found. Getting list of configurations in project...'
        configs = get_list_of_configurations_from_carbon(carbon_prj)
        print 'Saving configs to %s...' % CONFIGS_FILE
        fh = open(CONFIGS_FILE, 'w')
        try: [fh.write('%s\n' % c) for c in configs]
        finally: fh.close()
    
    print '\nFilter wanted configurations from file: '   
    configs = filter_configurations_from_file(options.filter)
    for elem in configs: print elem.strip()
    
    depr_features = []
    
    for c in configs:
        config_name = c.strip()
        # Configuration has not been exported yet
        if not os.path.exists(os.path.join(EXPORT_STORAGE, config_name)):
            print '\nExport configuration %s from Carbon' % config_name
            if not carbon_prj: 
                carbon_prj = api.Project(api.Storage.open(CARBON_PROJECT_URL,"r"))
            try:
                config = carbon_prj.get_configuration(config_name)
                carbon_prj.export_configuration(config, FileStorage(EXPORT_STORAGE, 'w'))
            except:
                print 'Unable to export %s' % config_name
                continue
        print '\nOpen configuration %s in project %s' % (config_name, EXPORT_STORAGE)
        if not local_prj:
            try:
                local_prj = api.Project(api.Storage.open(EXPORT_STORAGE, 'r'))
            except Exception, e:
                print 'Unable to open local project. %s' % e
                if carbon_prj: carbon_prj.close()
                return 1
        config = local_prj.get_configuration(c.strip())
        depr_features = check_deprecated_features(config, depr_features)
        
    if local_prj: local_prj.close()
    if carbon_prj: carbon_prj.close()
    
    save_report(depr_features)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())