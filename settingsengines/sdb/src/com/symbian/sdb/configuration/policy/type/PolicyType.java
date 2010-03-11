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

public enum PolicyType {
	DEFAULT(-1, -2),
	SCHEMA(0, -1),
	READ(1, -1),
	WRITE(2, -1)
	; 
	
	private int fPolicyType;
	private int fObjectType;
	
	private PolicyType(int aPolicyType, int aObjectType){
		fPolicyType = aPolicyType;
		fObjectType = aObjectType;
	}
	
	public int getPolicyTypeID(){
		return fPolicyType;
	}
	
	public int getObjectTypeID(){
		return fObjectType;
	}
	
	
}
