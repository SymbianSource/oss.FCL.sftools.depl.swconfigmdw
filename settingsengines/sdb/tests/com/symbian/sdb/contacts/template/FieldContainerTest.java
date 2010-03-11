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


import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.resource.RSSParser;

public class FieldContainerTest {
	FieldContainer container; 
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(FieldContainerTest.class); 
    }
    
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		System.setProperty("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml");
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
    	TemplateMapper mapper = TemplateMapper.getInstance();
    	
    	RSSParser resourceParser = RSSFactory.getRSSParserKit("tests/config/CNTMODEL.RSS").getParser();
    	try { 
	        HashMap<String, String> storagemap = mapper.getMapping(ContactMapTypes.storage);
	        HashMap<String, String> categorymap = mapper.getMapping(ContactMapTypes.category);
	        HashMap<String, String> flagmap = mapper.getMapping(ContactMapTypes.flags);
	        
	        resourceParser.setCategoryMapping(categorymap);
	        resourceParser.setFlagMapping(flagmap);
	        resourceParser.setStorageMapping(storagemap);
    	} catch (MappingMissingException ex) {
    		throw new SDBExecutionException("Configuration file error: " + ex.getMessage());
    	}
        resourceParser.document();
        container = resourceParser.getContainer();
        container.setMapper(mapper);
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testFlags() {
		IField field = container.get(2);
		List<Flag> flags = field.getFlags();
		
		Assert.assertTrue(flags.size() == 1);
		Flag flag = flags.get(0);
		Assert.assertEquals("EContactFieldFlagDisabled", flag.getUID());
		Assert.assertEquals(8, flag.getValue());
		
		Collection<IField> fields = container.get("KIntContactFieldVCardMapPHOTO");
		Assert.assertTrue(fields.size() == 1);
		field = fields.iterator().next();
		
		flags = field.getFlags();
		
		Assert.assertTrue(flags.size() == 1);
		flag = flags.get(0);
		Assert.assertEquals("EContactFieldFlagHidden", flag.getUID());
		Assert.assertEquals(1, flag.getValue());
		
		
		field = container.get(container.getSize() - 10 -1);
		flags = field.getFlags();
		
		Assert.assertTrue(flags.size() == 2);
		flag = flags.get(0);
		Assert.assertEquals("KIntFieldFlagSynchronize", flag.getUID());
		Assert.assertEquals(4, flag.getValue());
		
		flag = flags.get(1);
		Assert.assertEquals("KIntFieldFlagFilterable2", flag.getUID());
		Assert.assertEquals(64, flag.getValue());

		fields = container.get("KIntContactFieldVCardMapLOGO");
		Assert.assertEquals(1, fields.size());
		field = fields.iterator().next();
		flags = field.getFlags();
		Assert.assertEquals(1, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Hidden"));
		
		field = container.get(container.getSize() - 11);
		flags = field.getFlags();
		Assert.assertEquals(2, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Synchronize"));
		Assert.assertTrue(flags.get(1).getUID().contains("Filterable2"));
	}
	

	@Test
	public void testCategory() {
		IField field = container.get(0);
		Assert.assertEquals((byte)1, field.getCategory());

		Collection<IField> fields = container.get("KIntContactFieldVCardMapORG");
		Assert.assertTrue(fields.size() == 1);
		field = fields.iterator().next();
		Assert.assertEquals((byte)2, field.getCategory());
	}
	
	@Test
	public void test() throws MappingMissingException {
		Collection<IField> fields = container.get("KIntContactFieldVCardMapPHOTO");
		Assert.assertTrue(fields.size() == 1);
		Assert.assertEquals("10005dd1", Integer.toHexString(fields.iterator().next().getFieldTypeValue()));
	
		fields = container.get("KIntContactFieldVCardMapBDAY");
		Assert.assertTrue(fields.size() == 1);
		Assert.assertEquals(3, fields.iterator().next().getStorageType());
		
		
		fields = container.get("KIntContactFieldVCardMapAnniversary");
		Assert.assertTrue(fields.size() == 1);
		Assert.assertEquals(3, fields.iterator().next().getStorageType());
		Assert.assertEquals("Anniversary", fields.iterator().next().getFieldNameValue());
		
	}
	
	@Test
	public void testGetVCardMappingPropertyToContactSetIndexFieldType() throws MappingMissingException {
		Collection<IField> fields = container.get("KIntContactFieldVCardMapNOTE");
		Assert.assertTrue(fields.size() == 1);
		Assert.assertEquals(48, fields.iterator().next().getIndex());

		fields = container.get("KIntContactFieldVCardMapUnusedN");
		Assert.assertEquals(12, fields.size());
	
		Iterator<IField> it = fields.iterator();
		
		IField field = it.next();
		Assert.assertEquals(0, field.getIndex());
		Assert.assertTrue(Integer.toHexString(field.getFieldTypeValue()).toUpperCase().equals("1000178C"));
		field = it.next();
		Assert.assertEquals(1, field.getIndex());
	    Assert.assertTrue(Integer.toHexString(field.getFieldTypeValue()).toUpperCase().equals("1000137C"));
		Assert.assertEquals(2, it.next().getIndex());
		Assert.assertEquals(3, it.next().getIndex());
		Assert.assertEquals(4, it.next().getIndex());
	}
	
}
