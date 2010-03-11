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

/**
 * Represents types of communication address for SQLite 
 * 
 * @author krzysztofZielinski
 *
 */
public class SQLiteCommunicationAddressType {

    // ~ Public Static Constants ===============================================
    public static SQLiteCommunicationAddressType EMAIL = new SQLiteCommunicationAddressType(1);
    public static SQLiteCommunicationAddressType PHONE = new SQLiteCommunicationAddressType(2);
    
    // ~ Fields ================================================================
    
    private int value;
    
    // ~ Constructors ==========================================================
    
    private SQLiteCommunicationAddressType(int value) {
        this.value = value;
    }

    // ~ Getters/Setters =======================================================

    public int getValue() {
        return value;
    }
    
}
