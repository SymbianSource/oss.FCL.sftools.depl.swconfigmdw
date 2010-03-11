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

import com.symbian.sdb.util.LongArray;



/**
 * Represents group as a whole (tables: contact, group and group2)
 * 
 * @author krzysztofZielinski
 *
 */
public class DBMSContactGroup extends AbstractDBMSContact {

    private static final Integer NO_TEMPLATE = -1;
    
    // ~ Fields ================================================================
    
    LongArray members = new LongArray();
    String name;
    // ~ Constructors ==========================================================
    
	public DBMSContactGroup() {
        super();
        // groups don't use any template
        this.prefTemplateRefId = NO_TEMPLATE;

        this.type = ContactType.GROUP; 
        this.identityTable = new IdentityTable(this.type);
    }

    
    // ~ Getters/Setters =======================================================

    public LongArray getMembers() {
		return members;
	}

	public void setMembers(LongArray members) {
		this.members = members;
	}

	public void addMember(int id) {
		members.add(id);
	}
	
	public void addMember(AbstractDBMSContact contact) {
		members.add(contact.getId());
	}
	
	public String getName() {
		return name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
}
