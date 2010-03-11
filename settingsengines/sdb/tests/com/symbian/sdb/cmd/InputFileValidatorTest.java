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

import java.io.File;
import java.util.LinkedList;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.validation.InvalidArgumentException;
import org.junit.After;
import org.junit.Assert;
import org.junit.Test;

public class InputFileValidatorTest {
	
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(InputFileValidatorTest.class); 
    }
    
    List<Object> values = new LinkedList<Object>();
    
    @After
    public void tearDown() {
        values.clear();
    }
    
    @Test
    public void testValidate() throws InvalidArgumentException {
    	InputFileValidator validator = InputFileValidator.getInstance();
        validator.validate(values);
    }
    
    @Test
    public void testValidate1() throws InvalidArgumentException {
    	InputFileValidator validator = InputFileValidator.getInstanceForFilesWhichMustExist();
        values.add("tests/config/badSql.sql");
        validator.validate(values);
        
        Assert.assertTrue(values.size() == 1);
        Assert.assertTrue(allAreFiles(values));
        Assert.assertTrue(containsFileWithName(values,"badSql.sql"));
    }

    @Test
    public void testValidate2() throws InvalidArgumentException {
    	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
        values.add("testdata/FileValidatorTest");
        validator.validate(values);
        
        Assert.assertTrue(values.size() == 2);
        Assert.assertTrue(values.get(0) instanceof File);
    }
    
    @Test
    public void testValidate2_2() {
   	 	InputFileValidator validator = InputFileValidator.getInstanceForFilesWhichMustExist();
    	values.add("doesnotexist.txt");

		try {
			validator.validate(values);
		} catch (InvalidArgumentException e) {
			Assert.assertTrue(e.getMessage().equals("doesnotexist.txt does not exist"));
		}
    }


    @Test
    public void testValidate3() throws InvalidArgumentException {
   	 	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
        values.add("tests/config/*.sql");
        validator.validate(values);
        
        Assert.assertTrue(values.size() == 5);
        Assert.assertTrue(allAreFiles(values));
        Assert.assertTrue(containsFileWithName(values,"badSql.sql"));
    }
    
	private boolean allAreFiles(List<Object> files) {
		for (Object file : files) {
			if (!(file instanceof File))	{
				return false;
			}
		}
		return true;
	}

	private boolean containsFileWithName(List<Object> files, String fileName) {
		for (Object file : files) {
			if (((File)file).getName().equals(fileName))	{
				return true;
			}
		}
		return false;
	}

	@Test
    public void testValidate4() throws InvalidArgumentException {
   	 	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
    	values.add("tests/config/XML/nextVersion?.xml");
        validator.validate(values);
        
        Assert.assertTrue(values.size() == 3);
        Assert.assertTrue(allAreFiles(values));
        Assert.assertTrue(containsFileWithName(values, "nextVersion.xml"));
    }
    
    @Test(expected=InvalidCmdArgumentException.class)
    public void testValidate5() throws InvalidArgumentException {
    	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
        values.add("tests/sdb/config22/");
        validator.validate(values);
    }
    
    @Test(expected=InvalidCmdArgumentException.class)
    public void testValidate6() throws InvalidArgumentException {
   	 	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
    	values.add("tests/sdb/config22/next*Version?.xml");
        validator.validate(values);
    }
    
    @Test
    public void testValidate7() throws InvalidArgumentException {
   	 	InputFileValidator validator = InputFileValidator.getInstanceForPathsWithWildcardSupport();
    	values.add("tests/sdb/config22/next*Version?.xml");

		try {
			validator.validate(values);
		} catch (InvalidCmdArgumentException e) {
			Assert.assertTrue(e.getMessage().contains("tests/sdb/config22/next*Version?.xml"));
		}
    }
    
}
