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
import urllib
import logging
from jinja2 import Environment, FileSystemLoader, Template
from cone.public import utils

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger('cone.report_util')

class ReportShortcut(object):
    def __init__(self, template_file, report_file, description):
        self.template_file = template_file
        self.report_file = report_file
        self.description = description

class ReportShortcutContainer(object):
    """
    Container for report shortcuts.
    
    A report shortcut describes a pre-defined report option that
    has a default template, report file and description. The shortcut
    container holds a set of shortcuts and can be used to generate
    
    """
    def __init__(self, shortcuts, default_shortcut):
        """
        @param shortcuts: The shortcuts, a dictionary mapping shortcut
            names to ReportShortcut objects.
        @param default_shortcut: The default shortcut name to use
        """
        if not isinstance(shortcuts, dict):
            raise ValueError("'shortcuts' must a dictionary (%s given)!" % type(shortcuts))
        if default_shortcut is not None and default_shortcut not in shortcuts:
            raise ValueError("'default_shortcut' must be either None or exist ing 'shortcuts'!")
        self.shortcuts = shortcuts
        self.default_shortcut = default_shortcut
    
    def get_shortcut_help_text(self):
        """
        Create the text to append to the option description for the
        option used to specify the used shortcut.
        """
        shortcuts_text = []
        refs = sorted(self.shortcuts.keys())
        if refs:
            for ref in refs:
                sc = self.shortcuts[ref]
                text = "%s - %s" % (ref, sc.description)
                COLUMN_WIDTH = (80 - 25)
                space_count = COLUMN_WIDTH - (len(text) % COLUMN_WIDTH)
                shortcuts_text.append(text + space_count * ' ')
        else:
            shortcuts_text.append("None")
        shortcuts_text = '\n'.join(shortcuts_text)
        return shortcuts_text
    
    def is_valid_shortcut(self, shortcut):
        """
        Return whether the given shortcut is valid within the context
        of this container.
        """
        return shortcut is None or shortcut in self.shortcuts
    
    def determine_template_and_report(self, shortcut, template_file, report_file, report_file_name_without_ext):
        """
        Determine the actual template and report files based on the shortcuts
        and given options.
        @param shortcut: The used shortcut or None.
        @param template_file: Explicitly given template file or None.
        @param report_file: Explicitly given report file or None.
        @param report_file_name_without_ext: Prefix used to determine the
            report file name if the template was explicitly given, but the
            report file was not. E.g. if this is 'test' and the explicitly
            given template file is 'my_template.html', the report file would
            be 'test.html'.
        @return: Tuple (template_file, report_file) specifying the actual
            template and report files.
        """
        actual_shortcut      = None
        actual_template_file = None
        actual_report_file   = None
        
        # Handle report shortcut (set to default or check the given one)
        if not shortcut:
            actual_shortcut = self.default_shortcut
        else:
            actual_shortcut = shortcut
        
        # Determine template file
        if template_file:
            actual_template_file = template_file
        else:
            actual_template_file = self.shortcuts[actual_shortcut].template_file
        
        # Determine report output file
        if report_file:
            actual_report_file = report_file
        else:
            if template_file:
                # Determine report file name based on the template file name
                # if the template was explicitly given
                actual_report_file = report_file_name_without_ext + os.path.splitext(template_file)[1]
            else:
                actual_report_file = self.shortcuts[actual_shortcut].report_file
        
        return actual_template_file, actual_report_file

def generate_report(template_file, report_file, report_data):
    """
    Generate a report based on the given template file, report file
    and data dictionary.
    @param template_file: Path to the template file to use.
    @param report_file: Path to the output report file.
    @param report_data: The report data dictionary used when rendering
        the report from the template.
    @return: True if successful, False if not.
    """
    log.debug('generate_report(template_file=%r, report_file=%r, <data>)' % (template_file, report_file))
    if not isinstance(report_data, dict):
        raise ValueError("report_data must be a dictionary!")
    
    try:
        template_file = os.path.abspath(template_file)
        
        loader = FileSystemLoader([os.path.dirname(template_file), ROOT_PATH])
        env = Environment(loader=loader)
        _set_default_filters(env)
        
        template = env.get_template(os.path.basename(template_file))
        file_string = template.render(report_data)
        
        # Create directories for the report
        report_dir = os.path.dirname(report_file)
        if report_dir != '' and not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        # Write the rendered report to file
        f = open(report_file, 'wb')
        try:        f.write(file_string.encode('utf-8'))
        finally:    f.close()
        
        print "Generated report to '%s'" % report_file
        return True
    except Exception, e:
        utils.log_exception(log, "Failed to generate report: %s %s" % (type(e), e))
        return False

def _set_default_filters(env):
    """
    Set default filters to the given Jinja environment
    """
    env.filters['xml_charref_replace'] = lambda value: unicode(value).encode('ascii', 'xmlcharrefreplace')
    env.filters['pathname_to_url'] = lambda value: urllib.pathname2url(value)
    env.filters['csv_escape'] = _csv_escape
    env.filters['csv_escape_partial'] = lambda value: unicode(value).replace('"', '""')

def _csv_escape(value):
    """
    Escape a string value so that it can be used as a field in a CSV file.
    """
    value = unicode(value)
    
    needs_quoting = False
    for special_char in '",\n':
        if special_char in value:
            needs_quoting = True
    
    if needs_quoting:
        if '"' in value:
            value = value.replace('"', '""')
        value = '"' + value + '"'
    
    return value
