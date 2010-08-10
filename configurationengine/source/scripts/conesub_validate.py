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

import sys, os, shutil
import logging
from optparse import OptionParser, OptionGroup
import cone_common
from cone.report import report_util
from cone.public import api, exceptions, utils, plugin, parsecontext
import cone.validation.parsecontext
import cone.validation.schemavalidation
import cone.validation.implmlvalidation
import cone.validation.confmlvalidation
from cone.validation.problem_type_filter import ProblemTypeFilter

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

VERSION     = '1.0'

logger    = logging.getLogger('cone')

REPORT_SHORTCUTS = {
    'xml': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'validation_report_template.xml'),
        'validation_report.xml',
        "Create a validation report of xml type."),
    
    'html': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'validation_report_template.html'),
        'validation_report.html',
        "Create a validation report of html type."),
}

def main():
    """ Validate a configuration, or individual confml/implml files. """
    shortcut_container = report_util.ReportShortcutContainer(REPORT_SHORTCUTS,
                                                             'html')

    parser = OptionParser(version="ConE validate %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",
                        dest="configuration",
                        help="Defines the name of the configuration for the action",
                        metavar="CONFIG")

    parser.add_option("-p", "--project",
                       dest="project",
                       default=".",
                       help="defines the location of current project. Default is the "\
                            "current working directory.",
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Validate options',
                        'The validate action is intended for performing validation on a     '\
                        'configuration or individual files.                                 ')
    
    group.add_option('--confml-file',
                     action="append",
                     help='Validate only the given single ConfML file.',
                     metavar="FILE",
                     default=None)
    
    group.add_option('--implml-file',
                     action="append",
                     help='Validate only the given single ImplML file.',
                     metavar="FILE",
                     default=None)
        
    group.add_option("--template",
                     help="Template used in report generation. "\
                          "Example: --template=report_template.html.",
                     metavar="FILE",
                     default=None)
        
    group.add_option("--report-type",
                   help="The type of the report to generate. This is a convenience "\
                        "switch for setting the used template. If --template is given, this option has no effect. "\
                        "Possible values:                                        "\
                        + shortcut_container.get_shortcut_help_text(),
                   metavar="TYPE",\
                   default=None)    
    
    group.add_option("--report",
                   help="Specifies the location of the validation report. "\
                        "Example --report=report.html.",
                   metavar="FILE",
                   default=None)
    
    group.add_option("--dump-schema-files",
                     help="Dump the XML schema files used for validation into the specified directory.",
                     metavar="DIR",
                     default=None)

    group.add_option("--exclude-filter",
                     action="append",
                     help="Exclude validation problems by given filter. "\
                          "Examples: --exclude-filter=schema, --exclude-filter=schema.implml, --exclude-filter=schema.confml, --exclude-filter=schema.implml.ruleml",
                     default=None)

    group.add_option("--include-filter",
                     action="append",
                     help="Include validation problems by given filter."\
                          "Examples: --include-filter=schema.implml, --include-filter=schema.implml.ruleml",
                     default=None)

    parser.add_option_group(group)
    (options, _) = parser.parse_args()
    
    cone_common.handle_common_options(options)
    
    if not shortcut_container.is_valid_shortcut(options.report_type):
        parser.error("Invalid report type: %s" % options.report_type)
            
    if options.dump_schema_files:
        dump_dir = options.dump_schema_files
        print "Dumping XML schema files to '%s'" % dump_dir
        
        cone.validation.schemavalidation.dump_schema_files(dump_dir)
        return
    
    pt_filter = ProblemTypeFilter(includes = options.include_filter or [],
                               excludes = options.exclude_filter or [])
    
    problems = []
    if options.confml_file or options.implml_file:
        if options.confml_file:
            
            func = cone.validation.schemavalidation.validate_confml_data
            for file in options.confml_file:
                problems.extend(validate_file(file, func))
        if options.implml_file:
            func = cone.validation.schemavalidation.validate_implml_data
            for file in options.implml_file:
                problems.extend(validate_file(file, func))
    else:
        problems = validate_configuration(options.project, options.configuration, pt_filter)
    
    if problems is not None:
        filters = {'filter_by_severity':filter_by_severity}
        problems = pt_filter.filter(problems)
        
        print "Total %d problem(s) after filtering" % len(problems)
        
        print "Generating report..."
        problems.sort(key=lambda p: (p.severity, p.file, p.line))
        template, report = shortcut_container.determine_template_and_report(
            options.report_type,
            options.template,
            options.report,
            'validation_report')
        report_util.generate_report(template, report, {'problems': problems},extra_filters=filters)

