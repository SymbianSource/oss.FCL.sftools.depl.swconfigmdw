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


import java.util.Date;
import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.DatabaseSpecificContact;
import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;

/**
 * Contacts model class for DBMS database schema. Used as a base class for {@link DBMSContactCard} and {@link DBMSContactGroup} 
 * 
 * @author krzysztofZielinski
 *
 */
public abstract class AbstractDBMSContact implements DatabaseSpecificContact {
    
    // ~ Fields ================================================================

    private Long id = null;
    protected ContactType type;
    // changeable for contactCards only (fixed value for groups) 
    protected Integer prefTemplateRefId;
    private String UIDString;
    private Date lastModified;
    private Date contactCreationDate;
    private DBMSContactAttribute attributes;
    private Integer replicationCount = 0;
    private AbstractContactHeader header;
    private ContactTextBlob textBlob;
    private String searchableText;
    private Set<DBMSContactGroup> groups = new HashSet<DBMSContactGroup>();
    
    protected IdentityTable identityTable = null;

    private Set<SpeedDialData> speedDialData = new HashSet<SpeedDialData>();
    
    // ~ Getters/Setters =======================================================

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public ContactType getType() {
        return type;
    }

    public Integer getPrefTemplateRefId() {
        return prefTemplateRefId;
    }

    public String getUIDString() {
        return UIDString;
    }

    public void setUIDString(String string) {
        UIDString = string;
    }

    public Date getLastModified() {
        return lastModified;
    }

    public void setLastModified(Date lastModified) {
        this.lastModified = lastModified;
    }

    public Date getContactCreationDate() {
        return contactCreationDate;
    }

    public void setContactCreationDate(Date contactCreationDate) {
        this.contactCreationDate = contactCreationDate;
    }

    public DBMSContactAttribute getAttributes() {
        return attributes;
    }

    public void setAttributes(DBMSContactAttribute attributes) {
        this.attributes = attributes;
    }

    public Integer getReplicationCount() {
        return replicationCount;
    }

    public void setReplicationCount(Integer replicationCount) {
        this.replicationCount = replicationCount;
    }

    public AbstractContactBlobField getHeader() {
        return header;
    }

    public void setHeader(AbstractContactHeader header) {
        this.header = header;
    }

    public ContactTextBlob getTextBlob() {
        return textBlob;
    }

    public void setTextBlob(ContactTextBlob textBlob) {
        this.textBlob = textBlob;
    }

    public String getSearchableText() {
        return searchableText;
    }

    public void setSearchableText(String searchableText) {
        this.searchableText = searchableText;
    }

    public IdentityTable getIdentityTable() {
        return identityTable;
    }

    /**
     * @param dbmsGroup
     */
    public void addGroup(DBMSContactGroup dbmsGroup) {
        groups.add(dbmsGroup);
    }

    public Set<DBMSContactGroup> getGroups() {
        return groups;
    }

	public void setType(ContactType type) {
		this.type = type;
	}

	/**
	 * @return the speedDialData
	 */
	public Set<SpeedDialData> getSpeedDialData() {
		return speedDialData;
	}

	/**
	 * @param speedDialData the speedDialData to set
	 */
	public void setSpeedDialData(Set<SpeedDialData> speedDialData) {
		this.speedDialData = speedDialData;
	}

}
