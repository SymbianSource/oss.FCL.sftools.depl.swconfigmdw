// Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
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
// FieldHeaderTest.java
//

package com.symbian.sdb.contacts.sqlite.model;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.model.TemplateHint;

public class FieldHeaderTest {
	
	FieldHeader fieldHeader;

	@Before
	public void setUp() throws Exception {
		fieldHeader = new FieldHeader();
	}

	@Test
	public void testSetAttributes() {
		fieldHeader.setAttributes(0x00100000);
		Assert.assertEquals(0x00100000, fieldHeader.getAttributesContainer().getValue());	
	}

	@Test
	public void testFieldLabel() {
		ContactFieldLabel label = new ContactFieldLabel();
		label.setLabel("new label");
		label.setLength(9);
		
		fieldHeader.setFieldLabel(label);
		Assert.assertEquals(label, fieldHeader.getFieldLabel());
		Assert.assertEquals(label.getLength(), fieldHeader.getFieldLabel().getLength());
		Assert.assertEquals(label.getLabel(), fieldHeader.getFieldLabel().getLabel());
	}

	@Test
	public void testStreamId() {
		fieldHeader.setStreamId(1);
		Assert.assertEquals(1, fieldHeader.getStreamId());
	}

	@Test
	public void testContactFieldGuid() {
		fieldHeader.setContactFieldGuid(1001);
		Assert.assertEquals(1001, fieldHeader.getContactFieldGuid());
	}

	@Test
	public void testHint() {
		fieldHeader.setHint(0x82000000);
		Assert.assertEquals(0x82000000, fieldHeader.getHint());

		Assert.assertTrue(fieldHeader.hasVCardMapping());
		Assert.assertEquals(2, fieldHeader.getAdditionalFieldCount());
		Assert.assertEquals(0x0, fieldHeader.getFieldHintValue());
	}

	@Test
	public void testSetHint() {
		fieldHeader.setAdditionalFieldCount(2);
		Assert.assertEquals(0x02000000, fieldHeader.getHint());
		
		fieldHeader.setFieldVcardMapping(2);
		Assert.assertEquals(0x82000000, fieldHeader.getHint());
		
		fieldHeader.setHintValue(TemplateHint.KIntContactHintIsAddress.getValue());
		Assert.assertEquals(0x82000040, fieldHeader.getHint());
	}

	@Test
	public void testFieldHintValue() {
		fieldHeader.setHintValue(TemplateHint.KIntContactHintIsAddress.getValue());
		Assert.assertEquals(0x40, fieldHeader.getFieldHintValue());
	}

	@Test
	public void testFieldVcardMapping() {
		Assert.assertFalse(fieldHeader.hasVCardMapping());
		
		fieldHeader.setFieldVcardMapping(0x1000401E);
		Assert.assertEquals(0x1000401E, fieldHeader.getFieldVcardMapping());
		Assert.assertTrue(fieldHeader.hasVCardMapping());
	}


	@Test
	public void testtAdditionalFieldCount() {
		fieldHeader.setAdditionalFieldCount(5);
		Assert.assertEquals(5, fieldHeader.getAdditionalFieldCount());
	}
	
	@Test
	public void testFieldAdditionalUIDValues() {
		int[] uids = new int[3];
		uids[0] = 0x100039DB;
		uids[1] = 0x100039DD;
		uids[2] = 0x100039DE;
		fieldHeader.setFieldAdditionalUIDValues(uids);
		
		Assert.assertEquals(uids, fieldHeader.getFieldAdditionalUIDValues());
	}

	@Test
	public void testFieldId() {
		fieldHeader.setFieldId(10);
		Assert.assertEquals(10, fieldHeader.getFieldId());
	}



}
