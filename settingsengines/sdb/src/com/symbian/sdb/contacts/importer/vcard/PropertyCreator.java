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

package com.symbian.sdb.contacts.importer.vcard;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.w3c.dom.Element;
import org.w3c.dom.Node;

import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;

/**
 * @author krzysztofZielinski
 *
 */
public class PropertyCreator {

    private static final String TYPE_NAME_ATTRIBUTE = "name";

    private ITemplateModel templateModel;    
    
    private static final Map<String,Integer> structuredProperties = new HashMap<String, Integer>();
    private static final Set<String> listProperties = new HashSet<String>();
    private IVCardContactProperties contactProperties = new VCardContactProperties();
    
    {
        structuredProperties.put("ADR",7);
        structuredProperties.put("GEO",2);  // long and lat
        structuredProperties.put("N",5);
        structuredProperties.put("ORG",2);
        
        listProperties.add("CATEGORY");
        listProperties.add("NICKNAME");
    }
    
    public PropertyCreator(ITemplateModel templateModel) {
        this.templateModel = templateModel;
    }

    public void readProperty(Node node)    {
        String nodeName = getNodeName(node);
        
        if (isStructuredProperty(nodeName))    {
            StructuredProperty structuredProperty = PropertyFactory.newStructuredProperty((Element)node,structuredProperties.get(nodeName));

            if (isSupported(structuredProperty))	{
            	contactProperties.addStructuredProperty(structuredProperty);	
            }
        } else if (isListProperty(nodeName)) {
			ListProperty listProperty = PropertyFactory.newListProperty((Element) node);
			
			if (isSupported(listProperty))	{
				contactProperties.addListProperty(listProperty);	
			}
		} else {
            // assume it is a simple property
            SimpleProperty simpleProperty = PropertyFactory.newSimpleProperty((Element)node);
            
            if (isSupported(simpleProperty))	{
            	contactProperties.addSimpleProperty(simpleProperty);
            } else if (isSpeedDialProperty(simpleProperty)) {
    			contactProperties.getSpeedDialVCardPropertiesData().add(SpeedDialVCardTemporaryData.valueOf(simpleProperty));
    		}
        }
    }

    private boolean isSpeedDialProperty(SimpleProperty simpleProperty) {
		return SpeedDialVCardTemporaryData.isSpeedDialProperty(simpleProperty);
	}

	private boolean isSupported(IProperty property) {

    	PropertyData propertyData = ContactCreator.getPropertyData(property);
    	
    	// TODO KZ: temporarily exclude FN
        if (propertyData.getName().equals("FN"))    {
            return false;
        }

        try {
			return templateModel.templateContainsMappingForVCardProperty(propertyData);
		} catch (MappingMissingException e) {
			return false;
		}
    }

    public IVCardContactProperties getProperties()	{
    	return contactProperties;
    }
    
    private boolean isListProperty(String nodeName) {
		return listProperties.contains(nodeName);
	}

	private boolean isStructuredProperty(String nodeName) {
		return structuredProperties.keySet().contains(nodeName);
	}

    private String getNodeName(Node typeNode) {
        Element typeElement = (Element)typeNode;
        String typeName = typeElement.getAttribute(TYPE_NAME_ATTRIBUTE);
        return typeName;
    }

	/**
	 * @return the speedDialVCardPropertiesData
	 */
	public Set<SpeedDialVCardTemporaryData> getSpeedDialVCardPropertiesData() {
		return this.contactProperties.getSpeedDialVCardPropertiesData();
	}
    
}