def extend_without_duplicates(source, target):
    for item in source:
        if item not in target:
            target.append(item)

def validate_file(filename, validator_func):
    if not os.path.isfile(filename):
        print "'%s' does not exist or is not a file!" % filename
        return
    else:
        print "Validating file '%s'" % filename
    
    f = open(filename, 'rb')
    try:        data = f.read()
    finally:    f.close()
    
    problems = []
    try:
        validator_func(data)
    except exceptions.ParseError, e:
        problems.append(api.Problem.from_exception(e))
    print "Found %d problem(s)" % len(problems)
    
    for p in problems:
        p.file = filename
    return problems

def validate_configuration(project_path, config_path, problem_type_filter):
    print "Project:       %s" % project_path
    try:
        project = api.Project(api.Storage.open(project_path, 'r'))
    except exceptions.StorageException:
        print "No such project."
        return
    
    confml_parse_context = cone.validation.parsecontext.ValidationParseContext()
    parsecontext.set_confml_context(confml_parse_context)
    
    if config_path is None:
        config_path = project.get_storage().get_active_configuration()
        if config_path is None:
            print "Project does not have an active configuration, please specify the configuration using --configuration."
            return
    print "Configuration: %s" % config_path
    
    try:
        config  = project.get_configuration(config_path)
    except exceptions.NotFound:
        print "No such configuration in project."
        return
    
    result = []
    
    
    print "Finding ConfML files in configuration..."
    configs = config._traverse(type=api.Configuration)
    print "%d ConfML file(s)" % len(configs)
    print "%d problem(s) while parsing" % len(confml_parse_context.problems)
    result.extend(confml_parse_context.problems)
    
    # Schema-validate ConfML files if not filtered out
    if problem_type_filter.match('schema.confml'):
        print "Performing XML schema validation on ConfML files..."
        schema_problems = cone.validation.schemavalidation.validate_confml_file(config, config_path)
        for conf in configs:
            path = conf.get_full_path()
            problems = cone.validation.schemavalidation.validate_confml_file(config, path)
            schema_problems.extend(problems)
        print "%d problem(s)" % len(schema_problems)
        
        # Add the schema problems with duplicates removed, since XML parse
        # errors might have already been recorded in the ConfML parsing phase
        extend_without_duplicates(source=schema_problems, target=result)
    
    
    # Validate the ConfML model if not filtered out
    validator_classes = cone.validation.confmlvalidation.get_validator_classes(problem_type_filter)
    if validator_classes:
        print "Validating ConfML model..."
        model_problems = cone.validation.confmlvalidation.validate_configuration(config, validator_classes).problems
        print "%d problem(s)" % len(model_problems)
        result.extend(model_problems)
        
    
    print "Finding ImplML files in configuration..."
    impls = []
    for file in config.get_layer().list_implml():
        if plugin.ImplFactory.is_supported_impl_file(file):
            impls.append(file)
    print "Found %d supported files" % len(impls)
    
    # Schema-validate ImplML files if not filtered out
    if problem_type_filter.match('schema.implml'):
        print "Performing XML schema validation on ImplML files..."
        schema_problems = []
        for impl in impls:
            probs = cone.validation.schemavalidation.validate_implml_file(config, impl)
            schema_problems.extend(probs)
        print "%d problem(s)" % len(schema_problems)
        result.extend(schema_problems)
    
    # Validate the ImplML model if not filtered out
    if problem_type_filter.match('model.implml'):
        print "Parsing implementations..."
        implml_parse_context = cone.validation.parsecontext.ValidationParseContext()
        parsecontext.set_implml_context(implml_parse_context)
        impl_set = plugin.create_impl_set(impls, config)
        
        # Add the model-level problems with duplicates removed, since XML parse
        # errors might have already been recorded in the schema validation phase
        extend_without_duplicates(source=implml_parse_context.problems, target=result)
        
        
        validator_classes = cone.validation.implmlvalidation.get_validator_classes(problem_type_filter)
        if validator_classes:
            print "Validating implementations..."
            impl_problems = cone.validation.implmlvalidation.validate_impl_set(impl_set, config, validator_classes)
            print "%d problem(s)" % len(impl_problems)
            result.extend(impl_problems)
    
    return result


def filter_by_severity(problems, severity):
    """
    Filter problems by severity
    """
    return [p for p in problems if p.severity == severity]

if __name__ == "__main__":
    main()
