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

package com.symbian.sdb.contacts.dbms.model;


/**
 * @author krzysztofZielinski
 *
 */
public class IdentityTable {

    // ~ Fields ================================================================
    
    private Long parentCMID = null;
    private String firstName = "";
    private String lastName = "";
    private String companyName = "";
    private String firstNamePrn = "";
    private String lastNamePrn = "";
    private String companyNamePrn = "";
    private ContactType type;
    private DBMSContactAttribute attribute;
    private ContactHintField contactHintField = new ContactHintField();
    private ContactExtHintField contactExtHintField;
    
    // ~ Constructors ==========================================================
    
    public IdentityTable(ContactType type) {
        super();
        this.type = type;
    }
    
    // ~ Getters/Setters =======================================================
    
    public Long getParentCMID() {
        return parentCMID;
    }

    public void setParentCMID(Long parentCMID) {
        this.parentCMID = parentCMID;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getCompanyName() {
        return companyName;
    }

    public void setCompanyName(String companyName) {
        this.companyName = companyName;
    }

    public String getFirstNamePrn() {
        return firstNamePrn;
    }

    public void setFirstNamePrn(String firstNamePrn) {
        this.firstNamePrn = firstNamePrn;
    }

    public String getLastNamePrn() {
        return lastNamePrn;
    }

    public void setLastNamePrn(String lastNamePrn) {
        this.lastNamePrn = lastNamePrn;
    }

    public String getCompanyNamePrn() {
        return companyNamePrn;
    }

    public void setCompanyNamePrn(String companyNamePrn) {
        this.companyNamePrn = companyNamePrn;
    }

    public ContactType getType() {
        return type;
    }

    public void setType(ContactType type) {
        this.type = type;
    }

    public DBMSContactAttribute getAttribute() {
        return attribute;
    }

    public void setAttribute(DBMSContactAttribute attribute) {
        this.attribute = attribute;
    }

    public ContactHintField getContactHintField() {
        return contactHintField;
    }

    public void setContactHintField(ContactHintField contactHintField) {
        this.contactHintField = contactHintField;
    }

    public ContactExtHintField getContactExtHintField() {
        return contactExtHintField;
    }

    public void setContactExtHintField(ContactExtHintField contactExtHintField) {
        this.contactExtHintField = contactExtHintField;
    }
}
