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

import com.symbian.sdb.contacts.model.common.AbstractShortType;


/**
 * @author krzysztofZielinski
 *
 */
public class DBMSContactAttribute extends AbstractShortType {

    // ~ Constants Fields ======================================================
    
    public static final DBMSContactAttribute SYSTEM = new DBMSContactAttribute((short)1);
    public static final DBMSContactAttribute HIDDEN = new DBMSContactAttribute((short)2);
    public static final DBMSContactAttribute COMPRESSED_GUID = new DBMSContactAttribute((short)4);
    public static final DBMSContactAttribute DELETED = new DBMSContactAttribute((short)8);

    // ~ Constructors ==========================================================

    private DBMSContactAttribute(short value) {
        super(value);
    }
    
}