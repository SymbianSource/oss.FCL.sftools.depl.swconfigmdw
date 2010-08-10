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

import os.path
import sys
import logging
from optparse import OptionParser, OptionGroup
import cone_common
from cone.public import api
from conesub_merge import get_active_root_if_necessary
                          
VERSION = '1.0'

logger    = logging.getLogger('cone')

def find_variant_layers(source_config):
    """
    Find all layers in the configuration that contain custvariant* in
    their path name and return a list containing source->target mappings.
    @param target_config: The target configuration object.
    @param new_name: The new name to replace custvariant* in the
        target path name with.
    @return: A list of (source_layer, target_layer) tuples.
    """
    import re
    pattern = re.compile(r'.*/(custvariant[^/]*)/.*')
    result = []

    for src in source_config.list_configurations():
        m = pattern.match(src)
        if m:
            result.append(src)

    return result
    
def get_metadatas_as_convertprojectml(configuration_root):
    """
    Creates lines for convertprojectml file from metadata items and also adds
    version info to correct place. 
    @param configuration_root: Configuration root object which contains metadatas.
    @return: A list of metadata lines for convertprojectml.
    """
    metadatas = configuration_root.get_meta()
    metadata_line = []
    
    for metadata in metadatas:
        if metadata.ns == "http://www.s60.com/xml/confml/1" or metadata.ns == "http://www.s60.com/xml/confml/2":
            if metadata.tag == 'release':
                metadata_line.append("<" + metadata.tag + ">${convertproject.versioninfo}</" + metadata.tag + ">")
            elif metadata.tag == 'version':
                metadata_line.append("<" + metadata.tag + ">001</" + metadata.tag + ">")
            else:
                metadata_line.append("<" + metadata.tag + ">" + metadata.value + "</" + metadata.tag + ">")

        if metadata.ns == "http://www.nokia.com/xml/cpf-id/1":
            if metadata.attrs['name'] == 'sw_version':
                metadata_line.append('<cv:configuration-property name="' + metadata.attrs['name'] + '" value="${convertproject.versioninfo}" />')
            else:
                metadata_line.append('<cv:configuration-property name="' + metadata.attrs['name'] + '" value="' + metadata.attrs['value'] + '" />')

    return metadata_line
    
def get_layerlist_as_convertprojectml(configuration_root):
    """
    Creates lines for convertprojectml file from layer items in configurtion root
    @param configuration_root: Configuration root object
    @return: A list of layer lines for convertprojectml.
    """
    layer_line = []
    layer_list = configuration_root.list_configurations()
    
    for layer_item in layer_list:
        layer_line.append('<filter action="include_layer" data="' + layer_item + '"/>')
    
    return layer_line
    
def create_convertprojectml_file(conf_filename, conv_proj_filename, filepath,layerlist, metadatas, root_name):
    """
    Creates convertprojectml file for package
    @param conf_filename: configuration root filename
    @param conv_proj_filename: convertprojectml filename
    @param filepath: path where file is created
    @param layerlist: list of layers 
    @param metadatas: list of metadatas
    @param root_name: Name of configuration root
    """

    file_header = ['<?xml version="1.0" encoding="UTF-8"?>' + "\r\n", 
                   '<convertprojectml xmlns="http://www.s60.com/xml/convertprojectml/1">' + "\r\n\r\n",
                   '<targetProject path=""/>' + "\r\n",
                   "\t" + '<layer path="">' + "\r\n",
                   "\t\t" + '<file type="configuration_root" path="'+ conf_filename + '"']

    #root_name can be empty so we need to check is there some content.
    if root_name:
        file_header.append(' configuration_name="' + root_name + '"')                 
    file_header.append('>' + "\r\n")

    file_footer = ["\t\t" + '</file>' + "\r\n",
                   "\t" +'</layer>' + "\r\n",
                   '</convertprojectml>'+ "\r\n"]

    convert_file =  os.path.abspath(filepath + "/" + conv_proj_filename)
    fh = open(convert_file,'wb')
    fh.writelines(file_header)
    fh.write("\t\t\t" + '<meta xmlns:cv="http://www.nokia.com/xml/cpf-id/1">' + "\r\n")

    for meta_line in metadatas:
        fh.write("\t\t\t\t" + meta_line + "\r\n")
    fh.write("\t\t\t" + '</meta>' + "\r\n")

    for layer_line in layerlist:
        fh.write("\t\t\t" + layer_line + "\r\n")

    fh.writelines(file_footer)
    fh.close()
    
