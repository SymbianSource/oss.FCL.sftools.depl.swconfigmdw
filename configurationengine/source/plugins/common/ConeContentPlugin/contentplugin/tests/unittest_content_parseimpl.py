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

import unittest
import os, shutil
import sys
import pkg_resources 
try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

try:
	pkg_resources.require('ConeContentPlugin')
except pkg_resources.DistributionNotFound:
	import __init__
		
from contentplugin import contentmlparser


invalidxml_string = '<?xml version="1.0" encoding="UTF-8"?><content xmlns="http://www.s60.com/xml/content/1">'

contentml_string = \
'''<?xml version="1.0" encoding="UTF-8"?>
<content xmlns="http://www.s60.com/xml/content/1">
    <tag name='target' value='core'/>
    <tag name='target' value='rofs3'/>
    <tag name='test' value='foo'/>
	<desc>Description field text</desc>
	<input dir="test">
		<include pattern="prod"/>
		<exclude pattern=".svn"/>
	</input>
	<output dir="content" someother="sss"/>
</content>'''

contentml_files_string = '''<?xml version="1.0" encoding="UTF-8"?>
<content xmlns="http://www.s60.com/xml/content/1">
    <desc>Description field text</desc>
    <input dir="test">
      <include files="test/foobar.txt, test/bar.txt"/>
    </input>
    <output dir="content" someother="sss" flatten="true"/>
</content>
'''

contentml_string_with_phase = \
'<?xml version="1.0" encoding="UTF-8"?>'\
'<content xmlns="http://www.s60.com/xml/content/1" phase="pre">'\
'  <desc>Description field text</desc>'\
'  <input dir="test">'\
'    <include pattern="prod"/>'\
'    <exclude pattern=".svn"/>'\
'  </input>'\
'  <output dir="content" someother="sss"/>'\
'</content>'


contentml_brief = \
'<?xml version="1.0" encoding="UTF-8"?>'\
'<content xmlns="http://www.s60.com/xml/content/1">'\
'	<input dir="test"/>'\
'	<output dir="content" someother="sss"/>'\
'</content>'

contentml_brief2 = \
'<?xml version="1.0" encoding="UTF-8"?>'\
'<content xmlns="http://www.s60.com/xml/content/1">'\
'</content>'


contentml_with_refs = \
'<?xml version="1.0" encoding="UTF-8"?>'\
'<content xmlns="http://www.s60.com/xml/content/1">'\
'    <desc>Description field text</desc>'\
'    <input dir="${features.inputref}">'\
'        <include pattern="${features.inputfilter}"/>'\
'    </input>'\
'    <output dir="${features.outputref}" someother="sss"/>'\
'</content>'

contentml2_string = \
'''<?xml version="1.0" encoding="UTF-8"?>
<content xmlns="http://www.s60.com/xml/content/2">
    <tag name='target' value='core'/>
    <tag name='target' value='rofs3'/>
    <tag name='test' value='foo'/>
    <desc>Description field text</desc>
    <output dir="content">
      <input dir="test">
          <include pattern="prod"/>
          <exclude pattern=".svn"/>
      </input>
    </output>
    <output dir="${features.outputref}">
      <input dir="${features.inputref}">
        <include pattern="${features.inputfilter}"/>
      </input>
    </output>
</content>'''

content2_multi = '''<?xml version="1.0" encoding="UTF-8"?>
<content xmlns="http://www.s60.com/xml/content/2">
  <tag name='target' value='foo'/>
  <output dir="content">
    <input>
      <include files="test/override.txt, test/s60.txt"/>
    </input>
  </output>
  <output dir="include" flatten='true'>
    <input file="test/s60.txt"/>
  </output>
</content>'''

external_content_multi = '''<?xml version="1.0" encoding="UTF-8"?>
<content xmlns="http://www.s60.com/xml/content/2">
    <desc>Copy only prod</desc>
    <output dir="content">
        <externalinput dir="external_content/folder1"/>
    </output>    
    <output dir="content">
        <externalinput dir="external_content">
            <include pattern=".txt"/>
            <exclude pattern=".svn"/>
        </externalinput>
    </output>
</content>'''




