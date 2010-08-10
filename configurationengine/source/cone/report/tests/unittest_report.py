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
import unittest

from cone.report import generation_report
from cone.public import plugin, api
from testautomation.utils import remove_if_exists


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR     = os.path.normpath(os.path.join(ROOT_PATH, 'temp'))

class TestGenerateReport(unittest.TestCase):
    def setUp(self):
        remove_if_exists(TEMP_DIR)

    def test_create_report_data(self):
        rdata = generation_report.ReportData()
        self.assertEquals(rdata.context, None)

    def test_save_load_empty_report_data(self):
        rdata = generation_report.ReportData()
        tmpfile = os.path.join(TEMP_DIR, 'repdata.dat')
        generation_report.save_report_data(rdata, tmpfile)
        rdata2 = generation_report.load_report_data(tmpfile)
        self.assertEquals(repr(rdata), repr(rdata2))

    def test_save_load_report_data_with_some_content(self):
        rdata = generation_report.ReportData()
        p = api.Project(api.Storage.open(TEMP_DIR, 'w'))
        config = api.Configuration('test.confml')
        fea = config.create_feature('Foo')
        fea.create_feature('Child1')
        fea.create_feature('Child2')
        c3 = fea.create_feature('Child3')
        c3.value = 'test'
        rdata.log = ['one',
                     'two',
                     'three']
        p.add_configuration(config)
        p.save()
        rdata.context = plugin.GenerationContext(phase="pre",
                                                 tags={'target' : 'rofs3'},
                                                 output='foo',
                                                 configuration=config,
                                                 project=p)
        
        tmpfile = os.path.join(TEMP_DIR, 'repdata.dat')
        generation_report.save_report_data(rdata, tmpfile)
        rdata2 = generation_report.load_report_data(tmpfile)
        self.assertEquals(repr(rdata), repr(rdata2))
        self.assertEquals(rdata.log, rdata2.log) 
        self.assertEquals(rdata.log, rdata2.log) 
        self.assertEquals(rdata2.context.phase, 'pre')
        self.assertEquals(rdata2.context.tags, {'target' : 'rofs3'})
        self.assertEquals(rdata2.context.output, 'foo')
        self.assertEquals(rdata2.context.configuration.Foo.Child3.fqr, 'Foo.Child3')
        self.assertEquals(rdata2.context.configuration.Foo.Child3.get_value(), 'test')
        self.assertEquals(rdata2.context.configuration.Foo.Child3.value, 'test')

    def test_save_load_report_data_with_real_content(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'project')))
        config = prj.get_configuration('root.confml')
        impls = plugin.get_impl_set(config)
        context = plugin.GenerationContext(phase="normal",
                                           tags={'target' : ['rofs2']},
                                           output='temp',
                                           configuration=config)
                
        impls.generate(context)
        prj = config.get_project()
        c1 = config.get_configuration('layer1/root.confml')
        
        self.assertEquals(len(context.generation_output), 4)
        rdata = generation_report.ReportData()
        rdata.context = context
        rdata.project = prj
        tmpfile = os.path.join(TEMP_DIR, 'repdata_real.dat')
        generation_report.save_report_data(rdata, tmpfile)
        rdata2 = generation_report.load_report_data(tmpfile)
        self.assertEquals(repr(rdata), repr(rdata2))
        dview = rdata2.context.configuration.get_default_view()
        self.assertEquals(len(rdata2.context.generation_output), 4)


if __name__ == '__main__':
    unittest.main()
