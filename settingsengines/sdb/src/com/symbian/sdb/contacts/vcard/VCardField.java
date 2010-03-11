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

package com.symbian.sdb.contacts.vcard;

/**
 * Represents single field in vCard contact
 * 
 * @author krzysztofZielinski
 *
 */
public class VCardField {

    //~ Fields ================================================================
    
    private String name;
    private String value;
    
    // ~ Constructors ==========================================================
    
    public VCardField(
            String name,
            String value) {
        super();
        this.name = name;
        this.value = value;
    }

    // ~ Getters/Setters =======================================================

    public String getName() {
        return name;
    }

    public void setName(
            String name) {
        this.name = name;
    }

    public String getValue() {
        return value;
    }

    public void setValue(
            String value) {
        this.value = value;
    }
    
}
