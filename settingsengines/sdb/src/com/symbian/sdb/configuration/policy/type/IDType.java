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

package com.symbian.sdb.configuration.policy.type;

public enum IDType {
	VID(5),
	SID(4)
	;
	
	private Integer fValue;
	
	private IDType(int aArg){
		fValue = aArg;
	}
	
	public byte toByte(){
		return fValue.byteValue();
	}
	
}
