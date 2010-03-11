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

package com.symbian.sdb.contacts.model;

import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.Test;

import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.contacts.template.IField;

/**
 * @author jamesclark
 *
 */
public class ContactFieldTest {
	
	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(ContactFieldTest.class);
	}

	private final static String THE_ID = "uintAN_ID";
	
	private final static String MATCHING_ID_tint = "tintAN_ID";
	
	private final static String MATCHING_ID_value = "AN_ID";
	
	private final static String NOT_A_MATCH = "NOT_A_MATCH";
	
	/**
	 * Test method for {@link com.symbian.sdb.contacts.model.ContactField#doesImplementID(java.lang.String)}.
	 */
	@Test
	public void testDoesImplementID_validUint() throws Exception{
		
		Mockery mockery = new Mockery(){{
				setImposteriser(ClassImposteriser.INSTANCE);
		}};
		final PropertyData pdMock = mockery.mock(PropertyData.class);
		mockery.checking(new Expectations() {{
            allowing (pdMock).getParameters(); will(returnValue(Collections.EMPTY_SET));
        }});
		
		final IField fieldMock = mockery.mock(IField.class);
		mockery.checking(new Expectations() {{
            allowing (fieldMock).getFieldType(); will(returnValue(MATCHING_ID_tint));
        }});
		
		ContactField field = new ContactField("Value".getBytes(), fieldMock);
		
		Assert.assertTrue(field.doesImplementID(MATCHING_ID_tint));
	}

	/**
	 * Test method for {@link com.symbian.sdb.contacts.model.ContactField#doesImplementID(java.lang.String)}.
	 */
	@Test
	public void testDoesImplementID_validTint() throws Exception{
		Mockery mockery = new Mockery(){{
				setImposteriser(ClassImposteriser.INSTANCE);
		}};
		final PropertyData pdMock = mockery.mock(PropertyData.class);
		mockery.checking(new Expectations() {{
            allowing (pdMock).getParameters(); will(returnValue(Collections.EMPTY_SET));
        }});
		
		final IField fieldMock = mockery.mock(IField.class);
		mockery.checking(new Expectations() {{
            allowing (fieldMock).getFieldType(); will(returnValue(MATCHING_ID_value));
        }});
		
		ContactField field = new ContactField("Value".getBytes(), fieldMock);
		
		Assert.assertTrue(field.doesImplementID(MATCHING_ID_value));
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.contacts.model.ContactField#doesImplementID(java.lang.String)}.
	 */
	@Test
	public void testDoesImplementID_validProperty() throws Exception{
		Mockery mockery = new Mockery(){{
				setImposteriser(ClassImposteriser.INSTANCE);
		}};
		final PropertyData pdMock = mockery.mock(PropertyData.class);
		mockery.checking(new Expectations() {{
            allowing (pdMock).getParameters(); will(returnValue(Collections.EMPTY_LIST));
        }});
		
		final Set<String> properties = new LinkedHashSet<String>();
		properties.add(NOT_A_MATCH);
		properties.add(MATCHING_ID_tint);
		final IField fieldMock = mockery.mock(IField.class);
		mockery.checking(new Expectations() {{
            allowing (fieldMock).getFieldType(); will(returnValue(NOT_A_MATCH));
            allowing (fieldMock).getProperties(); will(returnValue(properties));
        }});
		
		ContactField field = new ContactField("Value".getBytes(), fieldMock);
		
		Assert.assertTrue(field.doesImplementID(MATCHING_ID_tint));
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.contacts.model.ContactField#doesImplementID(java.lang.String)}.
	 */
	@Test
	public void testDoesImplementID_invalid() throws Exception{
		Mockery mockery = new Mockery(){{
				setImposteriser(ClassImposteriser.INSTANCE);
		}};
		final PropertyData pdMock = mockery.mock(PropertyData.class);
		mockery.checking(new Expectations() {{
            allowing (pdMock).getParameters(); will(returnValue(Collections.EMPTY_LIST));
        }});
		
		final IField fieldMock = mockery.mock(IField.class);
		mockery.checking(new Expectations() {{
            allowing (fieldMock).getFieldType(); will(returnValue(NOT_A_MATCH));
            allowing (fieldMock).getProperties(); will(returnValue(Collections.EMPTY_SET));
        }});
		
		ContactField field = new ContactField("Value".getBytes(), fieldMock);
		
		Assert.assertFalse(field.doesImplementID(THE_ID));
	}
	
}
