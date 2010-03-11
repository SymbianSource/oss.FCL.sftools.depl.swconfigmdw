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

/**
 * Represents VCard properties e.g. for TEL;CELL;07912345678, TEL is a property name and CELL is a property parameter (property value is not part of property data)
 * 
 * @author krzysztofZielinski
 *
 */
public class PropertyData {

    private String name;
    private Set<String> parameters = new HashSet<String>();
    
    public static PropertyData newInstance(IProperty property)	{
    	return new PropertyData(property);
    }
    
    protected PropertyData(IProperty property) {
        super();
        this.name = property.getName();

        for (String parameter : property.getParameters().getValuesForTypeParameter()) {
            parameters.add(parameter);
        }
    }

    /**
     * @param string
     * @param strings
     */
    public PropertyData(String propertyName, String[] propertyParameters) {
        this.name = propertyName;
        
        for (int i = 0; i < propertyParameters.length; i++) {
            String parameter = propertyParameters[i].trim();
            this.parameters.add(parameter);
        }
    }

    public String getName() {
        return name;
    }

    public Set<String> getParameters() {
        return parameters;
    }
}
