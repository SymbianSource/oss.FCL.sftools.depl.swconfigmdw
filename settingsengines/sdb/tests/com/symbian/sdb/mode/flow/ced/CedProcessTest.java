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
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.List;

import junit.framework.JUnit4TestAdapter;
import mockit.Mockit;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.util.ProcessBuilderFactory;


/**
 * @author jamesclark
 *
 */
public class CedProcessTest {

	private static enum testCase {
		startOK,
		startIOException,
		startInterrupt;
	}
	
	private static testCase _currentTest;
	private CedProcess _fixture;
	private static final String ADDITIONAL_OPTION = "AdditionalOption";
	protected static final String Exception_Message = "test exception";
	
	@Before
	public void setup(){
		_fixture = new CedProcess(CedSchema.ced95);
	}
	
	@Test
	public void testAddOption() throws Exception{
		_currentTest = null;
		// mock process builder to validate command list
		//
		Mockit.redefineMethods(ProcessBuilderFactory.class, ProcessBuilderFactoryMock.class);
		Mockit.redefineMethods(MockProcess.class, ProcessMock.class);
		
		_fixture.addOptions(ADDITIONAL_OPTION);
		
		try {
			_fixture.start();
			fail();
		} catch (NullPointerException e) {
			// This should happen as mock returns null
		}
		Mockit.restoreAllOriginalDefinitions();
	}
	
	@Test
	public void testStart_OK() throws Exception{
		_currentTest = testCase.startOK;
		// mock process builder to validate command list
		//
		Mockit.redefineMethods(ProcessBuilderFactory.class, ProcessBuilderFactoryMock.class);
		Mockit.redefineMethods(MockProcess.class, ProcessMock.class);
		
		_fixture.addOptions(ADDITIONAL_OPTION);
		
		_fixture.start();
		
		Mockit.restoreAllOriginalDefinitions();
	}
	
	@Test
	public void testStart_IOException() throws Exception{
		_currentTest = testCase.startIOException;
		// mock process builder to validate command list
		//
		Mockit.redefineMethods(ProcessBuilderFactory.class, ProcessBuilderFactoryMock.class);
		Mockit.redefineMethods(MockProcess.class, ProcessMock.class);
		
		_fixture.addOptions(ADDITIONAL_OPTION);
		
		try {
			_fixture.start();
			fail("The start should end with an exception and not complete normally");
		} catch (SdbFlowException e) {
			assertEquals(IOException.class, e.getCause().getClass());
			assertEquals(Exception_Message, e.getCause().getLocalizedMessage()); 
		}
		Mockit.restoreAllOriginalDefinitions();
	}
	

	@Test
	public void testStart_InterruptedException() throws Exception{
		_currentTest = testCase.startInterrupt;
		// mock process builder to validate command list
		//
		Mockit.redefineMethods(ProcessBuilderFactory.class, ProcessBuilderFactoryMock.class);
		Mockit.redefineMethods(MockProcess.class, ProcessMock.class);
		
		_fixture.addOptions(ADDITIONAL_OPTION);
		
		try {
			_fixture.start();
			fail("The start should end with an exception and not complete normally");
		} catch (Exception e) {
			assertEquals(InterruptedException.class, e.getCause().getClass());
			assertEquals(Exception_Message, e.getCause().getLocalizedMessage()); 
		}
		Mockit.restoreAllOriginalDefinitions();
	}
	
	public static final class ProcessBuilderFactoryMock {

		public static IProcessBuilder getProcessBuilder(List<String> cmdArgs){
			
			//assertTrue("The command should contain the 9.5 exe", 
			//        cmdArgs.contains("\"" + CedSchema.ced95.getExeDirectory() + CedSchema.ced95.getExeName()+ "\"") );
			
			assertEquals("The command list should contain 4 arguements", 4, cmdArgs.size());
			
			assertTrue("The command should contain the additional option", cmdArgs.contains(ADDITIONAL_OPTION));
			
			Mockery processBuilderMockery = new Mockery();
			final IProcessBuilder proBuilderMock = processBuilderMockery.mock(IProcessBuilder.class);
			try {
				processBuilderMockery.checking(new Expectations() {{
					allowing (proBuilderMock).directory(with(any(File.class)));
					allowing (proBuilderMock).start(); will(returnValue(new MockProcess()));
					allowing (proBuilderMock).directory();will(returnValue(new File("foo")));
				}});
			} catch (IOException e) {
				fail(e.getLocalizedMessage());
			}
				
			
			return getPBMockForTest();
		}
	}
	
