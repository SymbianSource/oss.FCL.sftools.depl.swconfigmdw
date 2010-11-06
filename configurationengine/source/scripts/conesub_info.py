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

import sys, zipfile, os
import re, fnmatch
import logging

from optparse import OptionParser, OptionGroup

import cone_common
from cone.public import api, plugin, utils, exceptions
from cone.confml import persistentconfml
from cone.storage.filestorage import FileStorage
from cone.report import report_util

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


VERSION = '1.0'


REPORT_SHORTCUTS = {
    'api': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_api_report_template.html'),
        'api_report.html',
        "Create a report of the configuration's ConfML API."),
    
    'value': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_value_report_template.html'),
        'value_report.html',
        "Create a report of the configuration's data values. Multiple "\
        "configurations can also be given using --configurations"),
    
    'value_csv': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_value_report_template.csv'),
        'value_report.csv',
        "Create a report of the configuration's data values (CSV format)."),
    
    'api_csv': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_api_report_template.csv'),
        'api_report.csv',
        "Create a report of the configuration's ConfML API (CSV format)."),
    
    'impl': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_impl_report_template.html'),
        'impl_report.html',
        'Create a report of all implementations in the configuration.'),
    
    'content': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_content_report_template.html'),
        'content_report.html',
        'Create a report of the content files in the configuration.'),
    'ctr_csv': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_ctr_report_template.csv'),
        'ctr_report.csv',
        'Create a report of CTR configurations (CSV format).'),
    'ctr': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'info_ctr_report_template.html'),
        'ctr_report.html',
        'Create a report of CTR configurations.'),
}

