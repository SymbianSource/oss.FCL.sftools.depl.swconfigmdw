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

class HeaderWriter(object):
    def __init__(self,output_file, output_obj):
        self.output_obj = output_obj
        self.output_file = output_file

    def write(self):
        header_guard = os.path.basename(self.output_file).upper()
        header_guard = header_guard.replace('/', '_').replace('\\', '_').replace('.', '_')
        lines = [
            "#ifndef %s" % header_guard,
            "#define %s" % header_guard,
            "",
            "#include <hcr.h>",
            "",
        ]
        
        # Sort by category UID to make testing easier
        categories = sorted(self.output_obj.categories, key=lambda c: c.category_uid)
        for i, category in enumerate(categories):
            lines.append('const HCR::TCategoryUid %s = 0x%08X;' % (category.name, category.category_uid))
            lines.append('')
            
            # Again, sort for testability
            settings = sorted(category.settings, key=lambda s: s.id)
            max_name_len = max([len(s.name) for s in settings])
            format = "const HCR::TElementId %%-%ds = 0x%%08X;" % max_name_len
            for setting in settings:
                if setting.comment: lines.append("// %s" % setting.comment)
                lines.append(format % (setting.name, setting.id))
            
            if i + 1 != len(categories):
                lines.append('')
                lines.append('// ' + 70 * '-')
                lines.append('')
            
        lines.extend([
            "",
            "#endif",
        ])
        
        f = open(self.output_file, 'wb')
        try:        f.write(os.linesep.join(lines))
        finally:    f.close()
