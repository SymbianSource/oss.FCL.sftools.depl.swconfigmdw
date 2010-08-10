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
import os

from cone.public import api
from ruleplugin.evals import accesspoint_id_counter
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestAPIDC(unittest.TestCase):
    def test_get_ApDnContainer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals('Internet', container.get_all_dns()[0].get_name())
        self.assertEquals('1', container.get_all_dns()[0].get_id())
        self.assertEquals(['IAP11', 'IAP12', 'IAP13', 'WIAP16', None, None, None, None, None, None], 
         container.get_all_dns()[0].get_iaps())
        
        self.assertEquals('MMS', container.get_all_dns()[1].get_name())
        self.assertEquals('2', container.get_all_dns()[1].get_id())
        self.assertEquals(['IAP21', 'IAP22', 'IAP23', None, None, None, None, None, None, None], 
         container.get_all_dns()[1].get_iaps())
        
        self.assertEquals('Operator', container.get_all_dns()[2].get_name())
        self.assertEquals('3', container.get_all_dns()[2].get_id())
        self.assertEquals(['IAP31', 'IAP32', 'IAP33', None, None, None, None, None, None, None],
         container.get_all_dns()[2].get_iaps())

        self.assertEquals('WIAP16', container.get_all_aps()[0].get_name())
        self.assertEquals('5', container.get_all_aps()[0].get_id())
        
    def test_get_apid_by_apname(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals('1', container.get_apid_by_apname('IAP11'))
        self.assertEquals('2', container.get_apid_by_apname('IAP12'))
        self.assertEquals('7', container.get_apid_by_apname('IAP13'))

    def test_get_dnid_by_dnname(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals('1', container.get_dnid_by_dnname('Internet'))
        self.assertEquals('2', container.get_dnid_by_dnname('MMS'))
        self.assertEquals('3', container.get_dnid_by_dnname('Operator'))


    def test_get_apid_by_dnname_and_apname(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals('2', container.get_apid_by_dnname_and_apname('Internet', 'IAP12'))

    def test_calc_ap_ids(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals('6', container.get_all_aps()[6].get_id())
        self.assertEquals('5', container.get_all_aps()[0].get_id())

    def test_all_in_array(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))

        self.assertEquals(container.get_all_in_array(), 
            [
             ['Internet', '1', 
              ['IAP11', 'IAP12', 'IAP13', 'WIAP16', None, None, None, None, None, None], 
              ['1', '2', '7', '5', None, None, None, None, None, None], 
              ['1', '2', '3', '4', None, None, None, None, None, None]], 
             ['MMS', '2', 
              ['IAP21', 'IAP22', 'IAP23', None, None, None, None, None, None, None], 
              ['4', '8', '6', None, None, None, None, None, None, None], 
              ['5', '6', '7', None, None, None, None, None, None, None]], 
             ['Operator', '3', 
              ['IAP31', 'IAP32', 'IAP33', None, None, None, None, None, None, None], 
              [None, None, '9', None, None, None, None, None, None, None], 
              [None, None, '8', None, None, None, None, None, None, None]]
             ]
            )

    def test_get_next_free_id(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals("4", accesspoint_id_counter._get_next_free_id_(container.get_all_dns()))
        self.assertEquals("10", accesspoint_id_counter._get_next_free_id_(container.get_all_aps()))

    def test_get_apindex_by_apname(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        container = accesspoint_id_counter._get_ApDnContainer_(dview.get_feature("WLAN_APs"), dview.get_feature("APs"), dview.get_feature("DNs"))
        
        self.assertEquals("5", container.get_apindex_by_apname("IAP21"))
        self.assertEquals("1", container.get_apindex_by_apname("IAP11"))

        
if __name__ == "__main__":
    unittest.main()
