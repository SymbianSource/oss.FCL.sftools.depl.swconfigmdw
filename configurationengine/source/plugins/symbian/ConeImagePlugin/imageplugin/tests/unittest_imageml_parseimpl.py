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
import sys

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

from imageplugin import imageml


imageml_string = \
'''<?xml version="1.0" encoding="UTF-8"?>
<imageml xmlns="http://www.s60.com/xml/imageml/1">
    <output file="startup.mbm" extraparams="/V2">
    	<input dir="UI/Start-up Animation">
    		<include pattern="bmb$"/>
            <exclude pattern=".svn"/>
    	</input>
    </output>
    <output file="shutdown.mbm">
        <input file="UI/graphics/icon1.bmb" depth="8" />
        <input file="UI/graphics/icon2.bmb" depth="8" />
        <input file="UI/graphics/icon3.bmb" depth="8" />
        <input file="UI/graphics/icon4.bmb" depth="8" />
    </output>
</imageml>
'''

imageml_with_refs = \
'''<?xml version="1.0" encoding="UTF-8"?>
<imageml xmlns="http://www.s60.com/xml/imageml/1">
    <output file="${features.outputref}">
        <input dir="${features.inputref}">
            <include pattern="${features.inputfilter}"/>
        </input>
    </output>
    <output file="${features.outputseqfile}">
        <input file="${features.outputseq.file.localpath}">
        </input>
    </output>
</imageml>
'''
input_dir= \
'''<output xmlns="http://www.s60.com/xml/imageml/1" file="test.mbm">
  <input dir="UI/Start-up Animation" depth="8" test="foo">
    <include pattern="bmb$"/>
    <exclude pattern=".svn"/>
  </input>
  <input dir="UI/Start-up Animation/masks" depth="2">
    <include pattern="bmb$"/>
  </input>
</output>
'''
input_files = \
'''<output xmlns="http://www.s60.com/xml/imageml/1" file="test.mbm">
  <input file="UI/graphics/icon1.bmb" depth="8" />
  <input file="UI/graphics/icon2.bmb" depth="8" />
  <input file="UI/graphics/icon3.bmb" depth="8" />
  <input file="UI/graphics/icon4.bmb" depth="8" />
</output>
'''

class TestImagemlParseimpl(unittest.TestCase):    

    def test_parse_output(self):
        etree = ElementTree.fromstring(imageml_string)
        reader = imageml.ImageImplReader()
        outgens = reader.parse_outputs(etree)
        self.assertEquals(outgens[0].outputpath,'startup.mbm')

    def test_parse_input_include(self):
        etree = ElementTree.fromstring(input_dir)
        input = etree.find("{%s}input" % 'http://www.s60.com/xml/imageml/1')
        reader = imageml.ImageImplReader()
        include = reader.parse_input_include(input)
        self.assertEquals(include,{'pattern': ['bmb$']})

    def test_parse_input_exclude(self):
        etree = ElementTree.fromstring(input_dir)
        input = etree.find("{%s}input" % 'http://www.s60.com/xml/imageml/1')
        reader = imageml.ImageImplReader()
        include = reader.parse_input_exclude(input)
        self.assertEquals(include,{'pattern': ['.svn']})

    def test_parse_inputs_with_dir(self):
        etree = ElementTree.fromstring(input_dir)
        reader = imageml.ImageImplReader()
        inputs = reader.parse_inputs(etree)
        self.assertEquals(inputs[0].path,'UI/Start-up Animation')
        self.assertEquals(inputs[0].type,'dir')
        self.assertEquals(inputs[0].include, ['bmb$'])
        self.assertEquals(inputs[0].exclude, ['.svn'])
        self.assertEquals(inputs[0].depth,'8')
        self.assertEquals(inputs[0].test,'foo')
        self.assertEquals(inputs[1].path,'UI/Start-up Animation/masks')
        self.assertEquals(inputs[1].depth,'2')

    def test_parse_inputs_with_files(self):
        etree = ElementTree.fromstring(input_files)
        reader = imageml.ImageImplReader()
        inputs = reader.parse_inputs(etree)
        self.assertEquals(inputs[0].path,'UI/graphics/icon1.bmb')
        self.assertEquals(inputs[0].depth,'8')
        self.assertEquals(inputs[1].path,'UI/graphics/icon2.bmb')
        self.assertEquals(inputs[1].depth,'8')
        self.assertEquals(inputs[2].path,'UI/graphics/icon3.bmb')
        self.assertEquals(inputs[2].depth,'8')
        self.assertEquals(inputs[3].path,'UI/graphics/icon4.bmb')
        self.assertEquals(inputs[3].depth,'8')

    def test_parse_outputs(self):
        etree = ElementTree.fromstring(imageml_string)
        reader = imageml.ImageImplReader()
        outputs = reader.parse_outputs(etree)
        self.assertEquals(outputs[0].outputpath,'startup.mbm')
        self.assertEquals(outputs[0].extraparams, '/V2')
        self.assertEquals(outputs[0].inputs[0].path,'UI/Start-up Animation')
        self.assertEquals(outputs[0].inputs[0].type,'dir')
        self.assertEquals(outputs[0].inputs[0].include,['bmb$'])
        self.assertEquals(outputs[0].inputs[0].exclude,['.svn'])
        self.assertEquals(outputs[1].outputpath,'shutdown.mbm')
        self.assertEquals(outputs[1].inputs[0].type,'file')
        self.assertEquals(outputs[1].inputs[0].path,'UI/graphics/icon1.bmb')
        self.assertEquals(outputs[1].inputs[1].type,'file')
        self.assertEquals(outputs[1].inputs[1].path,'UI/graphics/icon2.bmb')
        self.assertEquals(outputs[1].inputs[2].type,'file')
        self.assertEquals(outputs[1].inputs[2].path,'UI/graphics/icon3.bmb')
        self.assertEquals(outputs[1].inputs[3].type,'file')
        self.assertEquals(outputs[1].inputs[3].path,'UI/graphics/icon4.bmb')

    def test_parse_from_string(self):
        reader = imageml.ImageImplReader()
        reader.fromstring(imageml_string)
        self.assertEquals(reader.desc,'')
        self.assertEquals(reader.outputgenerators[0].outputpath,'startup.mbm')
        self.assertEquals(reader.outputgenerators[0].inputs[0].path,'UI/Start-up Animation')
        self.assertEquals(reader.outputgenerators[0].inputs[0].type,'dir')
        self.assertEquals(reader.outputgenerators[0].inputs[0].include,['bmb$'])
        self.assertEquals(reader.outputgenerators[0].inputs[0].exclude,['.svn'])

    def test_parse_from_string_with_refs(self):
        reader = imageml.ImageImplReader()
        reader.fromstring(imageml_with_refs)
        self.assertEquals(reader.outputgenerators[0]._outputpath,'${features.outputref}')
        self.assertEquals(reader.outputgenerators[0].inputs[0]._path,'${features.inputref}')
        self.assertEquals(reader.outputgenerators[0].inputs[0].type,'dir')
        self.assertEquals(reader.outputgenerators[0].inputs[0].include,['${features.inputfilter}'])

# Only run these tests on Windows
if sys.platform != 'win32':
    del TestImagemlParseimpl

if __name__ == '__main__':
    unittest.main()
