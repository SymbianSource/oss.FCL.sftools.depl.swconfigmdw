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
Ruleml eval extension to check is passed ref changed on given layer(range).
'''

from cone.public import api

import logging

logger = logging.getLogger('cone.ruleplugin.evals.layer_utils')

def give_changed_layers(feat):
    """
    Returns a list of booleans where True means that feature is changed in that layer. Index is
    same than in configuration root's get_configuration_by_index(). 
    """
    
    logger.debug('Checking feature: %s' % feat.fqr)
    
    root_conf = feat.get_root_configuration()
    nro_of_layers = len(root_conf.list_configurations())
    result = [False] * nro_of_layers
    
    for i in range(0, nro_of_layers):
        conf = root_conf.get_configuration_by_index(i)
        logger.debug("Traversing data from configuration: %s" % conf.get_path())
        datas = conf._traverse(type=api.Data, filters=[lambda d: d.fqr==feat.fqr])
        for data in datas:
            try:
                if data.get_value() != None:
                    logger.debug("Feature '%s' is changed in layer %s with data '%s'" % (feat.fqr, i, data.get_value()))
                    result[i] = True
            except Exception, e:
                logger.debug("Failed to check Feature '%s' data in layer %s:", (e,i))
        if result[i] == False:
            logger.debug("Feature '%s' is not changed in layer: %s" % (feat.fqr, i))
    logger.debug("Feature '%s' is changed in layers: %s" % (feat.fqr, result))
    return result

def changed_on_last_layer(feat):
    """
    Returns True if feature is changed in the last layer.
    """
    
    root_conf = feat.get_root_configuration()
    conf = root_conf.get_configuration_by_index(-2)#autoconfig layer is ignored 
    
    def check(node):
        if isinstance(node, api.Data) and node.fqr == feat.fqr:
            return True
        for obj in node._objects():
            if check(obj):
                return True
    
    if check(conf):
        return True
    else:
        return False

def changed_on_autoconfig_layer(feat):
    """
    Returns True if feature is changed in the autoconfig layer.
    """
    
    root_conf = feat.get_root_configuration()
    conf = root_conf.get_configuration_by_index(-1) 
    
    def check(node):
        if isinstance(node, api.Data) and node.fqr == feat.fqr:
            return True
        for obj in node._objects():
            if check(obj):
                return True
    
    if check(conf):
        return True
    else:
        return False

def changed_on_layer(feat, layer):
    """
    Returns True if feature is changed in the given layer.
    """
    try:
        return give_changed_layers(feat)[layer]
    except IndexError, e:
        logger.warning("Given layer is not found: %s" % (layer))
        return False

def changed_on_layers(feat, findex, tindex):
    """
    Returns True if feature is changed in layer of given range.
    """
    layers = give_changed_layers(feat)
    
    if findex == tindex:
        return changed_on_layer(feat, findex)
    
    for i in range(findex, tindex):
        if i > len(layers):
            continue
        if layers != None and layers[i] != None and layers[i]:
            return True
    return False

