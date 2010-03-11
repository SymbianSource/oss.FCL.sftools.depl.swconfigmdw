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



package com.symbian.sdb.mode.flow;

/**
 * @author krzysztofZielinski
 *
 */
public enum ExecutionErrorCode {

	CED_EXECUTION_EXCEPTION(99), 
	GENERIC_FLOW_PARTIAL_EXECUTION_FAILURE(10);
	
	private int codeValue;

	private ExecutionErrorCode(int codeValue) {
		this.codeValue = codeValue;
	}

	public int getValue()	{
		return this.codeValue;
	}
}
