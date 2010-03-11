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
public class DBMSPhoneNumber {

    // ~ Fields ================================================================
    
    private Long id = null;
    private Integer phoneMatching = 0;
    private Integer extendedPhoneMatching = 0;

    // ~ Getters/Setters =======================================================

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getPhoneMatching() {
        return phoneMatching;
    }

    public void setPhoneMatching(Integer phoneMatching) {
        this.phoneMatching = phoneMatching;
    }

    public Integer getExtendedPhoneMatching() {
        return extendedPhoneMatching;
    }

    public void setExtendedPhoneMatching(Integer extendedPhoneMatching) {
        this.extendedPhoneMatching = extendedPhoneMatching;
    }

}
