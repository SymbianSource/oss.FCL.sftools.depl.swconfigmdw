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

import com.symbian.sdb.contacts.model.common.AbstractByteType;


/**
 * Contact Attributes are bit-flags to represent some special characters of the contact 
 * and stored in second byte of the 4 bytes integer (type_flags column)
 */
public class SQLiteContactAttribute extends AbstractByteType {


    // ~ Global Constant Fields ================================================

    public static final SQLiteContactAttribute SYSTEM = new SQLiteContactAttribute((byte)1);
    public static final SQLiteContactAttribute HIDDEN = new SQLiteContactAttribute((byte)2);
    public static final SQLiteContactAttribute COMPRESSED_GUID = new SQLiteContactAttribute((byte)4);
    public static final SQLiteContactAttribute DELETED = new SQLiteContactAttribute((byte)8);
    
    // ~ Constructors ==========================================================

    /**
     * @param value
     */
    private SQLiteContactAttribute(byte value) {
        super(value);
    }
    
}
