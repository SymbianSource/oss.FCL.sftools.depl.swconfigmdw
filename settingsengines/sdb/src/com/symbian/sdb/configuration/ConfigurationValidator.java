// Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
// All rights reserved.
// This component and the accompanying materials are made available
// under the terms of "Eclipse Public License v1.0"
// which accompanies this distribution, and is available
// at the URL "http://www.eclipse.org/legal/epl-v10.html".
//
// Initial Contributors:
// Nokia Corporation - initial contribution.
//
// Contributors:
//
// Description:
//

package com.symbian.sdb.configuration;

import java.io.File;
import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.validation.Schema;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;

import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.util.XMLBrowser;
import com.symbian.sdb.util.XmlManager;

public class ConfigurationValidator {
   private XMLBrowser browser = new XMLBrowser();
   private final Logger logger = Logger.getLogger(ConfigurationValidator.class);    
   
   private DocumentVersion dVersion;
   
   public XmlManager manager = new XmlManager();
   
   public Document loadAndValidate(File xmlFile) throws SDBValidationException {
       Document document = null;
       try {
           logger.debug("loading document " + xmlFile.getAbsolutePath());
           document = manager.loadDocument(xmlFile);

           String version = getVersion(document);
           
           if (version == null || version.trim().length() == 0) {
               version = "1.0";
           }
           
           logger.debug("version set to " + version);
           
           String schemaName = System.getProperty("sdb.schema.location." + version);
           if (schemaName == null || schemaName.trim().length() == 0) {
               throw new SDBValidationException("No schema matching current configuration version");
           }
           
           dVersion = DocumentVersion.valueOf("V" + version.replace(".", ""));
           
           logger.debug("loading schema " + schemaName);
           Schema schema = manager.loadSchema(schemaName);
           
           logger.debug("validating document");
           manager.validate(document, schema);
 
       } catch(IOException ex) {
           throw new SDBValidationException("Unable to find settings file: " + ex);
       } catch(SAXException ex) {
           throw new SDBValidationException("Settings File is not valid: " + ex.getMessage());
       } catch(ParserConfigurationException ex) {
           throw new SDBValidationException("Fatal Error has occured:: " + ex.getMessage());
       }
       
       return document;
   }
    
   public DocumentVersion getVersion() {
       return dVersion;
   }
   
    protected String getVersion(Document document) {
        return browser.findXPathValue("child::node()/@version", document);
    }
    

}
