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

import org.w3c.dom.Element;


/**
 * Represent vCard property e.g. TEL;VOICE;CELL;HOME:07873198633
 * 
 * @author krzysztofZielinski
 *
 */
public abstract class Property implements IProperty {

    private Element type;
    
	public Property() {
		super();
	}

	public Property(Element type) {
        this.type = type;
    }
    
    protected Element getElement() {
        return type;
    }
    
    public String getName() {
        return type.getAttribute("name");
    }
    
    public IParameters getParameters()   {
        return new Parameters(type);
    }

    public abstract byte[] getValue();
    
}
