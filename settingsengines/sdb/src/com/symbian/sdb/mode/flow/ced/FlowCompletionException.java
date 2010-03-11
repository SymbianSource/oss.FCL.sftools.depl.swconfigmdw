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
 * This exception type is used to indicate that an error has occured that can't be recovered from.
 * The application will simply exit with the specified return code at this point. 
 *
 * This exception type maybe refactored to contain a message (and log level) that should be displayed before exit. 
 */
@SuppressWarnings("serial")
public class FlowCompletionException extends RuntimeException {

	private int returnCode;
	
	public FlowCompletionException(SDBExecutionExitCodes exitCode) {
		this.returnCode = exitCode.getExitCode();
	}

	protected FlowCompletionException(int returnCode) {
		super();
		this.returnCode = returnCode;
	}

	/**
	 * @return the return code
	 */
	public int getReturnCode() {
		return returnCode;
	}
	
	
}
