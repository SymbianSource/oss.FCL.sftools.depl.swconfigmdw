// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.configuration.policy.PolicyFactory;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.exception.ValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.util.NodeWrapper;
import com.symbian.sdb.util.XMLBrowser;

public final class ConfigurationParser {
	
    private XMLBrowser browser = new XMLBrowser();
	private final Logger logger = Logger.getLogger(ConfigurationParser.class);	

	private String pQuery;
	private String cQuery;
	
    public ConfigurationParser(DBType type, DocumentVersion version) {
        pQuery = version.getQuery(new Object[] {"policy", type.toString().toLowerCase()});
        cQuery = version.getQuery(new Object[] {"configuration", type.toString().toLowerCase()});
    }
	
   protected NodeWrapper getPoliciesNodes(Document document) {
        NodeWrapper list = new NodeWrapper(browser.findXPathList(pQuery, document));
        return list;
    }
    
   public Map<String, String> parseConfigurationOptions(Document document) throws SDBValidationException {
       Iterable<Node> list = getConfigurationNodes(document);
       HashMap<String, String> options = new HashMap<String, String>(); 
       for (Node lRootNode : list) {
           String name = ((Element)lRootNode).getAttribute("name").toUpperCase();
           String value = ((Element)lRootNode).getAttribute("value").toUpperCase();
           
           DbOptions pOption = null;
           
           try {
               pOption = DbOptions.valueOf(name);
               pOption.setValue(value);
           } catch (IllegalArgumentException ex) {
               options.put(name, value);
           }
       }
       return options;
   }
   
   protected NodeWrapper getConfigurationNodes(Document document) {
       NodeWrapper list = new NodeWrapper(browser.findXPathList(cQuery, document));
       return list;
   }

    public SecuritySettings parseSecurityOptions(Document document) throws SDBExecutionException {		  
	    SecuritySettings lSecSettings = new SecuritySettings();

		StringBuilder lErrors = new StringBuilder();
		
		Iterable<Node> list = getPoliciesNodes(document);
		
		for (Node lRootNode : list) {
            try {
                lSecSettings.addPolicy(PolicyFactory.createPolicy((Element)lRootNode));
            } catch (ValidationException ex) {
                lErrors.append(ex.getLocalizedMessage());
                logger.debug("Stack Trace: ", ex);
            }
		}
		
	    //Validate the symbiansecurity object
        try {
            lSecSettings.validate();
        } catch(ValidationException ex){
            lErrors.append("\n"+ex.getMessage());
            logger.debug(ex);
        }
        
        if (lErrors.length() > 0) {
            throw new SDBExecutionException(lErrors.toString());
        }   
 
        return lSecSettings;
	}
	

}
