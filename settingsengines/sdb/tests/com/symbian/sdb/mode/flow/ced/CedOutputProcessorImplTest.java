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

import static org.junit.Assert.*;

import java.util.Arrays;
import java.util.Iterator;

import org.apache.log4j.Appender;
import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Test;

/**
 * @author jamesclark
 *
 */
public class CedOutputProcessorImplTest {

	CedOutputProcessorImpl processor = new CedOutputProcessorImpl();
	
	@Before
	public void setup(){
		// reset the processor
		processor = new CedOutputProcessorImpl();
	}
	
	
	/************************************************************
	 * This section of tests covers the more standardised errors
	 * eg those starting with Err, ERR, ERROR or Error
	 ************************************************************/
	@Test
	public void testGetSdbOutput_ERROR() {
		
		// Don't pick-up the final summary
		String stdEnd = "ERROR";
		assertEquals(stdEnd, processor.process(stdEnd, -1));
		assertFalse("The processor should not have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_ERR() {
		// General error cases
		String error1 = "ERR ";
		assertEquals(error1, processor.process(error1, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	@Test
	public void testGetSdbOutput_ERR_colon() {
		String error2 = "ERR: ";
		assertEquals(error2, processor.process(error2, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_ws_ERR() {
		String error3 = "  ERR ";
		assertEquals(error3, processor.process(error3, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_Error() {
		String error4 = "Error ";
		assertEquals(error4, processor.process(error4, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_Error_colon() {
		String error5 = "Error: ";
		assertEquals(error5, processor.process(error5, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_no_error() {
		String ok1 = "no error ";
		assertEquals(ok1, processor.process(ok1, -1));
		assertFalse("The processor should not have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_not_ERR() {
		String ok2 = "not ERR ";
		assertEquals(ok2, processor.process(ok2, -1));
		assertFalse("The processor should not have logged an error.", processor.hasErrorSummary());
	}
	
	
	
	/**********************************************************
	 * This section covers the selection of specific error message types
	 ************************************************************/
	
	@Test
	public void testGetSdbOutput_MESHERR(){
		String error = "MESHERR:";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_Insert_failed(){
		String error = "Insert failed:";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_CENREP_Create_Failed(){
		String error = "Failed to create Central Repository with ID : %x   (error %d)";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	
	
	@Test
	public void testGetSdbOutput_CENREP_commit_fail(){
		String error = "Central Repository CommitTransaction returned err [%d]";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_InsertRecordFail(){
		String error = "Insert record failed Err:";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_CreateRecordFail(){
		String error = "Creating Record set Failed";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	
	@Test
	public void testGetSdbOutput_CommsDat_could_not_connect(){
		String error = "Could not connect to Commsdat [%d ]";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_Failed_To_log(){
		String error = "Failed to open the output log file ";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_CommsDat_CorruptHexVal(){
		String error = "  Corrupt hex value";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	@Test
	public void testGetSdbOutput_Cannot_resolve(){
		String error = "Cannot resolve table entry reference :";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
	}
	
	/*******************************************************************
	 * Checking log level for warning 
	 *******************************************************************/
	@Test
	public void testGetSdbOutput_Deprecated_warning(){
		String error = "Warning - Use of deprecated parameter [%S]";
		assertEquals(error, processor.process(error, -1));
		assertTrue("The processor should have logged a warning.", processor.hasWarningSummary());
		assertFalse("The processor should not have logged an error.", processor.hasErrorSummary());
	}
	
	/*******************************************************************
	 * All Known errors in one test
	 **********************************************************************/
	
	@Test
	public void testGetSdbOutput_allKnownGeneralErrors() {
		String[] input = new String[]{ 
			"ERR: record id %d already inserted, skipping (check input file)",
			"ERR: Special char processing of %S failed due to %S",
			"  ERR Boolean mismatch column [%S] value [%S]",
			"ERR: Corrupt hex value '%S' - substituting 0",
			"ERR Integer mismatch column [%S] value [%S]",
			"ERR UInt32 mismatch column [%S] value [%S]",
			"ERR:  Token error [%S]",
			"ERR: Unknown or deprecated table : [%S]",
			"ERR: Unknown record : [%S]",
			"ERR: Use of [%S] inside deprecated [%S]",
			"ERR: Error parsing xml, err=%d",
			"Error parsing table [%S]",
			"Error parsing record [%S]",
			"Error parsing parameter [%S]",
			"ERROR: CommitTransaction returned err [%d]",
			"ERR Table %S Expected [%d] values, read [%d].Field count mismatch",
			"Error %d inserting record #%d to %S",
			"ERR: Configuration file [%S] could not be opened",
			"Warning - Use of deprecated parameter [%S]", 
			"MESHERR: Configuration file [%S] could not be opened",
			"MESHERR: Configuration file [%S], processing failed, reason=<%d>",
			"Failed to create Central Repository with ID : %x   (error %d)",
			"Central Repository CommitTransaction returned err [%d]",
			"Insert record failed Err:",
			"Creating Record set Failed [%d ]",
			"Could not connect to Commsdat [%d ]",
			"Failed to open the output log file",
			"  Corrupt hex value '%S' - substituting 0",
			"Cannot resolve table entry reference : [%S.%S]"
		};
		
		String[] inputErrors = new String[]{ 
				"ERR: record id %d already inserted, skipping (check input file)",
				"ERR: Special char processing of %S failed due to %S",
				"  ERR Boolean mismatch column [%S] value [%S]",
				"ERR: Corrupt hex value '%S' - substituting 0",
				"ERR Integer mismatch column [%S] value [%S]",
				"ERR UInt32 mismatch column [%S] value [%S]",
				"ERR:  Token error [%S]",
				"ERR: Unknown or deprecated table : [%S]",
				"ERR: Unknown record : [%S]",
				"ERR: Use of [%S] inside deprecated [%S]",
				"ERR: Error parsing xml, err=%d",
				"Error parsing table [%S]",
				"Error parsing record [%S]",
				"Error parsing parameter [%S]",
				"ERROR: CommitTransaction returned err [%d]",
				"ERR Table %S Expected [%d] values, read [%d].Field count mismatch",
				"Error %d inserting record #%d to %S",
				"ERR: Configuration file [%S] could not be opened",
				"MESHERR: Configuration file [%S] could not be opened",
				"MESHERR: Configuration file [%S], processing failed, reason=<%d>",
				"Failed to create Central Repository with ID : %x   (error %d)",
				"Central Repository CommitTransaction returned err [%d]",
				"Insert record failed Err:",
				"Creating Record set Failed [%d ]",
				"Could not connect to Commsdat [%d ]",
				"Failed to open the output log file",
				"  Corrupt hex value '%S' - substituting 0",
				"Cannot resolve table entry reference : [%S.%S]"
			};
		
		String[] inputWarnings = new String[]{ 
				"Warning - Use of deprecated parameter [%S]"
			};
		
		for(String error: input){
			assertEquals(error, processor.process(error, -1));
		}
		assertTrue("The processor should have logged an error.", processor.hasErrorSummary());
		Iterator<String> outputErrors = processor.getErrors().iterator(); 
		for(String inputError: inputErrors){
			String outputError = outputErrors.next();
			assertTrue("The output error should contain the original error message. \nInput: "+inputError+"\nOutput: "+outputError,outputError.contains(inputError.trim()));
		}
		
		assertTrue("The processor should have logged a warning.", processor.hasWarningSummary());
		Iterator<String> outputWarnings = processor.getWarnings().iterator(); 
		for(String inputWarning: inputWarnings){
			String outputWarning = outputWarnings.next();
			assertTrue("The output warning should contain the original error message. \nInput: "+inputWarning+"\nOutput: "+outputWarning, outputWarning.contains(inputWarning.trim()));
		}
	}
	
}
