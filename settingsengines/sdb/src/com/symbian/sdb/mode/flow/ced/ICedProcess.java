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
 * 
 * represents a Ced process that is executed to generate specific CED DBs
 *
 */
public interface ICedProcess {
	
	/**
	 *	Executes the relevant CED command and pipes output to the logger and
	 *  @throws SdbFlowException if an error occurs creating or executing the process
	 */
	public void start() throws SdbFlowException;
	
	/**
	 * Add option/values to the command to be executed
	 * @param String... options and/or values to add to command execution
	 */
	public void addOptions(String... options);
}
