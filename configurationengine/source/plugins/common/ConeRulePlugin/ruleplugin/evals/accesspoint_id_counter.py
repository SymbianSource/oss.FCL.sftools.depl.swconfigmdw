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
'''
Ruleml eval extension to count accesspoint id's
'''

import logging

logger = logging.getLogger('cone.ruleplugin.evals.accesspoint_id_counter')

def get_apindex_by_apname(wlan_aps, aps, dns, apname):
    """
    Returns AccessPoint index by given AccessPoint name
    """
    cnt = _get_ApDnContainer_(wlan_aps, aps, dns)
    return cnt.get_apindex_by_apname(apname)

def get_apid_by_apname(wlan_aps, aps, dns, apname):
    """
    Returns AccessPoint id by given AccessPoint name
    """
    cnt = _get_ApDnContainer_(wlan_aps, aps, dns)
    return cnt.get_apid_by_apname(apname)

def get_dnid_by_dnname(aps, dns, dnname):
    """
    Return DestinationNetwork id by given DestinationNetworks name
    """
    cnt = _get_ApDnContainer_(wlan_aps, aps, dns)
    return cnt.get_dnid_by_dnname(dnname)

def get_apid_by_dnname_and_apname(wlan_aps, aps, dns, dnname, apname):
    """
    Returns AccessPoint id by given DestinationNetwork name and AccessPoint name.
    """
    cnt = _get_ApDnContainer_(wlan_aps, aps, dns)
    return cnt.get_apid_by_dnname_and_apname(dnname, apname)

def get_all_in_array(wlan_aps, aps, dns):
    """
    Returns array containing all data:
        [DN name],[DN id], [IAPS names], [IAPS ids], [IAPS indexes] 
    """
    cnt = _get_ApDnContainer_(wlan_aps, aps, dns)
    return cnt.get_all_in_array()

def _get_ApDnContainer_(wlan_aps, aps, dns):
    """
    Returns populated ApDnContainer
    """
    cnt = ApDnContainer()
    
    _read_dns_(dns, cnt)
    _read_wlan_aps_(wlan_aps, cnt)
    _read_aps_(aps, cnt)
    
    cnt._calc_dn_ids_()
    cnt._calc_ap_ids_()
    cnt._calc_ap_indexes_()
    
    return cnt

def _read_dns_(dns, cnt):
    """
    Reads DNs to internal objects to ApDnContainer.
    """
    
    dn_names = None
    dn_ids = None
    dn_iaps = [None]*10
    
    for dn in dns.DN:
        if dn.ref == 'Name':
            dn_names = dn.value
        if dn.ref == 'DNId':
            dn_ids = dn.value
        if dn.ref == 'IAP':
            dn_iaps[0] = dn.value
        if dn.ref == 'IAP2':
            dn_iaps[1] = dn.value
        if dn.ref == 'IAP3':
            dn_iaps[2] = dn.value
        if dn.ref == 'IAP4':
            dn_iaps[3] = dn.value
        if dn.ref == 'IAP5':
            dn_iaps[4] = dn.value
        if dn.ref == 'IAP6':
            dn_iaps[5] = dn.value
        if dn.ref == 'IAP7':
            dn_iaps[6] = dn.value
        if dn.ref == 'IAP8':
            dn_iaps[7] = dn.value
        if dn.ref == 'IAP9':
            dn_iaps[8] = dn.value
        if dn.ref == 'IAP10':
            dn_iaps[9] = dn.value
    
    logger.info('Parsed DN names: %s' % dn_names)
    logger.info('Parsed DN ids: %s' % dn_ids)
    logger.info('Parsed DN iaps: %s' % dn_iaps)
    
    for i in range(len(dn_names)):
        mydn = Dn()
        mydn.set_id(dn_ids[i])
        mydn.set_name(dn_names[i])
        myiaps = [None]*10
        for j in range(10):
            myiaps[j] = dn_iaps[j][i]
        mydn.set_iaps(myiaps)
        cnt.add_dn(mydn)
    return cnt

def _read_all_aps_(wlan_aps, aps, cnt):
    """
    Reads WLAN_APs and APs to internal objects to ApDnContainer
    """
    

def _read_aps_(aps, cnt):
    """
    Reads APs to internal objects to ApDnContainer.
    """
    ap_names = None
    ap_ids1 = None
    
    for ap in aps.AP:
        if ap.ref == 'ConnectionName':
            ap_names = ap.value
        if ap.ref == 'ConnectionId':
            ap_ids1 = ap.value
    
    ap_ids2 = [None]*len(ap_names)
    if ap_ids1 == None:
        ap_ids1 = []
    
    
    for i in range(len(ap_ids1)):
        ap_ids2[i] = ap_ids1[i]
        
    
    logger.info('Parsed AP names: %s' % ap_names)
    logger.info('Parsed AP ids: %s' % ap_ids2)
    
    for i in range(len(ap_names)):
        myap = Ap()
        myap.set_id(ap_ids2[i])
        myap.set_name(ap_names[i])
        cnt.add_ap(myap)
    return cnt

