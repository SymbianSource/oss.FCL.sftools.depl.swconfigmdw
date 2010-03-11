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
public enum SQLiteExtendedAttributes {

    // TODO KZ: unknown values !

    PRIVATE             ((byte)0x01),
    SPEED_DIAL          ((byte)0x02),
    USER_DEFINED_FILTER ((byte)0x03);
    
    private byte value;

    private SQLiteExtendedAttributes(byte value) {
        this.value = value;
    }

    public byte getValue() {
        return value;
    }
}
