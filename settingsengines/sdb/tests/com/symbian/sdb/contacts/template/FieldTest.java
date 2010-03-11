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

package com.symbian.sdb.contacts.template;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.contacts.dbms.model.TemplateHintField;

public class FieldTest {
	
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(FieldTest.class); 
    }
    
	Field field;

    Mockery mapperContext = new Mockery();
    IFieldMapping map;

	@Before
	public void setUp() throws Exception {
		map = mapperContext.mock(IFieldMapping.class);
        
		mapperContext.checking(new Expectations() {{
			atLeast(1).of  (map).getLabel(with(same("STRING_r_cntui_new_field_defns1"))); will(returnValue("label"));
            atLeast(1).of (map).getFieldType(with(same("KUidContactFieldAssistantValue"))); will(returnValue(0));
            atLeast(1).of  (map).getValueFromvCardMapping(with(same("KIntContactFieldVCardMapURL"))); will(returnValue(0));
        }});

		field = new Field();
		field.setMapping(map);
	}

	@Test
	public void testGetStorageType() {
		field.setStorageType("10");
		Assert.assertEquals(10, field.getStorageType());
	}

	@Test
	public void testIsBinary() {
		field.setStorageType(0);
		Assert.assertFalse(field.isBinary());
		field.setStorageType(1);
		Assert.assertTrue(field.isBinary());
		field.setStorageType(2);
		Assert.assertFalse(field.isBinary());
		field.setStorageType(3);
		Assert.assertTrue(field.isBinary());
	}
	
	@Test
	public void testIsText() {
		field.setStorageType(0);
		Assert.assertTrue(field.isText());
		field.setStorageType(1);
		Assert.assertFalse(field.isText());
		field.setStorageType(2);
		Assert.assertFalse(field.isText());
		field.setStorageType(3);
		Assert.assertFalse(field.isText());
	}
	
	@Test
	public void testIsAgent() {
		field.setStorageType(0);
		Assert.assertFalse(field.isAgent());
		field.setStorageType(1);
		Assert.assertFalse(field.isAgent());
		field.setStorageType(2);
		Assert.assertTrue(field.isAgent());
		field.setStorageType(3);
		Assert.assertFalse(field.isAgent());
	}
	
	@Test
	public void testFieldType() throws MappingMissingException {
		field.setFieldType("KUidContactFieldAssistantValue");
		Assert.assertEquals("KUidContactFieldAssistantValue", field.getFieldType());
		
		Assert.assertEquals(0, field.getFieldTypeValue());
	}

	@Test
	public void testVCardMapping() throws MappingMissingException {
		field.setVCardMapping("KIntContactFieldVCardMapURL");
		Assert.assertEquals("KIntContactFieldVCardMapURL", field.getVCardMapping());
		
		Assert.assertEquals(0, field.getVCardMappingValue());
	}

	@Test
	public void testGetCategory() {
		field.setCategory("10");
		Assert.assertEquals((byte)10, field.getCategory());
	}

	@Test
	public void testFieldName()throws MappingMissingException  {
		field.setFieldName("STRING_r_cntui_new_field_defns1");
		Assert.assertEquals("STRING_r_cntui_new_field_defns1", field.getFieldName());
		
		Assert.assertEquals("label", field.getFieldNameValue());
	}

	@Test
	public void testAddFlag() {
		Flag flag = new Flag("one", 1);
		Flag flag2 = new Flag("two", 2);
		field.addFlag(flag);
		
		Assert.assertEquals(1, field.getFlags().size());
		Assert.assertEquals(flag, field.getFlags().get(0));
		
		field.addFlag(flag2);
		Assert.assertEquals(2, field.getFlags().size());
		Assert.assertEquals(flag2, field.getFlags().get(1));
	}

	@Test
	public void testAddProperty() {
		field.addProperty("property 1");
		Assert.assertEquals(1, field.getProperties().size());
		
		field.addProperty("property 2");
		Assert.assertEquals(2, field.getProperties().size());

		
		Assert.assertTrue(field.getProperties().contains("property 1"));
		Assert.assertTrue(field.getProperties().contains("property 2"));
	}
	
	@Test
	public void testGetPropertiesValue() throws MappingMissingException {
		field.addProperty("KIntContactFieldVCardMapURL");
		Assert.assertEquals(1, field.getProperties().size());
		Assert.assertEquals(0, 
				field.getPropertiesValue().iterator().next());
	}


	@Test
	public void testCompareTo() {
		Field field = new Field();
		Field field2 = new Field();
		
		field.setIndex(0);
		field2.setIndex(2);
		
		Assert.assertTrue(field.compareTo(field2) < 0);
		Assert.assertTrue(field2.compareTo(field) > 0);
	}


	@Test
	public void testGetIndex() {
		field.setIndex(0);
		Assert.assertEquals(0, field.getIndex());
	}
	
	@Test
	public void testGetFieldHint() {
		field.setFieldType("KUidContactFieldPhoneNumberValue");
		TemplateHintField hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(2, hintField.getValue());
		
		field.setFieldType("KUidContactFieldMsgValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(4, hintField.getValue());
		
		field.setFieldType("KUidContactFieldCompanyNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(8, hintField.getValue());
		
		field.setFieldType("KUidContactFieldFamilyNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(16, hintField.getValue());

		field.setFieldType("KUidContactFieldGivenNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(32, hintField.getValue());
		
		field.setFieldType("KUidContactFieldAddressValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(64, hintField.getValue());
		
		field.setFieldType("KUidContactFieldAdditionalNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(128, hintField.getValue());
	
		field.setFieldType("KUidContactFieldSuffixNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(256, hintField.getValue());	
		
		field.setFieldType("KUidContactFieldPrefixNameValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(512, hintField.getValue());
		
		field.setFieldType("KUidContactFieldStorageInlineValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(1024, hintField.getValue());	
		
		field.setFieldType("KUidContactFieldCompanyNamePronunciationValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(2056, hintField.getValue());
		
		field.setFieldType("KUidContactFieldFamilyNamePronunciationValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(2064, hintField.getValue());	
		
		field.setFieldType("KUidContactFieldGivenNamePronunciationValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(2080,  hintField.getValue());	

		field.setFieldType("KUidContactFieldEMailValue");
		hintField = new TemplateHintField(field.getFieldType());
		Assert.assertEquals(16384, hintField.getValue());		
	}

	private Field createField() {
		Field field = new Field();
		field.setIndex(1);
		field.setVCardMapping("vcard");
		field.setCategory((byte)0);
		field.setFieldName("field_name");
		field.setStorageType(0);
		field.setFieldType("field_type");
		return field;
	}
	
	@Test
	public void testSameProperties() {
		Field field1 = createField();
		Field field2 = createField();
		
		Assert.assertTrue("Two empty fields should be identified as the same.", field1.isSame(field2));
		
		//compare properties
		field2.addProperty("property1");
		field2.addProperty("property2");
		field2.addProperty("property3");
		
		Assert.assertFalse("One empty field should not be identified as the same as one with 3 properties.", field1.isSame(field2));
		
		field1.addProperty("property1");
		field1.addProperty("property3");
		field1.addProperty("property2");
		Assert.assertTrue("Two fields with the same 3 properties but different order should be identified as the same.", field1.isSame(field2));
		
		field1 = createField();
		field1.addProperty("property1");
		field1.addProperty("property1");
		field1.addProperty("property2");
		Assert.assertFalse("Two fields with the same number of properties but one having a subset " +
				"of the other with one repeated should be identified as different.", field1.isSame(field2));
	}
	
	@Test
	public void testSame() {
		Field field1 = createField();
		Field field2 = createField();

		Assert.assertTrue("Two empty fields should be identified as the same.", field1.isSame(field2));

		//compare storage type
		field2.setStorageType(1);
		Assert.assertFalse("Two fields with different storage type should be identified as different.", field1.isSame(field2));
	
		//compare category
		field2 = createField();
		field2.setCategory((byte)1);
		Assert.assertFalse("Two fields with different category should be identified as different.", field1.isSame(field2));
		
		//compare field name
		field2 = createField();
		field2.setFieldName("new field name");
		Assert.assertFalse("Two fields with different field name should be identified as different.", field1.isSame(field2));
		
		//compare field type
		field2 = createField();
		field2.setFieldType("new field type");
		Assert.assertFalse("Two fields with different field type should be identified as different.", field1.isSame(field2));
		
		//compare properties
		field2 = createField();
		field2.addProperty("new property");
		Assert.assertFalse("Two fields with different properties should be identified as different.", field1.isSame(field2));
		
		field1.addProperty("new property");
		Assert.assertTrue("Two fields with same properties should be identified as the same.", field1.isSame(field2));

		//compare flags
		field2 = createField();
		field1 = createField();
		
		field2.addFlag(new Flag("flag uid", 1));
		Assert.assertFalse("Two fields with different flags should be identified as different.", field1.isSame(field2));
		
		field1.addFlag(new Flag("flag uid", 1));
		Assert.assertTrue("Two fields with same flags should be identified as the same.", field1.isSame(field2));
		
		
		//compare flags - synchronized skipped
		field2 = createField();
		field1 = createField();
		
		field2.addFlag(new Flag("EContactFieldFlagSynchronize", 1));
		Assert.assertTrue("Two fields with only synchronized flag difference should be identified as the same.", field1.isSame(field2));

	}
	
	
}
