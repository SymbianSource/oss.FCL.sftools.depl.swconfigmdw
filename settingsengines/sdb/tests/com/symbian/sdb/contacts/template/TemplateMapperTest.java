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

import java.util.HashMap;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.junit.Before;
import org.junit.Test;
import org.w3c.dom.Document;

import com.symbian.sdb.exception.SDBExecutionException;

public class TemplateMapperTest {
	TemplateMapper mapper;
	
	public static junit.framework.Test suite() { 
		return new JUnit4TestAdapter(TemplateMapperTest.class); 
	}
	
	@Before
	public void setUp() throws Exception {
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		System.setProperty("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml");
		mapper = TemplateMapper.getInstance();
	}

	@Test
	public void testGetDocument() throws SDBExecutionException {
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		Document document = mapper.getDocument();
		Assert.assertNotNull(document);
		
		System.setProperty("sdb.contacts.configuration", "config/notExisting.xml");
		Document doc = mapper.getDocument();
		Assert.assertEquals(document, doc);
	}

	@Test
	public void testGetMapping() throws SDBExecutionException, MappingMissingException {
		HashMap<String, String> map1 = mapper.getMapping(ContactMapTypes.category);
	/*	<item name="EContactCategoryNone" value="0" /> 
		<item name="EContactCategoryHome" value="1" /> 
		<item name="EContactCategoryWork" value="2" /> 
		<item name="EContactCategoryOther" value="3" /> */
		Assert.assertTrue(map1.containsKey("EContactCategoryNone"));
		Assert.assertTrue(map1.containsKey("EContactCategoryHome"));
		Assert.assertTrue(map1.containsKey("EContactCategoryWork"));
		Assert.assertTrue(map1.containsKey("EContactCategoryOther"));
		
		Assert.assertEquals("0", map1.get("EContactCategoryNone"));
		Assert.assertEquals("1", map1.get("EContactCategoryHome"));
		Assert.assertEquals("2", map1.get("EContactCategoryWork"));
		Assert.assertEquals("3", map1.get("EContactCategoryOther"));
		
		HashMap<String, String> map2 = mapper.getMapping(ContactMapTypes.storage);
		/*		<item name="KStorageTypeText" value="0" /> 
		<item name="KStorageTypeStore" value="1" /> 
		<item name="KStorageTypeContactItemId" value="2" /> 
		<item name="KStorageTypeDateTime" value="3" /> */
		
		Assert.assertTrue(map2.containsKey("KStorageTypeText"));
		Assert.assertTrue(map2.containsKey("KStorageTypeStore"));
		Assert.assertTrue(map2.containsKey("KStorageTypeContactItemId"));
		Assert.assertTrue(map2.containsKey("KStorageTypeDateTime"));
		
		Assert.assertEquals("0", map2.get("KStorageTypeText"));
		Assert.assertEquals("1", map2.get("KStorageTypeStore"));
		Assert.assertEquals("2", map2.get("KStorageTypeContactItemId"));
		Assert.assertEquals("3", map2.get("KStorageTypeDateTime"));
		
		map2 = mapper.getMapping(ContactMapTypes.flags);
		/*<item name="EContactFieldFlagHidden" value="0x001" /> 
		<item name="EContactFieldFlagReadOnly" value="0x002" /> 
		<item name="EContactFieldFlagSynchronize" value="0x004" /> 
		<item name="EContactFieldFlagDisabled" value="0x008" /> 
		<item name="EContactFieldFlagFilterable" value="0x010" /> 
		<item name="EContactFieldFlagFilterable1" value="0x020" /> 
		<item name="EContactFieldFlagFilterable2" value="0x040" /> 
		<item name="EContactFieldFlagFilterable3" value="0x080" /> 
		<item name="EContactFieldFlagFilterable4" value="0x100" /> */
		
		Assert.assertTrue(map2.containsKey("EContactFieldFlagHidden"));
		Assert.assertTrue(map2.containsKey("EContactFieldFlagDisabled"));
		Assert.assertTrue(map2.containsKey("EContactFieldFlagFilterable3"));
		Assert.assertTrue(map2.containsKey("EContactFieldFlagFilterable1"));
		
		Assert.assertEquals("0x001", map2.get("EContactFieldFlagHidden"));
		Assert.assertEquals("0x020", map2.get("EContactFieldFlagFilterable1"));
		Assert.assertEquals("0x008", map2.get("EContactFieldFlagDisabled"));
		Assert.assertEquals("0x004", map2.get("EContactFieldFlagSynchronize"));
		
	}

	@Test
	public void testGetFieldType() throws SDBExecutionException, MappingMissingException {
		Integer value = mapper.getFieldType("KUidContactFieldAddressValue");
		Assert.assertEquals("1000130C", Integer.toHexString(value).toUpperCase());

		
		//<item name="KUidContactFieldICCPhonebookValue" value="0x101F7583"/>
		value = mapper.getFieldType("KUidContactFieldICCPhonebookValue");
		Assert.assertEquals("101F7583", Integer.toHexString(value).toUpperCase());
	}
	
	@Test(expected=MappingMissingException.class)
	public void test() throws SDBExecutionException, MappingMissingException {
		Integer value = mapper.getFieldType("nonexistingfield");
	}
	
	@Test
	public void testGetMappingFromvCard() throws SDBExecutionException, MappingMissingException  {
		//<item name="KIntContactFieldVCardMapADR" value="0x1000401D" token="KVersitTokenADR" vCard="ADR"/>
		String mapping = mapper.getMappingFromvCard("ADR", 2);
		Assert.assertEquals("KIntContactFieldVCardMapADR", mapping);
	
		//	<item name="KIntContactFieldVCardMapEMAILINTERNET" value="0x10004020" token="KVersitTokenEMAIL" vCard="EMAIL"/>
		mapping = mapper.getMappingFromvCard("EMAIL", 0);
		Assert.assertEquals("KIntContactFieldVCardMapEMAILINTERNET", mapping);
	}

	@Test
	public void getValueFromvCardMapping() throws SDBExecutionException, MappingMissingException  {
		Integer result = mapper.getValueFromvCardMapping("KIntContactFieldVCardMapGEO");
		Assert.assertEquals("10004021", Integer.toHexString(result).toUpperCase());
		
		result = mapper.getValueFromvCardMapping("KIntContactFieldVCardMapPGP");
		Assert.assertEquals("1000654F", Integer.toHexString(result).toUpperCase());
		
		result = mapper.getValueFromvCardMapping("KIntContactFieldVCardMapAVI");
		Assert.assertEquals("10005DCF", Integer.toHexString(result).toUpperCase());
	}
	
	
	@Test
	public void getLabel() throws SDBExecutionException, MappingMissingException  {
		String label = mapper.getLabel("STRING_r_cntui_new_field_defns37");
		Assert.assertEquals("Work PO box" , label);
		
		label = mapper.getLabel("STRING_r_cntui_new_field_defns50");
		Assert.assertEquals("Group / Template Label" , label);
	}
}





