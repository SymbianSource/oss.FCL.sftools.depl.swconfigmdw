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

package com.symbian.sdb.contacts.model.common;

/**
 * @author krzysztofZielinski
 *
 */
public class AbstractShortType {

    // ~ Fields ================================================================
    
    protected short value = 0;

    // ~ Constructors ==========================================================
    
    public AbstractShortType(short value) {
        this.value = value;
    }

    // ~ Getters/Setters =======================================================

    public short getValue() {
        return value;
    }

}