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

package com.symbian.sdb.mode.flow.ced;

/**
 * @author krzysztofzielinski
 *
 */
public enum SDBExecutionExitCodes {

	GENERIC_FLOW_EXECUTION_ERROR_WITH_KEEP_GOING(12),
	CONTACTS_FLOW_EXECUTION_ERROR_WITH_KEEP_GOING(13);
	
	private int exitCode;

	public int getExitCode() {
		return exitCode;
	}

	private SDBExecutionExitCodes(int exitCode) {
		this.exitCode = exitCode;
	}
	
}
