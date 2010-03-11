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

import com.symbian.sdb.contacts.model.ContactHint;
import com.symbian.sdb.contacts.model.common.AbstractShortType;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactExtHintField extends AbstractShortType {

    // ~ Constructors ==========================================================
    
    /**
     * @param value
     */
    public ContactExtHintField() {
        super((short) 0);
    }

    // ~ Business Methods ======================================================
    
    public void setField(ContactHint contactExtHintFieldsValue)  {
        this.value |= contactExtHintFieldsValue.getValue();
    }
}
