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

import org.apache.log4j.Level;

/**
 * Processes CED output i.e. parse output string, check if there is any error, translates SDB output to SDB output 
 * 
 * @author krzysztofZielinski
 *
 */
public interface CedOutputProcessor {

    /**
     * Parse a line of CED output. If an error is found the error summary is updated.
     * This also translates the CED output into suitable SDB output if required.
     * 
     * @param cedOutputLine the line of CED output to be translated
     * @param logLineNumber the line number for this log statement
     * @return the input translated to suitable SDB output.
     */
    public String process(String cedOutputLine, int logLineNumber);
    
    /**
     * Prints the error summary to the specified log level
     * @param the level at which the summary should be raised
     */
    public void printErrorSummary(Level level);
    
    /**
     * 
     * @return true if the processor has detected any errors to be summarised.
     */
    public boolean hasErrorSummary();
    
    /**
     * Prints the warning summary to the specified log level
     * @param the level at which the summary should be raised
     */
    public void printWarningSummary(Level level);
    
    /**
     * 
     * @return true if the processor has detected any warnings to be summarised.
     */
    public boolean hasWarningSummary();


}
