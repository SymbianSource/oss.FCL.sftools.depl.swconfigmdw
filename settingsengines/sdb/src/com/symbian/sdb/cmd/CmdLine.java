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

package com.symbian.sdb.cmd;

import org.apache.commons.cli2.OptionException;

/**
 * wrapper interface for the apache command line module
 */
public interface CmdLine {

	/**
	 * parser the command line options and arguments 
	 * @param args the command line arguments as given in the application main method
	 * @return true if application should act on the arguments, false otherwise
	 * @throws OptionException if the error was encountered during options parsing
	 */
	public boolean parseArguments(String[] args) throws OptionException;
	
	/**
	 * prints help - command line usage and options description
	 */
	public void printHelp();
	
	/**
	 * prints the header - application version and copy right information
	 */
	public void printHeader();
	
	/**
	 * prints the "finish work" information
	 */
	public void printFinish();
	
	/**
	 * prints the application version
	 */
	public void printVersion();
	
	/**
	 * prints the available modes and their arguments
	 */
	public void printModes();

}


//private Option files;
