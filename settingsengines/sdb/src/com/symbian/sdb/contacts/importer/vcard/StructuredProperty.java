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

import net.sf.vcard4j.util.XpathUtil;

import org.w3c.dom.Element;


/**
 * @author krzysztofZielinski
 *
 */
public class StructuredProperty extends Property {

    private int numberOfItems;
    
    /**
     * @param type
     */
    public StructuredProperty(Element type, int numberOfItems) {
        super(type);
        this.numberOfItems = numberOfItems;
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.vcard.Property#getValue()
     */
    @Override
    public byte[] getValue() {
        StringBuffer singleValue = new StringBuffer();
        
        // concatenate items in reversed sequence
        for (int i = numberOfItems; i > 0; i--) {
            String itemValue = getItemValue(i);
            itemValue.trim();
            if (!(itemValue.length() > 0))   {
                singleValue.append(itemValue);
                singleValue.append(" "); 
            }
        }
        // remove space in the beginning 
        return singleValue.toString().trim().getBytes();
    }

    public String getItemValue(int i) {
        String value = XpathUtil.getValue(getElement(), "value/structuredItem[" + i + "]/listItem/text/text()");
        if (null == value)	{
        	return "";
        }
    	return value;
    }

    public String[] getItemValues() {
    	return XpathUtil.getValueArray(getElement(), "value/structuredItem/listItem/text/text()");
    }

    public String getItemValuesAsString() {
    	
    	String[] values = XpathUtil.getValueArray(getElement(), "value/structuredItem/listItem/text/text()");
    	
    	if (values.length == 1) {
    		return values[0];
    	}
    	
    	StringBuffer singleValue = new StringBuffer();
    	
    	for (String item : values) {
    		singleValue.append(item + "; ");
    	}
    	
    	return singleValue.toString().trim();
    }
    
    public int getSize() {
    	// TODO: DW take a look at this
    	XpathUtil.getNode(getElement(), "//value");
        return Integer.parseInt(XpathUtil.getValue(getElement(), "//value/structuredItem"));
    }

}
