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
// ContactAttributesContainerTest.java
//
package com.symbian.sdb.contacts.sqlite.helper;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.contacts.sqlite.model.ContactFieldAttribute;
import com.symbian.sdb.contacts.sqlite.model.StorageType;

public class ContactAttributesContainerTest {
	ContactFieldAttributes attributes;
	
	//atributes sets - category
	private final int attributesCategoryNone  = 0x00000000;
	private final int attributesCategoryHome  = 0x00000010;
	private final int attributesCategoryWork  = 0x00000020;
	private final int attributesCategoryOther = 0x00000030;
	private final int attributesUserMaskSet   = 0x000000F0;
	
	//atributes sets - storage
	private final int attributesStorageText   = 0x00000000;
	private final int attributesStorageStore  = 0x00100000;
	private final int attributesStorageAgent  = 0x00200000;
	private final int attributesStorageDate   = 0x00300000;

	@Before
	public void setUp() throws Exception {
		attributes = new ContactFieldAttributes();
	}

	@Test
	public void testResetAttributes() {
		attributes = new ContactFieldAttributes(attributesStorageDate);
		Assert.assertEquals(attributesStorageDate, attributes.getValue());
		attributes.resetAttributes();
		Assert.assertEquals(0, attributes.getValue());
	}
	
	@Test
	public void testGetValue() {
		attributes = new ContactFieldAttributes(attributesStorageDate);
		Assert.assertEquals(attributesStorageDate, attributes.getValue());
	}

	@Test
	public void testStorageType() {
		attributes = new ContactFieldAttributes(attributesStorageText);
		Assert.assertEquals(StorageType.TEXT.getValue(), attributes.getFieldStorageType());
		
		attributes = new ContactFieldAttributes(attributesStorageStore);
		Assert.assertEquals(StorageType.STORE.getValue(), attributes.getFieldStorageType());
	
		attributes = new ContactFieldAttributes(attributesStorageAgent);
		Assert.assertEquals(StorageType.AGENT.getValue(), attributes.getFieldStorageType());
		
		attributes = new ContactFieldAttributes(attributesStorageDate);
		Assert.assertEquals(StorageType.DATE_TIME.getValue(), attributes.getFieldStorageType());
		
		attributes = new ContactFieldAttributes();
		attributes.setStorageType(StorageType.TEXT.getValue());
		Assert.assertEquals(attributesStorageText, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setStorageType(StorageType.STORE.getValue());
		Assert.assertEquals(attributesStorageStore, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setStorageType(StorageType.AGENT.getValue());
		Assert.assertEquals(attributesStorageAgent, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setStorageType(StorageType.DATE_TIME.getValue());
		Assert.assertEquals(attributesStorageDate, attributes.getValue());
	}

	@Test
	public void testCategory() {
		attributes = new ContactFieldAttributes(attributesCategoryNone);
		Assert.assertEquals(0, attributes.getCategory());
		
		attributes = new ContactFieldAttributes(attributesCategoryHome);
		Assert.assertEquals(1, attributes.getCategory());
	
		attributes = new ContactFieldAttributes(attributesCategoryWork);
		Assert.assertEquals(2, attributes.getCategory());
		
		attributes = new ContactFieldAttributes(attributesCategoryOther);
		Assert.assertEquals(3, attributes.getCategory());
		
		attributes = new ContactFieldAttributes();
		attributes.setCategory((byte)0);
		Assert.assertEquals(attributesCategoryNone, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setCategory((byte)1);
		Assert.assertEquals(attributesCategoryHome, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setCategory((byte)2);
		Assert.assertEquals(attributesCategoryWork, attributes.getValue());
		
		attributes = new ContactFieldAttributes();
		attributes.setCategory((byte)3);
		Assert.assertEquals(attributesCategoryOther, attributes.getValue());
		
		attributes = new ContactFieldAttributes(attributesUserMaskSet);
		attributes.setCategory((byte)0);
		Assert.assertEquals(attributesCategoryNone, attributes.getValue());
		
		attributes = new ContactFieldAttributes(attributesUserMaskSet);
		attributes.setCategory((byte)1);
		Assert.assertEquals(attributesCategoryHome, attributes.getValue());
		
		attributes = new ContactFieldAttributes(attributesUserMaskSet);
		attributes.setCategory((byte)2);
		Assert.assertEquals(attributesCategoryWork, attributes.getValue());
		
		attributes = new ContactFieldAttributes(attributesUserMaskSet);
		attributes.setCategory((byte)3);
		Assert.assertEquals(attributesCategoryOther, attributes.getValue());
	}

	@Test
	public void testAddAttributeContactFieldAttribute() {
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DELETED);
		Assert.assertTrue(attributes.isDeleted());
		
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DISABLED);
		Assert.assertTrue(attributes.isDeleted());
		Assert.assertTrue(attributes.isDisabled());
		
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_HIDDEN);
		Assert.assertTrue(attributes.isDeleted());
		Assert.assertTrue(attributes.isDisabled());
		Assert.assertTrue(attributes.isHidden());
		
		attributes = new ContactFieldAttributes();
		
	}

	
	@Test
	public void testAddAttributeInteger() {
		//ext attribute mask, should be ignored
		attributes.addAttribute(0x0001B000);
		Assert.assertEquals(0x0, attributes.getValue());
		
		//storage mask, should be ignored
		attributes.addAttribute(attributesStorageStore);
		Assert.assertEquals(0x0, attributes.getValue());
		
		//should set the value
		attributes.addAttribute(0xF0000FFF);
		Assert.assertEquals(0xF0000FFF, attributes.getValue());
	}

	@Test
	public void testExtendedAttributes() {
		//filt 1
		attributes.addExtendedAttributes(0x008);
		Assert.assertEquals(0x00008000, attributes.getValue());
		
		//filt 2 
		attributes.addExtendedAttributes(0x010);
		Assert.assertEquals(0x00018000, attributes.getValue());
		
		//speed dial
		attributes.addExtendedAttributes(0x002);
		Assert.assertEquals(0x0001A000, attributes.getValue());
	
		//private
		attributes.addExtendedAttributes(0x001);
		Assert.assertEquals(0x0001B000, attributes.getValue());
	}

	@Test
	public void testHasOverridenLabel() {
		Assert.assertFalse(attributes.hasOverridenLabel());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_OVERIDELABEL);
		Assert.assertTrue(attributes.hasOverridenLabel());
	}

	@Test
	public void testUsesTemplateData() {
		Assert.assertFalse(attributes.usesTemplateData());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USETEMPLATEDATA);
		Assert.assertTrue(attributes.usesTemplateData());
	}
	
