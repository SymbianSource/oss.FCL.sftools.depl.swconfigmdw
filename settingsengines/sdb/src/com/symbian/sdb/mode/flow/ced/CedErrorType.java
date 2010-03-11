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

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * @author jamesclark
 *
 */
public enum CedErrorType {

	DeprecatedUseError(Pattern.compile("\\s*(?i)Warning - Use of deprecated parameter.*"), CedErrorLevel.warn),
	
	MeshError(Pattern.compile("\\s*MESHERR.*"), CedErrorLevel.error),

	InsertFailed(Pattern.compile("\\s*Insert failed.*"), CedErrorLevel.error),
	InsertRecordFailed(Pattern.compile("\\s*Insert record failed Err:.*"), CedErrorLevel.error),
	
	CreateRecordFailed(Pattern.compile("\\s*Creating Record set Failed.*"), CedErrorLevel.error),
	
	CenRep_CreateFail(Pattern.compile("\\s*Failed to create Central Repository with ID.*"), CedErrorLevel.error),
	CenRep_CommitFail(Pattern.compile("\\s*Central Repository CommitTransaction returned err.*"), CedErrorLevel.error),
	
	CouldNotConnect(Pattern.compile("\\s*Could not connect to Commsdat.*"), CedErrorLevel.error),
	
	CouldNotLog(Pattern.compile("\\s*Failed to open the output log file.*"), CedErrorLevel.error),
	
	// looks like it's not used anymore (candidate to be removed)
	CorruptValue(Pattern.compile("\\s*Corrupt hex value.*"), CedErrorLevel.error),
	
	CannotResolve(Pattern.compile("\\s*Cannot resolve table entry reference.*"), CedErrorLevel.error),
	
	GeneralError(Pattern.compile("\\s*(?i)ERR:?.*"), CedErrorLevel.error),
	;
	private String errorMessage = "";
	private Pattern pattern;
	private CedErrorLevel level;
	
	CedErrorType(String errorMessage, Pattern pattern, CedErrorLevel level) {
		this.errorMessage = errorMessage;
		this.pattern = pattern;
		this.level = level;
	}
	
	CedErrorType(Pattern pattern, CedErrorLevel level) {
		this.pattern = pattern;
		this.level = level;
	}
	
	/**
	 * @param inputLine A line of log output that may contain an error message 
	 * @return The error type indicated by the input or null if the input does not indicate an error.
	 */
	public static CedErrorType getErrorType(String inputLine) {
		for(CedErrorType errorCode : CedErrorType.values()){
			if(errorCode.containsErrorCode(inputLine)){
				return errorCode;
			}
		}
		return null;
	}
	
	/**
	 * 
	 * @param message A line of text that may contain an error message
	 * @return true if the message contains an error message matching one of the error types (including unknown error)
	 */
	public boolean containsErrorCode(String message){
		Matcher matcher = pattern.matcher(message);
		return matcher.matches();
	}

	/**
	 * @param inputLine
	 * @return
	 */
	public String getMessage(String inputLine) {
		return errorMessage+inputLine;
	}
	
	public CedErrorLevel getLevel(){
		return level;
	}
}
