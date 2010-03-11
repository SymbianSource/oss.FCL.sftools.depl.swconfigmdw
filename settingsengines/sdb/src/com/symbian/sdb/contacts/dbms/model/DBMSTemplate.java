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
 * Class to represent template contact record in contacts 
 * 
 * @author Tanaslam1
 *
 */
public abstract class DBMSTemplate extends AbstractDBMSContact {
	
	//~ Constructors ------------------------------------------
	public DBMSTemplate() {
		super();
		initializeFields();
		this.identityTable.setContactExtHintField(new ContactExtHintField());
		this.identityTable.setContactHintField(new ContactHintField());
	}
	
    protected abstract void initializeFields();

    // ~ Business methods ----------------------------------------
	/**
	 * Set preferred template id for template
	 */
    public void setPrefTemplateRefId(Integer prefTemplateRefId) {
        this.prefTemplateRefId = prefTemplateRefId;
    }

    /**
     * set template contact attributes
     * @param attributes
     */
	@Override
    public void setAttributes(DBMSContactAttribute attributes) {
        super.setAttributes(attributes);
        this.identityTable.setAttribute(attributes);
    }

	/**
	 * Set contact id for template
	 */
	@Override
	public void setId(Long id) {
		super.setId(id);
		this.identityTable.setParentCMID(id);
	}

} //End of class