	@Test
	public void testIsHidden() {
		Assert.assertFalse(attributes.isHidden());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_HIDDEN);
		Assert.assertTrue(attributes.isHidden());
	}

	@Test
	public void testIsSyncable() {
		Assert.assertFalse(attributes.isSyncable());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_SYNCH);
		Assert.assertTrue(attributes.isSyncable());
	}

	@Test
	public void testIsDisabled() {
		Assert.assertFalse(attributes.isDisabled());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DISABLED);
		Assert.assertTrue(attributes.isDisabled());
	}

	@Test
	public void testHasUserMask() {
		Assert.assertFalse(attributes.hasUserMask());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERMASKED);
		Assert.assertTrue(attributes.hasUserMask());
	}

	@Test
	public void testHasTemplateMask() {
		Assert.assertFalse(attributes.hasTemplateMask());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_TEMPLATEMASK);
		Assert.assertTrue(attributes.hasTemplateMask());
	}

	@Test
	public void testIsUserAddedField() {
		Assert.assertFalse(attributes.isUserAddedField());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERADDEDFIELD);
		Assert.assertTrue(attributes.isUserAddedField());
	}

	@Test
	public void testIsTemplate() {
		Assert.assertFalse(attributes.isTemplate());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_TEMPLATE);
		Assert.assertTrue(attributes.isTemplate());
	}

	@Test
	public void testLabelUnspecified() {
		Assert.assertFalse(attributes.labelUnspecified());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_LABELUNSPECIFIED);
		Assert.assertTrue(attributes.labelUnspecified());
	}

	@Test
	public void testIsDeleted() {
		Assert.assertFalse(attributes.isDeleted());
		attributes.addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DELETED);
		Assert.assertTrue(attributes.isDeleted());
	}

}
