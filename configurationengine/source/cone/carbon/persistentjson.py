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
# @author Teemu Rytkonen
import re
import logging
import simplejson

""" cone specific imports """
from cone.public import persistence, exceptions, api, utils, container
from cone.carbon import model
from cone.carbon.resourcemapper import CarbonResourceMapper

MODEL                    = model

def dumps(obj, indent=True):
    """ Make sure that the object is mapped to an object in this model """
    mobj = obj._get_mapper('carbon').map_object(obj)
    writer = get_writer_for_class(mobj.__class__.__name__)
    dict = writer.dumps(mobj)
    # Return the data as dict, as it is urlencoded by client
    return dict

def loads(jsonstr):
    return CarbonReader().loads(jsonstr)


class ResourceListReader(persistence.ConeReader):
    """
    """ 
    def loads(self, jsonstr):
        """
        @param jsonstr: The json string to read. 
        """
        reslist = model.ResourceList()
        datadict = simplejson.loads(jsonstr)
        for configuration in datadict.get('configurations', []):
            reslist.add_resource(model.ConfigurationResource(**configuration))
        for featurelist in datadict.get('featurelists', []):
            reslist.add_resource(model.FeatureListResource(**featurelist))
        return reslist

class HasResourceReader(persistence.ConeReader):
    """
    """ 
    def loads(self, jsonstr):
        """
        @param jsonstr: The json string to read. 
        """
        try:
            datadict = simplejson.loads(jsonstr)
            return datadict.get('has_resource',False)
        except ValueError,e:
            logging.getLogger('cone').error("Failed to parser json from %s" % jsonstr)
            raise e


class CarbonWriter(persistence.ConeWriter):
    """
    """ 
    def dumps(self, obj):
        """
        @param obj: The object 
        """
        """ Make sure that the object is mapped to an object in this model """
        mobj = obj._get_mapper('carbon').map_object(obj)
        writer = get_writer_for_class(mobj.__class__.__name__)
        return writer.dumps(obj)


class CarbonReader(persistence.ConeReader):
    """
    """ 
    def loads(self, jsonstr):
        """
        @param xml: The xml which to read. reads only the first object. 
        """
        try:
            datadict = simplejson.loads(jsonstr)
            for key in datadict:
                reader = get_reader_for_elem(key)
                return reader.loads(datadict[key])
        except (SyntaxError, ValueError),e:
            utils.log_exception(logging.getLogger('cone'), "Json string parse raised exception: %s!" % (e))
            raise exceptions.ParseError("Json string %s parse raised exception: %s!" % (jsonstr,e))

