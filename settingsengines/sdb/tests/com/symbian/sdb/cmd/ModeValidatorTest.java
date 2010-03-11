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

import static org.junit.Assert.fail;

import java.util.ArrayList;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.validation.InvalidArgumentException;
import org.junit.Before;
import org.junit.Test;

public class ModeValidatorTest {
	ModeValidator validator;

	public static junit.framework.Test suite() { 
	    return new JUnit4TestAdapter(ModeValidatorTest.class); 
	}
	
	@Before
	public void setUp() throws Exception {
		System.setProperty("sdb.contacts.enabled", "true");
		validator = new ModeValidator();
	}

	@Test(expected= InvalidArgumentException.class)
	public void testValidateEmpty() throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		validator.validate(values);
	}

	@Test(expected= InvalidArgumentException.class)
	public void testValidateMoreThanOne() throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		values.add("xxx");
		values.add("yyy");
		validator.validate(values);
	}
	
	@Test
	public void testValidateGenericSqliteMode()  {
		List<String> values = new ArrayList<String>();
		values.add("sqlite");
		try {
			validator.validate(values);
		} catch(InvalidArgumentException ex) {
			fail("shouldn't be an exception here");
		}	
	}
	
	@Test
	public void testValidateGenericDBMSMode()  {
		List<String> values = new ArrayList<String>();
		values.add("dbms");
		try {
			validator.validate(values);
		} catch(InvalidArgumentException ex) {
			fail("shouldn't be an exception here");
		}

	}
	
	@Test
	public void testValidateCed95Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.95";
		validateMode(cedModeParameter);
	}

	/**
	 * @param cedModeParameter
	 * @throws InvalidArgumentException
	 */
	private void validateMode(String cedModeParameter) throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		values.add(cedModeParameter);
		validator.validate(values);
	}
	
	@Test
	public void testValidateCed94Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.94";
		validateMode(cedModeParameter);
	}

	@Test(expected=InvalidArgumentException.class)
	public void testValidateCed944Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.944";
		validateMode(cedModeParameter);
	}

	@Test
	public void testValidateCed93Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.93";
		validateMode(cedModeParameter);
	}

	@Test
	public void testValidateCed92Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.92";
		validateMode(cedModeParameter);
	}

	@Test
	public void testValidateCed91Mode() throws InvalidArgumentException  {
		String cedModeParameter = "ced.91";
		validateMode(cedModeParameter);
	}

	@Test(expected=InvalidArgumentException.class)
	public void testValidateCedXXMode() throws InvalidArgumentException {
		String cedModeParameter = "ced.XX";
		validateMode(cedModeParameter);
	}

	@Test(expected=InvalidArgumentException.class)
	public void testValidateCedMode() throws InvalidArgumentException  {
		String cedModeParameter = "ced";
		validateMode(cedModeParameter);
	}

	@Test
	public void testValidateSqliteContactsMode()  {
		List<String> values = new ArrayList<String>();
		values.add("sqlite.contacts");
		try {
			validator.validate(values);
		} catch(InvalidArgumentException ex) {
			fail("shouldn't be an exception here");
		}
	}
	
	//shoudln't be dbms/sqlite.contacts.schema
	
	@Test
	public void testValidateDbmsContactsMode()  {
		List<String> values = new ArrayList<String>();
		values.add("dbms.contacts");
		try {
			validator.validate(values);
		} catch(InvalidArgumentException ex) {
			fail("shouldn't be an exception here");
		}
	}
	
	@Test(expected= InvalidArgumentException.class)
	public void testFailDbmsContactsMode() throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		values.add("dbms.contacts.9.5");
		validator.validate(values);
	}
	
	@Test(expected= InvalidArgumentException.class)
	public void testFailSqliteContactsMode() throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		values.add("sqlite.contacts.9.5");
		validator.validate(values);
	}
	
	@Test(expected= InvalidArgumentException.class)
	public void testFail() throws InvalidArgumentException {
		List<String> values = new ArrayList<String>();
		values.add("sqlite.xxxx");
		validator.validate(values);
	}
}








