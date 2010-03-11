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
public class DBMSEmailAddress {

    // ~ Fields ================================================================
    
    private Long filedId;
    private Long parentCMID;
    private String value = "";

    // ~ Getters/Setters =======================================================

    public Long getFiledId() {
        return filedId;
    }

    public void setFiledId(Long filedId) {
        this.filedId = filedId;
    }

    public Long getParentCMID() {
        return parentCMID;
    }

    public void setParentCMID(Long parentCMID) {
        this.parentCMID = parentCMID;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }
}
