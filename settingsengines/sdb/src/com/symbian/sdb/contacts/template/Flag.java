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

package com.symbian.sdb.contacts.template;

public class Flag {
	private Integer value;
	private String UID;

	public Flag(String UID, Integer value) {
		this.UID = UID;
		this.value = value;
	}

	public Integer getValue() {
		return value;
	}

	public String getUID() {
		return UID;
	}

    public boolean same(Flag flag) {
        return this.value.equals(flag.value);
    }
}