def main():
    """ Get information about project / configurations. """
    shortcut_container = report_util.ReportShortcutContainer(REPORT_SHORTCUTS,
                                                             None)
    
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",
                      action="append",
                      dest="configs",
                      help="Defines a configuration to use in report generation or info printout. "\
                           "May be defined more than once, but multiple configuration will only "\
                           "do anything if the report type supports them. If multiple configurations "\
                           "are not supported, the first one will be used",
                      metavar="CONFIG",
                      default=[])
    
    parser.add_option("--config-wildcard",\
                      action="append",
                      dest="config_wildcards",
                      help="Wildcard pattern for including configurations, e.g. product_langpack_*_root.confml",
                      metavar="WILDCARD",
                      default=[])
    
    parser.add_option("--config-regex",\
                      action="append",
                      dest="config_regexes",
                      help="Regular expression for including configurations, e.g. product_langpack_\\d{2}_root.confml",
                      metavar="REGEX",
                      default=[])
    
    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")

    info_group = OptionGroup(parser, 'Info options',
                    'The info functionality is meant for printing information about the       '\
                    'contents of a cpf/zip file or Configuration Project (folder). Two        '\
                    'separate use cases are currently supported:                              '\
                    '1. Printing basic information about a project or configuration to        '\
                    '   stdout.                                                               '\
                    '2. Creating a report of the contents of a configuration or configurations.')
    
    info_group.add_option("--report-type",
                   help="The type of the report to generate. This is a convenience "\
                        "switch for setting the used template.                     "\
                        "Possible values:                                        "\
                        + shortcut_container.get_shortcut_help_text(),
                   metavar="TYPE",\
                   default=None)
    
    info_group.add_option("--report",
                   help="The file where the configuration info report is written."\
                        "By default this value is determined by the used "\
                        "report type. Example: --report report.html.",
                   metavar="FILE",\
                   default=None)

    info_group.add_option("--template",
                   help="Template used in a report generation. By default "\
                        "this value is determined by the used report type. "\
                        "Example: --template report_template.html.",
                   metavar="FILE",\
                   default=None)
    
    info_group.add_option("--impl-filter",
                   help="The pattern used for filtering implementations for the "\
                        "report. See the switch --impl in action generate for "\
                        "more info. ",
                   metavar="PATTERN",
                   default='.*')
    
    info_group.add_option("--view-file",
                   help="External ConfML file containing the view used for filtering "\
                        "the features listed in the setting value report. The first view "\
                        "defined in the file will be used.",
                   metavar="FILE",
                   default=None)
    
    info_group.add_option("--print-active-root",
                   action="store_true",
                   help="Print active root in the current project and exit.")
    
    parser.add_option_group(info_group)
    
    (options, args) = parser.parse_args()
    cone_common.handle_common_options(options)
    
    if options.print_active_root:
        print_active_root(options)
        sys.exit(0)
    
    if not shortcut_container.is_valid_shortcut(options.report_type):
        parser.error("Invalid report type: %s" % options.report_type)
    if (options.report_type or options.template) and \
        (not options.configs and not options.config_wildcards and not options.config_regexes):
        parser.error("Report type or template specified but configuration(s) not given!")
    if options.view_file and not os.path.isfile(options.view_file):
        parser.error("No such file: %s" % options.view_file)
    
    # Load view from the specified file if necessary
    view = None
    if options.view_file:
        try:
            view = _load_view_from_file(options.view_file)
            print "Loaded view '%s' from '%s'" % (view.get_name(), options.view_file)
        except ViewLoadError, e:
            print e
            sys.exit(1)
    
    current = api.Project(api.Storage.open(options.project,"r", username=options.username, password=options.password))
    print "Opened project in %s" % options.project
    
    # Get a list of configurations if necessary
    config_list = None
    if options.configs or options.config_wildcards or options.config_regexes:
        try:
            config_list = cone_common.get_config_list_from_project(
                project          = current,
                configs          = options.configs,
                config_wildcards = options.config_wildcards,
                config_regexes   = options.config_regexes)
        except cone_common.ConfigurationNotFoundError, e:
            parser.error(str(e))
        
        # Specifying configurations using --configuration should always either result
        # in an error or a configuration, so if there are no configurations, it
        # means that the user specified only wildcards and/or patterns, and none
        # matched
        if len(config_list) == 0:
            parser.error("No matching configurations for wildcard(s) and/or pattern(s).")
    
    
    if config_list is not None:
        # One or more configurations have been specified
        
        if options.report_type is not None or options.template is not None:
            # Generating a report
            
            # Create a list of configurations
            configs = []
            for config_name in config_list:
                configs.append(current.get_configuration(config_name))
            
            # Generate the report
            if options.report_type: report_name = options.report_type + '_info'
            else:                   report_name = 'info'
            template, report = shortcut_container.determine_template_and_report(
                options.report_type,
                options.template,
                options.report,
                report_name)
            data_providers = {'impl_data'   : ImplDataProvider(configs[0], options.impl_filter),
                              'api_data'    : ApiDataProvider(configs[0]),
                              'content_data': ContentDataProvider(configs[0]),
                              'value_data'  : ValueDataProvider(configs, view),
                              'ctr_data'    : CtrDataProvider(configs)}
            report_util.generate_report(template, report, {'data': ReportDataProxy(data_providers)}, [ROOT_PATH])
        else:
            # Printing configuration info
            config_name = config_list[0]
            config = current.get_configuration(config_name)
            print "Opened configuration %s" % config_name
            print "Features %s" % len(config.get_default_view().list_all_features())
            print "Impl files %s" % len(plugin.get_impl_set(config).list_implementation())
        
    else:
        print "Configurations in the project."
        configlist = current.list_configurations()
        configlist.sort()
        for config in configlist:
            print config
    if current: current.close()

def print_active_root(options):
    storage = api.Storage.open(options.project,"r", username=options.username, password=options.password)
    active_root = storage.get_active_configuration()
    if active_root:
        print "Active root: %s" % active_root
    else:
        print "No active root."
    

# ============================================================================
# Report data proxy and data providers
# ============================================================================

class ReportDataProxy(object):
    """
    Proxy object for loading report data on demand.
    
    It is used so that e.g. when generating an API report, the
    implementations are not unnecessarily loaded. The class utilizes
    ReportDataProviderBase objects to handle the actual data generation,
    and logs any exceptions that happen there.
    """
    def __init__(self, data_providers):
        assert isinstance(data_providers, dict), "data_providers must be a dict!"
        self._data_providers = data_providers
    
    def __getattr__(self, attrname):
        if attrname in self._data_providers:
            try:
                return self._data_providers[attrname].get_data()
            except Exception, e:
                utils.log_exception(logging.getLogger('cone'),
                                    "Exception getting %s: %s" % (attrname, e))
        else:
            return super(ReportDataProxy, self).__getattr__(attrname)

