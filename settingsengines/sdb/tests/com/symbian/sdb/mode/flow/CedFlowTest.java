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

import java.io.File;
import java.io.IOException;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;
import mockit.Mockit;

import org.apache.commons.cli2.OptionException;
import org.apache.commons.io.FileUtils;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.ced.CEDProcessFactory;
import com.symbian.sdb.mode.flow.ced.CedFlowCompletionException;
import com.symbian.sdb.mode.flow.ced.CedSchema;
import com.symbian.sdb.mode.flow.ced.ICedProcess;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;
import com.symbian.sdb.settings.Settings.SDBPROPS;

public class CedFlowTest extends BaseIntegrationTestCase {

	protected static final File PROCESS_DIR = new File("processDir");
	protected static final String Exception_Message = "test exception";
	private final static String CED_DB = "cccccc00.cre";

	
	@Test(expected=SDBValidationException.class)
	public void testValidateFailNoFiles() throws OptionException, SDBValidationException {
	    try    {
	        CmdLinev2 cmd = new CmdLinev2();
	        cmd.parseArguments(new String[] {});
	        
	        CedFlow cedFlow = new CedFlow();
	        cedFlow.validateOptions(cmd);
	        fail();
	    }
	    catch (SDBValidationException e) {
        }
	}
	
    public void testValidateFailNoCedFiles() throws OptionException, SDBValidationException {
        try {
            CmdLinev2 cmd = new CmdLinev2();
            cmd.parseArguments(new String[] {"tests/config/badSql.sql"});
            
            CedFlow cedFlow = new CedFlow();
            cedFlow.validateOptions(cmd);
            fail();
        }
        catch (SDBValidationException e) {
        }
    }
	
   @Test
   public void testValidatePass() throws OptionException, SDBValidationException {
       CmdLinev2 cmd = new CmdLinev2();
       cmd.parseArguments(new String[] {"tests/config/ced.cfg"});
       
       CedFlow cedFlow = new CedFlow();
       cedFlow.validateOptions(cmd);
   }
   
   //TODO: comment these tests as the desired behaviour is not
   //TODO: correct spelling
   @Test
   public void testValidateUnregnisedFiles() throws OptionException, SDBValidationException {
       CmdLinev2 cmd = new CmdLinev2();
       cmd.parseArguments(new String[] {"tests/config/ced.cfg", "tests/config/badSql.sql"});
       
       CedFlow cedFlow = new CedFlow();
       cedFlow.validateOptions(cmd);
   }
   
   public void testValidateFailMoreThanOne() throws OptionException, SDBValidationException {
       try  {
           CmdLinev2 cmd = new CmdLinev2();
           cmd.parseArguments(new String[] {"tests/config/ced.cfg", "tests/config/ced.cfg"});
           
           CedFlow cedFlow = new CedFlow();
           cedFlow.validateOptions(cmd);
           fail();
       }
       catch (SDBValidationException e) {
       }
   }
   
   //DPDEF130349
   @Test
   public void testOutputLocation_default() throws Exception{
	   System.setProperty("sdb.ced.dbname", CED_DB);
	   CmdLinev2 cmd = new CmdLinev2();
	   cmd.parseArguments(new String[]{});
    
       CedFlow cedFlow = new CedFlow();
       Assert.assertEquals(new File("cccccc00.cre"), cedFlow.getOutputDbFile(cmd));
   }
   
   //DPDEF130349
   @Test
   public void testOutputLocation_overrideProperty() throws Exception{
	   System.setProperty("sdb.ced.dbname", "foo.db");
	   CmdLinev2 cmd = new CmdLinev2();
	   cmd.parseArguments(new String[]{});
    
       CedFlow cedFlow = new CedFlow();
       Assert.assertEquals(new File("foo.db"), cedFlow.getOutputDbFile(cmd));
   }
   
   //DPDEF130349
   @Test
   public void testOutputLocation_overrideOption() throws Exception{
	   CmdLinev2 cmd = new CmdLinev2();
	   cmd.parseArguments(new String[]{"-o", "foo2.db"});
    
       CedFlow cedFlow = new CedFlow();
       Assert.assertEquals(new File("foo2.db"), cedFlow.getOutputDbFile(cmd));
    }
  
   //DPDEF130352
   @Test
   public void testErroredOutputDbExists() throws Exception{
	  
	   Mockit.redefineMethods(CEDProcessFactory.class, CedProcessFactoryMock2.class);
	   System.setProperty(SDBPROPS.ced_location.toString(), "tests/config/cedflow");
	   
	   CmdLinev2 cmd = new CmdLinev2();
	   cmd.parseArguments(new String[]{"-m", "ced.95", "-o", "foo2.db", "tests/config/cedflow/ced95err.cfg"});
	   
	   File cedOutputFile = new File("foo2_err.db");
	   cedOutputFile.delete();
       
	   CedFlow cedFlow = new CedFlow();
       try {
    	   cedFlow.validateOptions(cmd);
    	   cedFlow.start(cmd);
       }
       catch(CedFlowCompletionException e) {
    	   Assert.assertEquals("The test exception was not the exception caught", 99, e.getReturnCode());
    	   Assert.assertTrue(cedOutputFile.exists());
       }
       cedOutputFile.delete();
       Mockit.restoreAllOriginalDefinitions();
    }
   
   public static class CedProcessFactoryMock2 {
	   
	   public static ICedProcess getProcess(CedSchema schema){
			return new ICedProcess(){

				public void addOptions(String... options) {
					// TODO Auto-generated method stub
					
				}

				public void start() throws SdbFlowException {
					Boolean isWindows = System.getProperty("os.name").startsWith("Windows");
					String destinationPath = "tests/config/cedflow/cccccc00.cre";
					try {
						FileUtils.copyFile(new File("tests/config/cedflow/cccccc00.bk"), new File(destinationPath));
					} catch (IOException e) {
						Assert.fail("Could not create cre for test.");
					}
					throw new CedFlowCompletionException(99);
				}
				
			};
		}
   }
	/**
	 * @return
	 */
	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(CedFlowTest.class); 
	}
	
}
