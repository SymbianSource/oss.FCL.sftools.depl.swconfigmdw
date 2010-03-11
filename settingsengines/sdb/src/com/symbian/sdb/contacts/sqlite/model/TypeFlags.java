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
import com.symbian.sdb.contacts.sqlite.BitsOperationsUtil;


/**
 * Class representing type_flags column in contact table of SQLite contact database schema
 * 
 * @author krzysztofZielinski
 *
 */
public class TypeFlags {

    // ~ Fields ================================================================
    
    private byte fistByte = 0;
    private byte secondByte = 0;
    private byte thirdByte = 0;
    private byte fourthByte = 0;

    // ~ Constructors ==========================================================
    
    public TypeFlags(ContactType contactType) {
        setContactType(contactType);
    }

    // ~ Business Methods ======================================================
    
    /**
     * @param sQLiteContactAttribute
     */
    public void setContactAttributes(SQLiteContactAttribute sQLiteContactAttribute) {
        // perform OR with added attribute
        this.secondByte |= sQLiteContactAttribute.getValue();
    }

    public void setContactHintField(ContactHintField contactHintFields) {
        // perform OR with added hit fields constant
        this.thirdByte = BitsOperationsUtil.getHigherByte(contactHintFields.getValue()); 
        this.fourthByte = BitsOperationsUtil.getLowerByte(contactHintFields.getValue());
    }
    
    // ~ Internal Implementation Methods =======================================
    
    /**
     * @param contactType
     */
    private void setContactType(AbstractByteType contactType) {
        this.fistByte = contactType.getValue();
    }

    // ~ Getters/Setters =======================================================

    public int getValue()   {
        return BitsOperationsUtil.getIntFormBytes(fistByte, secondByte, thirdByte, fourthByte);
    }
    
}