class ReportDataProviderBase(object):
    """
    Report data provider base class for lazy-loading of report data.
    """
    def get_data(self):
        """
        Return the report data.
        
        The data is generated on the first call to this, and later the
        cached data is returned.
        """
        CACHE_ATTRNAME = "__datacache"
        if hasattr(self, CACHE_ATTRNAME):
            return getattr(self, CACHE_ATTRNAME)
        else:
            data = self.generate_data()
            setattr(self, CACHE_ATTRNAME, data)
            return data
    
    def generate_data(self):
        """
        Generate the actual report data. Called when get_data() is called
        the first time.
        """
        raise NotImplementedError()

# ----------------------------------------------------------------------------

class ApiDataProvider(ReportDataProviderBase):
    def __init__(self, config):
        self._config = config
    
    def generate_data(self):
        columns = {'fqr':'Full reference',
                   'name':'Name',
                   'type':'Type',
                   'desc':'Description',
                   }
        data = self._get_feature_api_data(self._config, columns)
        data.sort(key=lambda item: item['fqr'])
        return {'columns'   : columns,
                'data'      : data}
    
    @classmethod
    def _get_feature_api_data(cls, config, column_dict):
        # Traverse through all features in the api
        # and construct the data rows
        data = []
        storageroot = os.path.abspath(config.get_storage().get_path())
        for elem in config.get_default_view().get_features('**'):
            elemfile = os.path.join(storageroot,elem._obj.find_parent(type=api.Configuration).get_full_path())
            #print "elemfile %s " % elemfile
            featurerow = {'file': elemfile}
            
            for col in column_dict:
                try:
                    featurerow[col] = getattr(elem,col) or ''
                except AttributeError,e:
                    #logging.getLogger('cone').warning('Could not find attribute %s from %s' % (col, elem.fqr))
                    featurerow[col] = ''
            data.append(featurerow)
        return data


class ImplDataProvider(ReportDataProviderBase):
    def __init__(self, config, impl_filters):
        self._config = config
        self._impl_filters = impl_filters
        
    def generate_data(self):
        impl_set = plugin.filtered_impl_set(self._config, [self._impl_filters or '.*'])
        return impl_set.get_all_implementations()


class ContentDataProvider(ReportDataProviderBase):
    def __init__(self, config):
        self._config = config
        
    def generate_data(self):
        class Entry(object):
            pass
        data = []
        layered_content = self._config.layered_content()
        for ref in sorted(layered_content.list_keys()):
            entry = Entry()
            entry.file = ref
            entry.actual_files = layered_content.get_values(ref)
            data.append(entry)
        return data

class CtrDataProvider(ReportDataProviderBase):
    def __init__(self, configs):
        self._configs = configs
    
    def generate_data(self):
        lines = []
        for config in self._configs:
            lines.extend(self._get_config_data(config))
        return lines
    
    def _get_config_data(self, config):
        ctrs = []
        config_name = config.get_name()
        ctrs_in_meta_index = config.meta.find_by_attribute('name','based_on_ctr')
        ctrs = config.meta[ctrs_in_meta_index].attrs['value'].split(',')
        lines = []
        ppbit = language = country = uda = ''
        for c in config.list_configurations():
            m = re.search(r'/ppbit/ppbit_(.*)/', c)
            if m: ppbit = m.group(1)
            m = re.search(r'/language/(.*)/', c)
            if m: language = m.group(1)
            m = re.search(r'/country/(.*)/', c)
            if m: country = m.group(1)
            m = re.search(r'/uda/(.*)/', c)
            if m: uda = m.group(1)
        for ctr in ctrs:
            data = {'ctr_code':     ctr,
                    'config_name':  config_name,
                    'ppbit':        ppbit,
                    'language':     language,
                    'country':      country,
                    'uda':          uda
                    }
            lines.append(data)
        return lines
        

