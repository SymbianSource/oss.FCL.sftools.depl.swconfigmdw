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

import logging
import xml.parsers.expat

from cone.public import api, utils
from cone.storage import metadata

class StorageBase(api.Storage):
    """
    A general base class for all storage type classes
    """
    METADATA_FILENAME = ".metadata"

    def __init__(self,path):
        super(StorageBase, self).__init__(path)
        self.meta = self.read_metadata()

    def get_active_configuration(self): 
        """
        Return the active configuration. 
        If the storage holds only one configuration, it will be always active  
        """
        root_confmls = self.list_resources("/")
        root_confmls = utils.resourceref.filter_resources(root_confmls,"\.confml")
        if self.meta.get_root_file() == '' and len(root_confmls) == 1:
            return root_confmls[0]
        else:
            return self.meta.get_root_file()
            

    def set_active_configuration(self, ref):
        self.meta.set_root_file(ref)

    def read_metadata(self):
        meta = None
        if not self.is_resource(self.METADATA_FILENAME):
            logging.getLogger('cone').info("No metadata found for: %s" % (self.get_path()))
            # return empty metadata object
            meta = metadata.Metadata()
        else:
            res = self.open_resource(self.METADATA_FILENAME)
            try:
                try:
                    meta = metadata.MetadataReader().fromstring(res.read())
                except xml.parsers.expat.ExpatError:
                    """ in case of xml parsing error return empty metadata """
                    meta = metadata.Metadata()
            finally:
                res.close()
        return meta

    def write_metadata(self):
        # Try to update the metadata, which might fail on ZipStorage

        try:
            if self.get_mode(self.mode) != api.Storage.MODE_READ:
                # update the active configuration
                self.set_active_configuration(self.get_active_configuration())
                metares = self.open_resource(self.METADATA_FILENAME,"wb")
                metadata.MetadataWriter().toresource(self.meta,metares)
                metares.close()
        except Exception,e:
            logging.getLogger('cone').error("Could not save metadata. Exception %s" % e)
        return

    def close(self):
        if self.get_current_path() == "": 
            self.write_metadata()
        super(StorageBase, self).close()

