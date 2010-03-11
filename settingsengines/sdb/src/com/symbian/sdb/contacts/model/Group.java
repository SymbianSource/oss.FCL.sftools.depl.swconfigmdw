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

package com.symbian.sdb.contacts.model;

/**
 * Represents group  for contact
 * 
 * @author krzysztofZielinski
 *
 */
public class Group {

	private static final long NOT_SET = -2l;
	
    //~ Fields ================================================================
    
    private long groupId = NOT_SET;
    private String name;

    // ~ Constructors ==========================================================

    public Group(
            String name) {
        super();
        this.name = name;
    }

    // ~ Getters/Setters =======================================================

    public String getName() {
        return name;
    }

    public long getGroupId() {
        return groupId;
    }

    public void setGroupId(long groupId) {
        this.groupId = groupId;
    }
    
    public boolean isPersisted(){
    	return this.groupId == NOT_SET;
    }
    
}
