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

package com.symbian.sdb.contacts.dbms;

import java.util.Collections;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.configuration.ConfigurationDbmsTest;
import com.symbian.sdb.contacts.dbms.model.DBMSPhoneNumber;
import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.contacts.model.PhoneNumber;
import com.symbian.sdb.contacts.template.IField;


public class DBMSContactPersisterImplTest {

    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigurationDbmsTest.class); 
    }

    Mockery mockery;
    PropertyData pdMock;
    IField fieldMock;
    DBMSContactPersisterImpl dbmsImpl;
    
	@Before
	public void setUp() throws Exception {
		
		mockery = new Mockery(){{
			setImposteriser(ClassImposteriser.INSTANCE);
		}};
		
		pdMock = mockery.mock(PropertyData.class);
		mockery.checking(new Expectations() {{
	        allowing (pdMock).getParameters(); will(returnValue(Collections.EMPTY_SET));
	    }});
		
		fieldMock = mockery.mock(IField.class);
		
		dbmsImpl = new DBMSContactPersisterImpl();
	}
    
	@Test
	public void testTransformPhoneNumbers() {
		
		String [][] tests = {
				{"*#42# 0401234567 p123", "40000000", "7654321" },
				{"*#42# +358401234567 p123", "48530000", "7654321"},
				{"*61 0401234567", "40160000", "7654321"},
				{"*61 +358401234567", "48530000", "7654321"},
				{"+358401234567 +3", "48530000", "7654321"},
				{"+358401234567 p123", "48530000", "7654321"},
				{"(+358) 1234567", "85300000", "7654321"},
				{"*#42# 0401234567#p123", "0", "0"},
				{"*12345+0401234567", "0", "5432100" },
				{"*+123+456++++++++++", "0", "3210000" },
				{"thisissometextandnotanumber", "0", "0"}
		};
		
		for (int i = 0; i < tests.length; i++) {
			PhoneNumber number =  new PhoneNumber(tests[i][0].getBytes(), fieldMock);
			DBMSPhoneNumber dbSpecificContact = dbmsImpl.transformPhoneNumber(number);
			
			Assert.assertEquals(tests[i][1], dbSpecificContact.getExtendedPhoneMatching() + "");

			Assert.assertEquals(tests[i][2], dbSpecificContact.getPhoneMatching() + "");
		}
	}
}
