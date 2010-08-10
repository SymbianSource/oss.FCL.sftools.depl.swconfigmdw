# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of the License "Symbian Foundation License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.symbianfoundation.org/legal/sfl-v10.html".
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

from cone.public import api, plugin

import logging
import re

logger = logging.getLogger('cone.ruleplugin.evals.layer_utils')


def layers_used(config, layers_or_regex, impl_tags):
    """
    Return True if matching layers are used by any implementation with given tag.
    @param config: The configuration.
    @param layers_or_regex: List of layer objects to check against, or regular
        expression (string) for resolving the list of layers.
    @param impl_tags: Implementation tags to use.
    """
    # Resolve layer list
    if isinstance(layers_or_regex, basestring):
        layers = []
        for lay in config.list_configurations():
            if re.search(layers_or_regex, lay):
                layers.append(config.get_configuration(lay))
    else:
        layers = layers_or_regex
    
    impls = plugin.filtered_impl_set(config).filter_implementations(tags=impl_tags)
    context = plugin.GenerationContext(tags=impl_tags,
                                       configuration=config)
    for impl in impls:
        if impl.uses_layers(layers, context) == True:
            return True
    return False


def get_all_layers(feat):
    """
    Returns all layers.
    """
    
    root_conf = feat.get_root_configuration()
    result = []
    
    for i in range(0, len(root_conf.list_configurations())):
        result.append(root_conf.get_configuration_by_index(i))
    return result

def give_changed_layers(feat):
    """
    Returns a list of booleans where True means that feature is changed in that layer. Index is
    same than in configuration root's get_configuration_by_index(). 
    """
    
    logger.debug('Checking feature: %s' % feat.fqr)
    
    root_conf = feat.get_root_configuration()
    nro_of_layers = len(root_conf.list_configurations())
    result = []
    for i in range(0, nro_of_layers):
        result.append(_changed_on_layer(feat, root_conf.get_configuration_by_index(i)))
    return result

def changed_on_last_layer(feat):
    """
    Returns True if feature is changed in the last layer.
    """
    
    root_conf = feat.get_root_configuration()
    conf = root_conf.get_configuration_by_index(-2)#autoconfig layer is ignored 
    return _changed_on_layer(feat, conf)

def changed_on_autoconfig_layer(feat):
    """
    Returns True if feature is changed in the autoconfig layer.
    """
    
    root_conf = feat.get_root_configuration()
    conf = root_conf.get_configuration_by_index(-1)
    return _changed_on_layer(feat, conf)

def changed_on_layer(feat, layer):
    """
    Returns True if feature is changed in the given layer.
    """
    try:
        return give_changed_layers(feat)[layer]
    except IndexError:
        logger.warning("Given layer is not found: %s" % (layer))
        return False

def _changed_on_layer(feature, layer_obj):
    """
    Return whether the given feature is changed on the given layer.
    """
    # Check recursively if the layer contains any data objects with
    # the same FQR as the feature
    def check(node):
        if isinstance(node, api.Data) and node.fqr == feature.fqr:
            return True
        for obj in node._objects():
            if check(obj):
                return True
        return False
    
    return check(layer_obj)

def changed_on_layers(feat, findex, tindex):
    """
    Returns True if feature is changed in layer of given range.
    """
    root_conf = feat.get_root_configuration()
    nro_of_layers = len(root_conf.list_configurations())
    
    # Convert negative indices to positive
    def neg_index_to_pos(index):
        if index < 0:   return nro_of_layers + index
        else:           return index
    begin = neg_index_to_pos(findex)
    end = neg_index_to_pos(tindex)
    
    if end == begin:
        return changed_on_layer(feat, begin)
    
    # Check the layers inside the range
    if end > begin: index_range = xrange(begin, end)
    else:           index_range = xrange(end, begin)
    for i in index_range:
        if i < 0 or i >= nro_of_layers:
            continue
        
        layer = root_conf.get_configuration_by_index(i)
        if _changed_on_layer(feat, layer):
            return True
    return False

def changed_on_layers_regex(feat, regex):
    """
    Return whether the given feature is changed on any layer that matches
    the given regular expression.
    """
    pattern = re.compile(regex)
    root_conf = feat.get_root_configuration()
    for config_path in root_conf.list_configurations():
        if pattern.search(config_path):
            layer = root_conf.get_configuration(config_path)
            if _changed_on_layer(feat, layer):
                return True
    return False

def changed_on_custvariant_layer(feat):
    """
    Return whether the given feature is changed on any of the custvariant layers
    (layers that match the regex '/custvariant(_.*)?/').
    """
    return changed_on_layers_regex(feat, r'/custvariant(_.*)?/')
