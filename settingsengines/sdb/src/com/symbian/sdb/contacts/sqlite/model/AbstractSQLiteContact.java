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

package com.symbian.sdb.contacts.sqlite.model;

import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.DatabaseSpecificContact;
import com.symbian.sdb.util.ByteUtil;

/**
 * @author krzysztofZielinski
 *
 */
public abstract class AbstractSQLiteContact implements DatabaseSpecificContact {
    
    // ~ Fields ================================================================
    
    private Set<SQLiteContactGroup> groups = new HashSet<SQLiteContactGroup>();
    
    private Long contactId = null;
    
    private int templateId = 0;
    private int typeFlags = 0;
    private int accessCount = 0;
    private long creationDate = 0;
    private long lastModification = 0;
    private String guidString;
    private byte[] textFieldsHeader;
	private byte[] binaryFieldsHeader;
    private String textFields;
    private byte[] binaryFields;
    

    // ~ Business Methods ======================================================
    
    public void addGroup(SQLiteContactGroup group)  {
        groups.add(group);
    }

    // ~ Getters/Setters =======================================================

    public Long getContactId() {
        return contactId;
    }

    public void setContactId(Long contactId) {
        this.contactId = contactId;
    }

    public int getTemplateId() {
        return templateId;
    }

    public void setTemplateId(int templateId) {
        this.templateId = templateId;
    }

    public int getTypeFlags() {
        return typeFlags;
    }

    public void setTypeFlags(TypeFlags typeFlags) {
        this.typeFlags = typeFlags.getValue();
    }

    public int getAccessCount() {
        return accessCount;
    }

    public void setAccessCount(int accessCount) {
        this.accessCount = accessCount;
    }

    public long getCreationDate() {
        return creationDate;
    }

    public void setCreationDate(long creationDate) {
        this.creationDate = creationDate;
    }

    public long getLastModification() {
        return lastModification;
    }

    public void setLastModification(long lastModification) {
        this.lastModification = lastModification;
    }

    public String getGuidString() {
        return guidString;
    }

    public void setGuidString(String guidString) {
        this.guidString = guidString;
    }

    public byte[] getTextFieldsHeader() {
        return textFieldsHeader;
    }

    public byte[] getBinaryFieldsHeader() {
        return binaryFieldsHeader;
    }

    public void setBinaryFieldsHeader(String binaryFieldsHeader) {
        this.binaryFieldsHeader = ByteUtil.fromHexString(binaryFieldsHeader);
    }

    public String getTextFields() {
        return textFields;
    }

    public void setTextFields(String textFields) {
        this.textFields = textFields;
    }

    public byte[] getBinaryFields() {
        return binaryFields;
    }

    /**
	 * @param textFieldsHeader the textFieldsHeader to set
	 */
	public void setTextFieldsHeader(byte[] textFieldsHeader) {
		this.textFieldsHeader = textFieldsHeader;
	}

	/**
	 * @param binaryFieldsHeader the binaryFieldsHeader to set
	 */
	public void setBinaryFieldsHeader(byte[] binaryFieldsHeader) {
		this.binaryFieldsHeader = binaryFieldsHeader;
	}

	/**
	 * @param binaryFields the binaryFields to set
	 */
	public void setBinaryFields(byte[] binaryFields) {
		this.binaryFields = binaryFields;
	}

	public Set<SQLiteContactGroup> getGroups() {
        return groups;
    }
    
    public String getFirstName() {
        return null;
    }

    public String getLastName() {
        return null;
    }

    public String getCompanyName() {
        return null;
    }

    public String getFirstNamePrn() {
        return null;
    }

    public String getLastNamePrn() {
        return null;
    }

    public String getCompanyNamePrn() {
        return null;
    }

    
}
