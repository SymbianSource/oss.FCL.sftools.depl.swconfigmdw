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

import java.util.ArrayList;
import java.util.List;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;

/**
 * @author krzysztofZielinski
 *
 */
public class CedOutputProcessorImpl implements CedOutputProcessor {
    private static final Logger logger = Logger.getLogger(CedOutputProcessorImpl.class);
    
    // ~ Fields ================================================================
    private List<String> errors = new ArrayList<String>();
    private List<String> warnings = new ArrayList<String>();

    // ~ Business Methods ======================================================
    
    /* (non-Javadoc)
     * @see com.symbian.sdb.mode.flow.ced.CedOutputProcessor#printErrorSummary()
     */
    public void printErrorSummary(Level level) {
        for(String error: errors){
        	logger.log(level, error);
        }
    }
    
    /* (non-Javadoc)
     * @see com.symbian.sdb.mode.flow.ced.CedOutputProcessor#printWarningSummary()
     */    
    public void printWarningSummary(Level level) {
        for(String warning: warnings){
        	logger.log(level, warning);
        }
    }
    
    /**
     * @return true if errors were detected in the log output
     */
    public boolean hasErrorSummary(){
    	return errors.size()>0;
    }
    
    /**
     * @return true if warnings were detected in the log output
     */
    public boolean hasWarningSummary(){
    	return warnings.size()>0;
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.mode.flow.ced.CedOutputProcessor#process(java.lang.String)
     */
    public String process(String cedOutput, int logLineNumber) {
    	// ignore the ending "ERROR" message as this is handled by the return code
    	//
    	if(!cedOutput.equals("ERROR")){
    		CedErrorType error = getErrorCode(cedOutput);
    		if(error != null){
    			if(error.getLevel() == CedErrorLevel.error){
    				handleError(error, cedOutput, logLineNumber);
    			}
    			else {
    				handleWarning(error, cedOutput, logLineNumber);
    			}
    		}
    	}
    	return cedOutput;
    }
    
	/**
	 * @param errorType	The error that has matched on the log line 
	 * @param inputLine	The input line that matched to the log
	 */
	private void handleError(CedErrorType errorType, String inputLine, int logLineNumber) {
		errors.add("CED: "+errorType.getMessage(inputLine.trim())+" at line "+logLineNumber);
	}

	/**
	 * @param warningType	The warning that has matched on the log line 
	 * @param inputLine	The input line that matched to the log
	 */
	private void handleWarning(CedErrorType warningType, String inputLine, int logLineNumber) {
		warnings.add("CED: "+warningType.getMessage(inputLine.trim())+" at line "+logLineNumber);
	}

	/**
	 * @param inputLine the line of CED output that may contain an error
	 * @return the CedErrorType identified in the input line or null if none.
	 */
	private CedErrorType getErrorCode(String inputLine) {
		return CedErrorType.getErrorType(inputLine);
	}

	/**
	 * @return the list of error messages in the summary
	 * 
	 */
	protected List<String> getErrors() {
		return this.errors;
	}
	
	/**
	 * @return the list of error messages in the summary
	 * 
	 */
	protected List<String> getWarnings() {
		return this.warnings;
	}

}
