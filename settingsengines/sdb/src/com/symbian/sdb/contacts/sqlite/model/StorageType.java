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
 * @author krzysztofZielinski
 *
 */
public enum StorageType {

    // TODO KZ: unknown values

    TEXT(       (byte)0x00),
    STORE(      (byte)0x01),
    AGENT(      (byte)0x02),
    DATE_TIME(  (byte)0x03);
    
    private byte value;

    private StorageType(byte value) {
        this.value = value;
    }
    
    public byte getValue()  {
        return value;
    }
}
