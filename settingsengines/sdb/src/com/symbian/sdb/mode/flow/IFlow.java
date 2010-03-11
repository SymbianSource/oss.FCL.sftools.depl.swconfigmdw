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


import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;

/**
 * Main application flow interface
 * The flow is started after command line arguments are parsed and validated
 * It is responsible for managing the control and object flow in the program
 */
public interface IFlow {
	
	public void validateOptions(CmdLineArgs cmd) throws SDBValidationException;
	
	public void start(CmdLineArgs cmd) throws SDBExecutionException, SdbFlowException;
	
}

