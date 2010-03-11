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

import com.symbian.sdb.contacts.model.ContactHint;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactHintField  {

    private short value = 0;
    
    public void addHint(ContactHint hintFlag)   {
        this.value |= hintFlag.getValue();
    }
    
    public short getValue() {
        return value;
    }
    
}
