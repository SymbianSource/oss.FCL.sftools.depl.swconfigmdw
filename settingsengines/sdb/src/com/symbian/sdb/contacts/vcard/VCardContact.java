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

import java.util.HashSet;
import java.util.Set;

/**
 * Represents single contact imported from vCard
 * 
 * @author krzysztofZielinski
 *
 */
public class VCardContact {

    //~ Fields ================================================================
    
    // TODO KZ: what is required?
    private String firstName = "";
    private String lastName = "";
    private String companyName = "";
    // set of additional fields
    private Set<VCardField> fields = new HashSet<VCardField>();
    
    // ~ Constructors ==========================================================
    
    // TODO KZ: for now i assume firstName is required
    public VCardContact(String firstName) {
        super();
        this.firstName = firstName;
    }

    // ~ Business Methods =======================================================
    
    public void addField(VCardField field)    {
        fields.add(field);
    }
    
    // ~ Getters/Setters =======================================================

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(
            String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(
            String lastName) {
        this.lastName = lastName;
    }

    public String getCompanyName() {
        return companyName;
    }

    public void setCompanyName(
            String companyName) {
        this.companyName = companyName;
    }

    public Set<VCardField> getFields() {
        return fields;
    }

    public void setFields(
            Set<VCardField> fields) {
        this.fields = fields;
    }
}
