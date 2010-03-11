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

import static org.junit.Assert.assertEquals;

import java.io.File;
import java.io.IOException;
import java.util.Collections;

import org.junit.Test;

/**
 * @author jamesclark
 *
 */
public class ProxyProcessBuilderTest {

	private static final File EXE_DIR = new File("foo");
	
	public static boolean startedFlag = false;
	public static boolean directoryReqestedFlag = false;
	public static boolean redirectErrorStreamReqestedFlag = false;
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.ced.ProxyProcessBuilder#ProxyProcessBuilder(java.util.List)}.
	 */
	@Test
	public void testProxyProcessBuilder() {
		// TODO fix exception caused by jMock it  Looks like a bug in a jmockit dependency http://jira.codehaus.org/browse/SUREFIRE-298  
		/*Mockit.redefineMethods(ProcessBuilder.class, MockProcessBuilder.class);
		ProxyProcessBuilder builder = new ProxyProcessBuilder(Collections.EMPTY_LIST);
		builder.directory(EXE_DIR);
		builder.redirectErrorStream(true);
		try {
			builder.start();
		} catch (IOException e) {
			fail("No exception should be thrown");
		}
		builder.directory();
		
		assertTrue("The mock process builder should have recieved the start message.", startedFlag);
		assertTrue("The mock process builder should have recieved the directory message.", directoryReqestedFlag);
		assertTrue("The mock process builder should have been set to redirect the error stream.", redirectErrorStreamReqestedFlag);
		*/
	}
	
	public void testProxyProcessBuilder_checkGettersAnsSetters() {
		ProxyProcessBuilder builder = new ProxyProcessBuilder(Collections.EMPTY_LIST);
		builder.directory(EXE_DIR);
		builder.redirectErrorStream(true);
		
		
		assertEquals("The directory value should have been updated.",EXE_DIR, builder.directory());
		assertEquals("The environment should be initialised to be the same as the System environment.", System.getenv(), builder.environment());
	}
	
	public static final class MockProcessBuilder{
		/*
		 * (non-Javadoc)
		 * 
		 * @see
		 * com.symbian.sdb.mode.flow.ced.IProcessBuilder#directory(java.io.File)
		 */
		public ProcessBuilder directory(File exeDirectory) {
			assertEquals("The executable directory should be passed straigh on", EXE_DIR, exeDirectory);
			return null;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#start()
		 */
		public Process start() throws IOException {
			startedFlag = true;
			
			return null;
		}
		/* (non-Javadoc)
		 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#directory()
		 */
		public File directory() {
			directoryReqestedFlag = true;
			return null;
		}
		
		/* (non-Javadoc)
		 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#redirectErrorStream(boolean)
		 */
		public ProcessBuilder redirectErrorStream(boolean redirectErrorStream) {
			redirectErrorStreamReqestedFlag = redirectErrorStream;
			return null;
		}
	}

}
