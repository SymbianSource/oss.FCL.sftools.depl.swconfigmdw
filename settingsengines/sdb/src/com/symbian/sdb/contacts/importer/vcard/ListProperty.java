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

public class ListProperty extends Property  {

	public ListProperty(Element type) {
		super(type);
	}

	@Override
	public byte[] getValue() {		
        StringBuffer singleValue = new StringBuffer();

        for (String item : getItemValues()) {
        	item.trim();
            singleValue.append(item);
            singleValue.append(", ");
        }

        return singleValue.toString().trim().getBytes();
	}

    public String[] getItemValues() {
    	return XpathUtil.getValueArray(getElement(), "value/listItem/text/text()");
    }
}
