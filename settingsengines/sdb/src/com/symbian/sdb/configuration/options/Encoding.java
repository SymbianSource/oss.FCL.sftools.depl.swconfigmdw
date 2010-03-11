// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.configuration.options;

public enum Encoding {
	UTF_8("UTF-8"),
	UTF_16("UTF-16");
	
	String value;
	
	private Encoding(String value) {
	    this.value = value;
	}
	
	public String getValue() {
	    return value;
	}
}