	public static IProcessBuilder getPBMockForTest(){
		IProcessBuilder retval = null;
		Mockery processBuilderMockery = new Mockery();
		switch (_currentTest) {
		case startOK:
			final IProcessBuilder proBuilderMock = processBuilderMockery.mock(IProcessBuilder.class);
			try {
				processBuilderMockery.checking(new Expectations() {{
					allowing (proBuilderMock).directory(with(any(File.class)));
					allowing (proBuilderMock).start(); will(returnValue(new MockProcess()));
					allowing (proBuilderMock).directory();will(returnValue(new File("foo")));
					
				}});
			} catch (IOException e) {
				fail(e.getLocalizedMessage());
			}
			retval = proBuilderMock;
			break;
			
		case startInterrupt:
			final IProcessBuilder proBuilderMock2 = processBuilderMockery.mock(IProcessBuilder.class);
			try {
				processBuilderMockery.checking(new Expectations() {{
					allowing (proBuilderMock2).directory(with(any(File.class)));
					allowing (proBuilderMock2).start(); will(returnValue(new MockProcess()));
					allowing (proBuilderMock2).directory();will(returnValue(new File("foo")));
					
				}});
			} catch (IOException e) {
				fail(e.getLocalizedMessage());
			}
			retval = proBuilderMock2;
			break;
			
		case startIOException:
			final IProcessBuilder proBuilderMock3 = processBuilderMockery.mock(IProcessBuilder.class);
			try {
				processBuilderMockery.checking(new Expectations() {{
					allowing (proBuilderMock3).directory(with(any(File.class)));
					allowing (proBuilderMock3).start(); will(throwException(new IOException(Exception_Message)));
					allowing (proBuilderMock3).directory();will(returnValue(new File("foo")));
					
				}});
			} catch (IOException e) {
				fail(e.getLocalizedMessage());
			}
			retval = proBuilderMock3;
			break;
		default:
			retval = null;
		}
		
		return retval;
	}


	public static class MockProcess extends Process{

		/* (non-Javadoc)
		 * @see java.lang.Process#destroy()
		 */
		@Override
		public void destroy() {}

		/* (non-Javadoc)
		 * @see java.lang.Process#exitValue()
		 */
		@Override
		public int exitValue() {
			return 0;
		}

		/* (non-Javadoc)
		 * @see java.lang.Process#getErrorStream()
		 */
		@Override
		public InputStream getErrorStream() {
			return null;
		}

		/* (non-Javadoc)
		 * @see java.lang.Process#getInputStream()
		 */
		@Override
		public InputStream getInputStream() {
			return null;
		}

		/* (non-Javadoc)
		 * @see java.lang.Process#getOutputStream()
		 */
		@Override
		public OutputStream getOutputStream() {
			return null;
		}

		/* (non-Javadoc)
		 * @see java.lang.Process#waitFor()
		 */
		@Override
		public int waitFor()
				throws InterruptedException {
			return 0;
		}
		
	}
	
	public static class ProcessMock {
	
		public InputStream getInputStream(){
			return null;
		}
		
		public InputStream getErrorStream(){
			return null;
		}
		
		public int waitFor() throws InterruptedException{
			if(_currentTest == testCase.startInterrupt){
				throw new InterruptedException(Exception_Message);
			}
			return 0;
		}
	}

	/**
	 * @return
	 */
	public static junit.framework.Test suite() { 
	    return new JUnit4TestAdapter(CedProcessTest.class); 
	}
}