class ValueDataProvider(ReportDataProviderBase):
    
    class FeatureGroup(object):
        def __init__(self, name, features):
            self.name = name
            self.features = features
    
    class Feature(object):
        def __init__(self, **kwargs):
            self.ref  = kwargs['ref']
            self.name = kwargs['name']
            self.type = kwargs['type']
            self.desc = kwargs['desc']
            self.options = kwargs['options']
    
    class Config(object):
        def __init__(self, name, path, values, refs):
            self.name = name
            self.path = path
            self.values = values
            self.refs = refs
    
    class SequenceColumn(object):
        def __init__(self, ref, name, type):
            self.ref = ref
            self.name = name
            self.type = type
        
        def __eq__(self, other):
            if type(self) == type(other):
                for varname in ('ref', 'name', 'type'):
                    if getattr(self, varname) != getattr(other, varname):
                        return False
                return True
            else:
                return False
        
        def __ne__(self, other):
            return not (self == other)
        
        def __repr__(self):
            return "SequenceColumn(ref=%r, name=%r, type=%r)" \
                % (self.ref, self.name, self.type)
    
    class SequenceData(object):
        def __init__(self, columns, rows):
            self.columns = columns
            self.rows = rows
            self.is_sequence_data = True
        
        def __eq__(self, other):
            if type(self) == type(other):
                for varname in ('columns', 'rows'):
                    if getattr(self, varname) != getattr(other, varname):
                        return False
                return True
            else:
                return False
        
        def __ne__(self, other):
            return not (self == other)
        
        def __repr__(self):
            return "SequenceData(columns=%r, rows=%r)" \
                % (self.columns, self.rows)
    
    
    def __init__(self, configs, view):
        assert len(configs) > 0, "configs must contain at least one configuration!"
        self._configs = configs
        self._view = view
    
    def generate_data(self):
        configs = self._configs
        view = self._view
        
        # Get the feature list from the first configuration
        feature_groups = self._get_feature_groups(self._configs[0], view)
        
        # Load setting values from all configurations
        output_configs = [] # List of self.Config objects, not api.Configuration objects
        for i, config in enumerate(self._configs):
            print "Loading configuration %s (%d of %d)" % (config.get_path(), i + 1, len(self._configs))
            dview = config.get_default_view()
            
            values = {}
            for group in feature_groups:
                for entry in group.features:
                    try:
                        feature = dview.get_feature(entry.ref)
                        values[entry.ref] = self._resolve_value(feature)
                    except exceptions.NotFound:
                        pass
            # Get the feature refs from last layer
            last_layer_refs = set(config.get_last_configuration().list_leaf_datas())
            output_configs.append(self.Config(config.get_name(), config.get_path(), values, last_layer_refs))
        
        # Add a 'modified' attribute to all features
        for group in feature_groups:
            for feature in group.features:
                modified = False
                first_value_set = False
                first_value = None
                for output_config in output_configs:
                    if feature.ref not in output_config.values:
                        continue
                    
                    if not first_value_set:
                        first_value = output_config.values[feature.ref]
                        first_value_set = True
                    else:
                        if output_config.values[feature.ref] != first_value:
                            modified = True
                            break
                
                feature.modified = modified
        
        return {'feature_groups' : feature_groups,
                'configs'        : output_configs}
    
    def _resolve_value(self, feature):
        """
        Resolve the value of the given feature (must be a data proxy).
        
        @param feature: The feature whose value is to be resolved.
        @return: The resolved value (value directly from the feature, name of a selection option,
            or a SequenceData object.
        """
        assert isinstance(feature, api._FeatureDataProxy)
        
        if isinstance(feature._obj, api.FeatureSequence):
            return self._get_sequence_data(feature)
        
        return self._resolve_option_value(feature, feature.get_value())
    
    def _resolve_option_value(self, feature, value):
        """
        Resolve an option value for the given feature.
        
        @param feature: The feature, can be a data proxy or the feature object itself.
        @param value: The value to resolve.
        @return: The resolved value; the name of the selected option if possible,
            otherwise the value that was passed in.
        """
        if isinstance(feature, api._FeatureDataProxy):
            feature = feature._obj
        
        for option in self._get_options(feature):
            if option.get_value() == value:
                return option.get_name()
        
        return value
    
    def _get_sequence_data(self, seq_feature):
        """
        Return a SequenceData object based on the given sequence feature.
        """
        assert isinstance(seq_feature, api._FeatureDataProxy)
        assert isinstance(seq_feature._obj, api.FeatureSequence)
        
        sub_feature_objs = []
        columns = []
        for obj in seq_feature._obj._objects():
            if isinstance(obj, api.Feature):
                col = self.SequenceColumn(obj.ref, obj.name, obj.type)
                columns.append(col)
                sub_feature_objs.append(obj)
        
        rows = []
        for value_row in seq_feature.get_value():
            row = {}
            for index, value_item in enumerate(value_row):
                ref = columns[index].ref
                sub_feature = sub_feature_objs[index]
                value = self._resolve_option_value(sub_feature, value_item)
                row[ref] = value
            rows.append(row)
        
        return self.SequenceData(columns, rows)
        
    def _get_feature_groups(self, config, view):
        """
        Return a list of FeatureGroup objects generated based on the given configuration and view.
        @param configuration: The configuration to use.
        @param view: The view to use. Can be None, in which case all features in the
            configuration will be used.
        """
        feature_groups = []
        
        if view is None:
            feature_list = self._get_feature_list(config.get_default_view().get_features('**'))
            feature_groups = [self.FeatureGroup('All settings', feature_list)]
        else:
            # Populate the view so that it contains the settings and
            # get_features() can be used
            config._add(view)
            view.populate()
            
            # Recursively collect a flattened list of all groups
            def visit_group(group, name_prefix):
                name = None
                
                # Ignore the name for the view, record only group-level names
                # (the view cannot directly contain settings according to the
                # spec, they need to be inside a group)
                if not isinstance(group, api.View):
                    if name_prefix: name = name_prefix + ' -- ' + group.get_name()
                    else:           name = group.get_name()
                
                # Add features if necessary
                features = self._get_feature_list(group.get_features('*'))
                if len(features) > 0:
                    feature_groups.append(self.FeatureGroup(name, features))
                
                # Recurse to child groups
                for child in group._objects():
                    if isinstance(child, api.Group):
                        visit_group(child, name)
            
            visit_group(view, None)
         
        return feature_groups
    
    def _get_feature_list(self, feature_objects):
        """
        Return a list of feature data entries based on the given features.
        @param feature_objects: List of api._FeatureDataProxy objects, e.g.
            the output of api.Group.get_features().
        @return: List of ValueDataProvider.Feature objects.
        """
        refs = set()
        feature_list = []
        for elem in feature_objects:
            # Ignore elements with no type (they are not settings)
            if not hasattr(elem, 'type') or elem.type in (None, ''):
                continue
            
            # For sequences don't include sub-settings, only the
            # sequence settings themselves
            feature = self._get_parent_sequence_or_self(elem._obj)
            ref = feature.fqr
            
            # Don't add if it's already in the list
            if ref in refs: continue
            else:           refs.add(ref)
            
            feature_data = self.Feature(
                ref  = ref,
                name = feature.name,
                type = feature.type,
                desc = feature.desc,
                options = self._get_options(feature))
            feature_list.append(feature_data)
        return feature_list
    
    def _get_options(self, feature):
        """
        Return a list of api.Option objects for the given feature.
        """
        if isinstance(feature, api._FeatureDataProxy):
            feature = feature._obj
        
        options = []
        for obj in feature._objects():
            if isinstance(obj, api.Option):
                options.append(obj)
        return options
        
    def _get_parent_sequence_or_self(self, feature):
        """
        Return the parent sequence of the given feature, or the feature
        itself if it is not a sequence sub-setting.
        """
        current = feature._parent
        while current is not None:
            if isinstance(current, api.FeatureSequence):
                return current
            current = current._parent
        return feature


# ============================================================================
# Helper functions
# ============================================================================

class ViewLoadError(RuntimeError):
    """Exception raised if _load_view_from_file() fails"""
    pass

def _load_view_from_file(filename):
    """
    Load the last view from the given ConfML file.
    @raise ViewLoadError: An error occurred when loading the file.
    """
    file_abspath = os.path.abspath(filename)
    file_dir = os.path.dirname(file_abspath)
    file_name = os.path.basename(file_abspath)
    
    # Open the view file inside a "project" so that XIncludes are
    # handled properly
    try:
        view_project = api.Project(FileStorage(file_dir, 'r'))
        view_config = view_project.get_configuration(file_name)
        views = view_config._traverse(type=api.View)
    except Exception, e:
        import traceback
        logging.getLogger('cone').debug(traceback.format_exc())
        raise ViewLoadError("Error parsing view ConfML file: %s" % e)
    
    if len(views) == 0:
        raise ViewLoadError("No views in specified view ConfML file '%s'" % filename)
    elif len(views) == 1:
        return views[0]
    else:
        print "Found %d view(s) in file '%s', using the last one" % (len(views), filename)
        return views[-1]

# ============================================================================

if __name__ == "__main__":
    main()
