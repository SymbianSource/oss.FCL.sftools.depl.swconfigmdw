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

import com.symbian.sdb.contacts.model.common.AbstractShortType;



/**
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactFieldAttributes extends AbstractShortType {

    // ~ Constants Fields ======================================================
    
    public static final SQLiteContactFieldAttributes UNKNOWN = new SQLiteContactFieldAttributes((byte)0x010);
    public static final SQLiteContactFieldAttributes HIDDEN = new SQLiteContactFieldAttributes((byte)2);
    public static final SQLiteContactFieldAttributes SYNCHRONIZE = new SQLiteContactFieldAttributes((byte)4);
    public static final SQLiteContactFieldAttributes USE_TEMPLATE_DATA = new SQLiteContactFieldAttributes((short) 0x200);

    // ~ Constructors ==========================================================
    
    private SQLiteContactFieldAttributes(short value) {
        super(value);
    }
    
}
