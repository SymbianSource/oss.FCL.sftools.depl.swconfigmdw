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

import java.util.HashSet;
import java.util.Set;

import net.sf.vcard4j.util.XpathUtil;

import org.w3c.dom.Element;
import org.w3c.dom.Node;

/**
 * @author krzysztofZielinski
 *
 */
public class Parameters implements IParameters {

    private static final String PROPERTY_TYPE_ATTRIBUTE = "TYPE";
    private static final String PROPERTY_VALUE_ATTRIBUTE = "value";
    
    private Element type;

	public Parameters(Element property) {
        super();
        this.type = property;
    }
 
    /* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.importer.vcard.IParameters#getValuesForTypeParameter()
	 */
    public Set<String> getValuesForTypeParameter()  {
        return getValuesForParameter(PROPERTY_TYPE_ATTRIBUTE);
    }

    protected Set<String> getValuesForParameter(String parameterName)    {
        
        Node[] parameters = findElementForParameter(parameterName);
        Set<String> parameterValues = retrieveValuesForParameters(parameters);
        return parameterValues;
    }
 
    private Set<String> retrieveValuesForParameters(Node[] parameters) {
        Set<String> parameterValues = new HashSet<String>();
        for (int i = 0; i < parameters.length; i++) {
            Element parameterElement = (Element) parameters[i];
            parameterValues.add(parameterElement.getAttribute(PROPERTY_VALUE_ATTRIBUTE));
        }
        return parameterValues;
    }

    private Node[] findElementForParameter(String parameterName) {
        Node[] parameters = (Node[]) XpathUtil.getNodeArray(type, "parameter[@name='" + parameterName + "']");
        return parameters;
    }
    
}