def main(argv=sys.argv):
    """ Pack (zip) the variant layers of a configuration. """
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)

    parser.add_option("-p", "--project",
                       dest="project",
                       help="Defines the location of current project. Default is the current working directory.",
                       default=".",
                       metavar="STORAGE")
    
    group = OptionGroup(parser, "Packvariant options",
                        "The packvariant action is intended for packing variant to a zip-file for integration purposes.")
    
    group.add_option("-c", "--configuration",
                        dest="configuration",
                        help="Name of the configuration wanted to be packed.",
                        metavar="CONFIG")
    
    group.add_option("-r", "--remote",
                        dest="remote",
                        help="Defines a location and a name of remote storage (ZIP)",
                        metavar="STORAGE")
    
    group.add_option("-l", "--convert-location",
                        dest="convertlocation",
                        help="Defines a location of convertprojectml file."
                        "Default location is <PROJECT>/convertpluginlayer/implml/",
                        default="/convertpluginlayer/implml/")
        
    parser.add_option_group(group)
    (options, _) = parser.parse_args(argv)
    
    cone_common.handle_common_options(options)
    
    # Check the passed options
    if not options.remote:      parser.error("Target where variant package is placed must be given")
    if not options.configuration:  parser.error("Configuration root to be packed must be given")
    
    try:
        target_storage = api.Storage.open(options.remote,'w', username=options.username, password=options.password)
        target_project = api.Project(target_storage)
        source_storage = api.Storage.open(options.project,'r', username=options.username, password=options.password)
 
        if not os.path.isdir(source_storage.get_path()):
            print "ERROR: --Project must be a directory. Terminating the program."
            sys.exit(1)
        
        source_project = api.Project(source_storage)
        source_config = get_active_root_if_necessary(source_project, options.configuration, 'source')
        source_config = source_project.get_configuration(source_config)
        fname, _ = os.path.splitext(options.configuration)
        conv_project_filename =  fname + ".convertprojectml"
        print "Packing configuration: %s" % options.configuration
        print "Source project: %s" % options.project
        print "Target project: %s" % options.remote
        
        # Adding all files in layers
        layer_list = find_variant_layers(source_config)

        for add_layer in layer_list:
            layer_config = source_project.get_configuration(add_layer)
            layer = layer_config.get_layer()
            path_part = layer.path + "/"
            target_project.import_configuration(layer_config)
            resource_list = layer_config.layer.list_all_resources(recurse=True)

            for single_resource in resource_list:
                parsed_path = path_part + single_resource
                if source_storage.is_resource(parsed_path):
                    logger.info("Adding file: %s" % parsed_path)
                    target_storage.import_resources([parsed_path], source_storage)
                if source_storage.is_folder(path_part + single_resource):
                    logger.info("Adding folder: %s" % parsed_path)
                    target_storage.create_folder(parsed_path)

        layer_list = get_layerlist_as_convertprojectml(source_config)
        metadata_list = get_metadatas_as_convertprojectml(source_config)
        if not source_storage.is_folder(os.path.normpath(options.convertlocation + "/")):
            source_storage.create_folder(os.path.normpath(options.convertlocation + "/"))
        create_convertprojectml_file(options.configuration,
                                     conv_project_filename,
                                     options.project + "/"+ options.convertlocation + "/" ,
                                     layer_list,
                                     metadata_list,
                                     source_config.get_name())

        target_storage.import_resources([os.path.normpath(options.convertlocation + "/" +conv_project_filename)], source_storage) 
    except Exception ,e:
        print "Could not create Zip archive: %s" % e
        sys.exit(2)

    try:
        target_storage.save()
        source_project.close()
        target_project.close()
        
        conv_path = (os.path.normpath(options.project + "/" + options.convertlocation + "/"))
        conv_file_path = (os.path.normpath(conv_path + "/" + conv_project_filename))
        
        os.remove(conv_file_path)
        os.removedirs(conv_path)
    except:
        pass  
        


if __name__ == "__main__":
    main()