class ConfigurationCreateWriter(CarbonWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this CarbonWriter supports writing
        of the given class name
        """
        return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        featurelists = []
        included = []
        # Remove the featurelists and configurations from the creation phase
#        resmapper = CarbonResourceMapper()
#        for confpath in obj.list_configurations():
#            config = obj.get_configuration(confpath)
#            if config.meta and config.meta.get('type') == 'featurelist':
#                featurelists.append(resmapper.map_confml_resource('featurelist',confpath))
#            elif config.meta and config.meta.get('type'):
#                included.append(resmapper.map_confml_resource(config.meta.get('type'),confpath))
#            else:
#                # ignore configs that are not carbon configs
#                pass

        configuration_dict = {'name' : obj.name,
                              'parent_path' : '',
                              'included' : included,
                              'description' : obj.desc or 'Needs description',
                              'configuration_type' : 'carbon',
                              'resource_type' : 'configuration',
                              'feature_lists' : featurelists, 
                               }
        
        return configuration_dict

class ConfigurationWriter(CarbonWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this CarbonWriter supports writing
        of the given class name
        """
        if classname=="CarbonConfiguration":
            return True
        else:
            return False

    def dumps(self, obj):
        if obj.meta:
            if obj.meta.get('type') == 'configurationroot':
                return self.dumps_root(obj)
            elif obj.meta.get('type') == 'configurationlayer':
                return self.dumps_layer(obj)
        raise Exception("Not supported CarbonConfigruration, %s" % obj)

    def dumps_root(self, obj):
        """
        @param obj: The Configuration object 
        """
        featurelists = []
        included = []
        resmapper = CarbonResourceMapper()
        for confpath in obj.list_configurations():
            config = obj.get_configuration(confpath)
            if config.meta:
                if config.meta.get('type') == 'featurelist':
                    featurelists.append(resmapper.map_confml_resource('featurelist',confpath))
                else:
                    included.append(resmapper.map_confml_resource(config.meta.get('type'),confpath))
            else:
                # This default case could also be identified as error
                included.append(confpath)

        configuration_dict = {'feature_lists': featurelists,
                             'parent_config': None, 
                             'configuration_name': obj.name, 
                             'version_identifier': obj.version_identifier, 
                             'included': included, 
                             'ref': obj.ref}
        
        return configuration_dict

    def dumps_layer(self, obj):
        """
        @param obj: The Configuration object 
        """
        configuration_dict = {'version_identifier': obj.version_identifier}
        
        datawriter = DataWriter()
        data = datawriter.dumps(obj)
        configuration_dict['data'] =  data
        
        return configuration_dict

class ConfigurationRootReader(CarbonReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="configurationroot":
            return True
        else:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        name = dict.get('configuration_name')
        path = name + ".confml"
        conf = model.CarbonConfiguration(dict.get('ref'), path=path, type='configurationroot')
        conf.name = name
        conf.version = dict.get('version_identifier')
        resmapper = CarbonResourceMapper()
        
        """ Read the featurelists as included configurations """
        for fealist in dict.get('feature_lists',[]):
            conf.include_configuration(resmapper.map_carbon_resource(fealist))
        """ Read the included configurations """
        for includedconfig in dict.get('included',[]):
            conf.include_configuration(resmapper.map_carbon_resource(includedconfig))
        return conf

class ConfigurationLayerReader(CarbonReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="configurationlayer":
            return True
        else:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        name = dict.get('configuration_name')
        path = name + "/root.confml"
        conf = model.CarbonConfiguration(dict.get('ref'), path=path, type='configurationlayer')
        conf.name = name
        
        conf.version = dict.get('version_identifier')
        
        """ Last read the data of this configuration and add it as a configuration """
        data_reader = DataReader()
        datacont = data_reader.loads(dict.get('data', {}))
        conf.add_configuration(datacont)
        return conf

class FeatureListCreateWriter(CarbonWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Feature list create writer is supported only explicitly
        """
        return False

    def dumps(self, obj):
        """
        @param obj: The FeatureList object 
        """
        """ Make sure that the object is mapped to an object in this model """
        mobj = obj._get_mapper('carbon').map_object(obj)
        featurelist_dict = {'type' : 'featurelist',
                            'flv_description' : mobj.desc or 'Needs description',
                            'version_identifier' : mobj.version_identifier
                            }
        if hasattr(mobj, 'responsible'):
            featurelist_dict['responsible'] = mobj.responsible
        return featurelist_dict

class FeatureListWriter(CarbonWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Feature list create writer is supported only explicitly
        """
        if classname == 'FeatureList':
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The FeatureList object 
        """

        featurelist_dict = {
                            'type' : 'featurelist',
                            'name' : obj.name,
                            'flv_description' : obj.desc or 'Needs description',
                            'path' : obj.path,
                            'features' : []
                            }
        if obj.meta.get('version_identifier'):
            featurelist_dict['version_identifier'] = obj.meta.get('version_identifier')
        # add all features of the featurelist
        for fearef in obj.list_features():
            feature = obj.get_feature(fearef)
            writer = FeatureWriter()
            feadict = writer.dumps(feature)
            featurelist_dict['features'].append(feadict)
        
        return featurelist_dict

class FeatureListReader(CarbonReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="featurelist":
            return True
        else:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        fealist_expanded            = dict.get('expanded')
        fealist_version             = dict.get('version_identifier')
        fealist_is_latest_version   = dict.get('is_latest_version')
        fealist_list_id             = dict.get('list_id')
        fealist_path                = dict.get('path')
        fealist_version_title       = dict.get('version_title')
        fealist_can_be_released     = dict.get('can_be_released')
        fealist_type                = dict.get('type')
        fealist_has_external_relations = dict.get('is_latest_version')
        
        # Create a configuration object from the featurelist
        conf = model.FeatureList(path='featurelists/'+fealist_version_title+'.confml')
        conf.meta.add('version_identifier', fealist_version)
        
        for feature in dict.get('features'):
            reader = FeatureReader()
            fea = reader.loads(feature)
            if fea != None:
                conf.add_feature(fea)
        
        for feafqr in conf.list_all_features():
            # Add empty data object to featurelist configuration
            conf.add_data(api.Data(fqr=feafqr))
            
        return conf


class FeatureWriter(CarbonWriter):
    CONFML_TO_CARBON_TYPE = {
                             'boolean'   : 'BOOLEAN',
                             'int'       : 'INTEGER',
                             'selection' : 'SELECTION',
                             'string'    : 'STRING',
                             None : None,
                             '' : ''
                             }
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Feature" or\
            classname=="CarbonBooleanSetting" or\
            classname=="CarbonIntSetting" or\
            classname=="CarbonStringSetting" or\
            classname=="CarbonSelectSetting"or\
            classname=="CarbonSetting":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Feature object 
        """
        """ Make sure that the object is mapped to an object in this model """
        mobj = obj._get_mapper('carbon').map_object(obj)
        
        featuredict = {'type' : 'feature',
                       'status' : 'APPROVED',
                       'title' : mobj.name,
                       'ref' : mobj.ref,
                       'description' : mobj.desc or 'Needs description',
                       'responsible' : None,
                       'value_type' : self.CONFML_TO_CARBON_TYPE[mobj.type],
                       'children' : []}
        if featuredict['value_type'] != None:
            featuredict['type_object'] = 's60_feature'
        if mobj.type == 'selection':
            featuredict['options'] = mobj.options.keys() 

        writer = FeatureWriter()
        for fearef in mobj.list_features():
            feaobj = obj.get_feature(fearef)
            childdict = writer.dumps(feaobj)
            featuredict['children'].append(childdict)
        return featuredict


class FeatureReader(CarbonReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="features":
            return True
        else:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        id = dict.get('id')
        name = dict.get('title')
        ref = dict.get('ref')
        ref = utils.resourceref.to_objref(ref)
        status = dict.get('status')
        value_type = dict.get('value_type')
        description = dict.get('description')
        
        if value_type == 'boolean':
            fea = model.CarbonBooleanSetting(ref, type=value_type)
        elif value_type == 'integer':
            fea = model.CarbonIntSetting(ref, type=value_type)
        elif value_type == 'string':
            fea = model.CarbonStringSetting(ref, type=value_type)
        elif value_type == 'selection':
            fea = model.CarbonSelectionSetting(ref, type=value_type)
            for option_name in dict.get('options'):
                fea.create_option(option_name, option_name)
        elif value_type == '':
            fea = model.CarbonFeature(ref, type=value_type)
        else:
            fea = model.CarbonFeature(ref)

        
        fea.name = name
        fea.status = status
        fea.desc = description
         
        for childdict in dict.get('children',[]):
            reader = FeatureReader()
            subfea = reader.loads(childdict)
            if subfea != None:
                fea.add_feature(subfea)
        return fea

class DataWriter(CarbonWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if  classname=="Data" or \
            classname=="DataContainer":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The DataContainer object 
        """
        datadict = {}
        for dataelem in obj._traverse(type=api.Data):
            if dataelem.get_value() != None:
                datadict[dataelem.get_fearef()] = map_confml2carbon_value(dataelem.get_value())
        return datadict


class DataReader(CarbonReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="data":
            return True
        else:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        datacont  = api.Configuration('confml/data.confml')
        for dataref in dict.keys():
            # Ignore null values
            if dict[dataref]:
                refs = []
                for elem in dataref.split('.'):
                    refs.append(utils.resourceref.to_objref(elem))
                newref = '.'.join(refs)
                dataelem = api.Data(fqr=newref, value=map_carbon2confml_value(dict[dataref]))
                datacont.add_data(dataelem)
        return datacont

def map_carbon2confml_value(value):
    if value == 'DEFINED':
        return 'true'
    elif value == 'UNDEFINED':
        return 'false'
    else:
        return value

def map_confml2carbon_value(value):
    if value == 'true':
        return 'DEFINED'
    elif value == 'false':
        return 'UNDEFINED'
    else:
        return value

def get_reader_for_elem(elemname, parent=None):
    for reader in CarbonReader.__subclasses__():
        if reader.supported_elem(elemname,parent):
            return reader()
    raise exceptions.ConePersistenceError("No reader for given elem %s under %s found!" % (elemname, parent))

def get_writer_for_class(classname):
    for writer in CarbonWriter.__subclasses__():
        if writer.supported_class(classname):
            return writer ()
    raise exceptions.ConePersistenceError("No writer for given class found! %s" % classname)