def _read_wlan_aps_(wlan_aps, cnt):
    """
    Reads APs to internal objects to ApDnContainer.
    """
    ap_names = None
    ap_ids1 = None
    
    for ap in wlan_aps.WLAN_AP:
        if ap.ref == 'ConnectionName':
            ap_names = ap.value
        if ap.ref == 'ConnectionId':
            ap_ids1 = ap.value
    
    ap_ids2 = [None]*len(ap_names)
    if ap_ids1 == None:
        ap_ids1 = []
    
    
    for i in range(len(ap_ids1)):
        ap_ids2[i] = ap_ids1[i]
        
    
    logger.info('Parsed WLAN_AP names: %s' % ap_names)
    logger.info('Parsed WLAN_AP ids: %s' % ap_ids2)
    
    for i in range(len(ap_names)):
        myap = Ap()
        myap.set_id(ap_ids2[i])
        myap.set_name(ap_names[i])
        cnt.add_ap(myap)
    return cnt

def _get_next_free_id_(bases, start_index=0):
    """
    Returns next id as a string that is not in use.
    """
    
    biggest_id = int(start_index)
    
    for base in bases:
        current_id = base.get_id()
        if current_id != None or current_id != '':
            if current_id > biggest_id:
                biggest_id = current_id
    
    return str(int(biggest_id) + 1)


class ApDnContainer(object):
    """
    Container for AccessPoints and DestinationNetworks, that provides various access and search methods to them.
    """
    
    def __init__(self):
        self.dns = []
        self.aps = []

    def __str__(self):
        return "ApDnContainer(dns: " + str(self.dns) + ", aps:" + str(self.aps) + ")"

    def add_dn(self, dn):
        self.dns.append(dn)
    
    def add_ap(self, ap):
        self.aps.append(ap)

    def get_all_dns(self):
        return self.dns
    
    def get_all_aps(self):
        return self.aps
    
    def _calc_dn_ids_(self):
        for dn in self.dns:
            if dn.get_id() == None or dn.get_id() == '':
                dn.set_id(_get_next_free_id_(self.dns, 1))

    def _calc_ap_indexes_(self, ind=1):
        index = ind
        for dn in self.dns:
            for iap in dn.get_iaps():
                if iap != None:
                    for ap in self.aps:
                        if ap.get_name() == iap and ap.get_index() == '':
                            ap.set_index(str(index))
                            index += 1

    def _calc_ap_ids_(self, start_index=0):
        """
        Calculates unique index for every AccessPoint.
        """
                        
        for ap in self.aps:
            if ap.get_id() == None or ap.get_id() == '':
                ap.set_id(_get_next_free_id_(self.aps, int(start_index)))
    
    def get_apid_by_apname(self, apname):
        """
        Returns Accesspoint id by given AccessPoint name
        """
    
        for ap in self.aps:
            if ap.name == apname:
                return ap.get_id()
        logger.warning('ApId not found by ApName: %s' % apname)
        return None
    
    def get_apindex_by_apname(self, apname):
        """
        Returns Accesspoint index by given AccessPoint name
        """
        
        for ap in self.aps:
            if ap.get_name() == apname:
                return ap.get_index()
        logger.warning('ApIndex not found by ApName: %s' % apname)
        return None
    
    
    def get_dnid_by_dnname(self, dnname):
        """
        Return DestinationNetwork id by given DestinationNetworks name
        """
        for dn in self.dns:
            if dn.name == dnname:
                return dn.id
        logger.warning('DnId not found by DnName: %s' % dnname)
        return None
    
    def get_apid_by_dnname_and_apname(self, dnname, apname):
        """
        Returns AccessPoint id by given DestinationNetwork name and AccessPoint name.
        """
        for dn in self.dns:
            if dn.name == dnname:
                iaps = dn.get_iaps()
                for iap in range(len(iaps)):
                    if iaps[iap] != None and iaps[iap] == apname:
                        return self.get_apid_by_apname(apname)
        logger.warning('ApId not found by DnName: %s ApName: %s' % dnname, apname)
        return None
    
    def get_all_in_array(self):
        """
        Returns array containing all data:
            [DN name],[DN id], [IAPS names], [IAPS ids] [IAPS index]
        """
        ret = [None]*len(self.dns)
        
        for i in range(len(self.dns)):
            line = [None]*5
            line[0] = self.dns[i].get_name()
            line[1] = self.dns[i].get_id()
            line[2] = self.dns[i].get_iaps()
            
            ap_ids = [None]*10
            
            for j in range(10):
                ap_ids[j] = self.get_apid_by_apname(self.dns[i].get_iaps()[j])
            
            line[3] = ap_ids
            
            ap_indexes = [None]*10
            
            for j in range(10):
                ap_indexes[j] = self.get_apindex_by_apname(self.dns[i].get_iaps()[j])
            
            line[4] = ap_indexes
            
            ret[i] = line
            
        return ret

class Base(object):
    """
    Base data classes for AP and DN classes.
    """
    def __init__(self):
        self.name = ''
        self.id = ''

    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def set_id(self, id):
        self.id = id
    
    def get_id(self):
        return self.id

class Dn(Base):
    """
    Destination network
    """
    
    def __init__(self):
        self.name = None
        self.id = None
        self.iaps = [None]*10
    
    def __str__(self):
        return "Dn(name: " + self.name + ", id:" + self.id + ", iaps:" + str(self.iaps) + ")"
    
    def set_iaps(self, iaps):
        self.iaps = iaps

    def set_iap(self, index, value):
        self.iaps[index] = value
    
    def get_iap(self, index):
        return self.iaps[index]
    
    def get_iaps(self):
        return self.iaps
    
class Ap(Base):
    
    def __init__(self):
        self.name = ''
        self.id = ''
        self.index = ''
    
    def __str__(self):
        return "Ap(name: " + self.name + ", id:" + self.id + ")"
    
    def set_index(self, index):
        self.index = index
    
    def get_index(self):
        return self.index