class TestContentParseimpl(unittest.TestCase):    
    
    def test_parse_desc(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        desc = reader.parse_desc(etree)
        self.assertEquals(desc,'Description field text')

    def test_parse_output(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        output = reader.parse_outputs(etree)
        self.assertEquals(output[0].dir,'content')

    def test_parse_input_dir(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        input = reader.parse_input(etree)
        self.assertEquals(input.dir,'test')

    def test_parse_input_include(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        include = reader.parse_input_include(etree)
        self.assertEquals(include,{'pattern': ['prod']})

    def test_parse_input_files(self):
        etree = ElementTree.fromstring(contentml_files_string)
        reader = contentmlparser.Content1Parser()
        include = reader.parse_input_include(etree)
        self.assertEquals(include,{'files': ['test/foobar.txt, test/bar.txt']})

    def test_parse_input_include_not_found(self):
        etree = ElementTree.fromstring(contentml_brief)
        reader = contentmlparser.Content1Parser()
        include = reader.parse_input_include(etree)
        self.assertEquals(include,{})

    def test_parse_input_exclude(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        include = reader.parse_input_exclude(etree)
        self.assertEquals(include,{'pattern': ['.svn']})

    def test_parse_input_exclude_not_found(self):
        etree = ElementTree.fromstring(contentml_brief)
        reader = contentmlparser.Content1Parser()
        include = reader.parse_input_exclude(etree)
        self.assertEquals(include,{})

    def test_parse_tags(self):
        etree = ElementTree.fromstring(contentml_string)
        reader = contentmlparser.Content1Parser()
        tags = reader.parse_tags(etree)
        self.assertEquals(tags,{'target' : ['core','rofs3'],
                                'test' : ['foo']})

class TestContent2Parseimpl(unittest.TestCase):    
    
    def test_parse_desc(self):
        etree = ElementTree.fromstring(contentml2_string)
        reader = contentmlparser.Content2Parser()
        desc = reader.parse_desc(etree)
        self.assertEquals(desc,'Description field text')

    def test_parse_outputs(self):
        etree = ElementTree.fromstring(contentml2_string)
        reader = contentmlparser.Content2Parser()
        outputs = reader.parse_outputs(etree)
        self.assertEquals(outputs[0].dir,'content')
        self.assertEquals(len(outputs[0].inputs),1)
        self.assertEquals(outputs[0].inputs[0].dir,'test')
        self.assertEquals(outputs[0].inputs[0].include,{'pattern': ['prod']})
        self.assertEquals(outputs[1].inputs[0].dir,'${features.inputref}')
        self.assertEquals(outputs[1].dir,'${features.outputref}')


class TestContentParser(unittest.TestCase):    
    def test_parse_from_string(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml_string)
        self.assertEquals(reader.desc,'Description field text')
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(reader.outputs[0].inputs[0].dir,'test')
        self.assertEquals(reader.outputs[0].inputs[0].include, {'pattern':['prod']})
        self.assertEquals(reader.outputs[0].inputs[0].exclude, {'pattern':['.svn']})
        self.assertEquals(reader.phase, None)
        self.assertEquals(reader.tags, {'target' : ['core','rofs3'],
                                        'test' : ['foo']})

    def test_parse_from_string_with_phase(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml_string_with_phase)
        self.assertEquals(reader.desc,'Description field text')
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(reader.outputs[0].inputs[0].dir,'test')
        self.assertEquals(reader.outputs[0].inputs[0].include, {'pattern':['prod']})
        self.assertEquals(reader.outputs[0].inputs[0].exclude, {'pattern':['.svn']})
        self.assertEquals(reader.phase, 'pre')

    def test_parse_from_string_brief(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml_brief)
        self.assertEquals(reader.desc,"")
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(reader.outputs[0].inputs[0].dir,'test')
        self.assertEquals(reader.outputs[0].inputs[0].include, {})
        self.assertEquals(reader.outputs[0].inputs[0].exclude, {})

    def test_parse_from_string_brief2(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml_brief2)
        self.assertEquals(reader.desc,"")
        self.assertEquals(reader.outputs[0].dir,"")
        self.assertEquals(len(reader.outputs[0].inputs),0)

    def test_parse_from_string_with_refs(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml_with_refs)
        
        self.assertEquals(reader.outputs[0].dir,"${features.outputref}")
        self.assertEquals(reader.outputs[0].inputs[0].dir,"${features.inputref}")
        self.assertEquals(reader.outputs[0].inputs[0].include, {'pattern': ['${features.inputfilter}']} )

    def test_content2_parse_outputs(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(contentml2_string)
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(len(reader.outputs[0].inputs),1)
        self.assertEquals(reader.outputs[0].inputs[0].dir,'test')
        self.assertEquals(reader.outputs[0].inputs[0].include,{'pattern': ['prod']})
        self.assertEquals(reader.outputs[1].inputs[0].dir,'${features.inputref}')
        self.assertEquals(reader.outputs[1].dir,'${features.outputref}')
        self.assertEquals(reader.tags, {'target' : ['core','rofs3'],
                                        'test' : ['foo']})

    def test_content2_parse_multi(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(content2_multi)
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(len(reader.outputs[0].inputs),1)
        self.assertEquals(reader.outputs[0].inputs[0].dir,'')
        self.assertEquals(reader.outputs[0].inputs[0].include,{'files': ['test/override.txt, test/s60.txt']})
        self.assertEquals(reader.outputs[1].inputs[0].file,'test/s60.txt')
        self.assertEquals(reader.outputs[1].inputs[0].get_filelist(),['test/s60.txt'])

    def test_external_content_parse_multi(self):
        reader = contentmlparser.ContentImplReader()
        reader.fromstring(external_content_multi)
        self.assertEquals(reader.outputs[0].dir,'content')
        self.assertEquals(len(reader.outputs[0].inputs),1)
        self.assertEquals(len(reader.outputs[1].inputs),1)
        self.assertEquals(reader.outputs[0].inputs[0].dir,'external_content/folder1')
        self.assertEquals(reader.outputs[0].inputs[0].include,{})
        self.assertEquals(reader.outputs[1].inputs[0].dir,'external_content')
        self.assertEquals(reader.outputs[1].inputs[0].include,{'pattern': ['.txt']})


class TestContentOutput(unittest.TestCase):    
    def test_content_output_dir(self):
        conout = contentmlparser.ContentOutput(dir='foobar/test')
        self.assertEquals(conout.dir, 'foobar/test')

    def test_content_output_include(self):
        conout = contentmlparser.ContentOutput(flatten=True)
        self.assertEquals(conout.flatten, True)

    def test_path_convert(self):
        conout = contentmlparser.ContentOutput()
        self.assertEquals(conout.path_convert('z:\\test\\foo\\bar.txt'), 'test\\foo\\bar.txt')
        self.assertEquals(conout.path_convert('z:/test/foo/bar.txt'), 'test/foo/bar.txt')

class TestContentInput(unittest.TestCase):    
    def test_content_input_dir(self):
        conin = contentmlparser.ContentInput(dir='foobar/test')
        self.assertEquals(conin.dir, 'foobar/test')

    def test_content_include_pattern(self):
        conin = contentmlparser.ContentInput(include={'pattern':['foo','bar']})
        self.assertEquals(conin.get_include_pattern(), 'foo')

    def test_content_exclude_pattern(self):
        conin = contentmlparser.ContentInput(exclude={'pattern':['foo','bar']})
        self.assertEquals(conin.get_exclude_pattern(), 'foo')

    def test_parse_invalid_xml(self):
        try:
            etree = ElementTree.fromstring(invalidxml_string)
            self.fail('Parsing invalid xml succeeds?')
        except:
            pass


if __name__ == '__main__':
    unittest.main()
