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

import java.util.List;
import java.util.Map;

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;

public class TemplateManagerTest {
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(TemplateManagerTest.class); 
    }
    
    @BeforeClass
    public static void setUpBeforeClass() {
    	System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
    	System.setProperty("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml");
    }
    
    ITemplateModel templateModel = null;

    
    @Before
    public void setUp() throws SDBExecutionException, Exception {    	
        ITemplateManager manager = new TemplateManager();
        templateModel = manager.parse("tests/config/CNTMODEL.RSS");
    }
    
	@Test
	public void testGetVCardMappingPropertyToContactFieldType() 
	throws MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("NOTE", new String[0]);
        Integer result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertNotNull(result);
        Assert.assertEquals("1000401c", Integer.toHexString(result));

        data = new PropertyData("FN", new String[0]);
        result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertEquals("0", Integer.toHexString(result));

        
        String[] propertyParameters = new String[2];
        propertyParameters[0] = "MODEM";
        propertyParameters[1] = "WORK";
        data = new PropertyData("TEL", propertyParameters);
        result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertEquals("1000130e", Integer.toHexString(result));

        
   //     data = new PropertyData("PHOTO", new String[0]);
   //     result = templateModel.getVCardMappingPropertyToContactFieldType(data);
   //     Assert.assertEquals("10005dd1", Integer.toHexString(result));
	}

	@Test
	public void testGetVCardMappingPropertyToContactSetIndexFieldType() throws MappingMissingException {
        String[] propertyParameters = new String[3];
        propertyParameters[0] = "HOME";
        propertyParameters[1] = "CELL";
        propertyParameters[2] = "VOICE";
        PropertyData data = new PropertyData("TEL", propertyParameters);
        Map<Integer, Integer> result = templateModel.getvCardMappingPropertyToFieldIndexTypeSet(data);
        Assert.assertEquals(5, result.keySet().iterator().next());
        
        
        propertyParameters = new String[2];
        propertyParameters[0] = "MODEM";
        propertyParameters[1] = "WORK";
        data = new PropertyData("TEL", propertyParameters);
        result = templateModel.getvCardMappingPropertyToFieldIndexTypeSet(data);
        Assert.assertEquals(32, result.keySet().iterator().next());
        
        data = new PropertyData("N", new String[0]);
        result = templateModel.getvCardMappingPropertyToFieldIndexTypeSet(data);
        Assert.assertTrue("size is " + result.size(), result.size() == 10);
        
        Assert.assertTrue(result.keySet().contains(0));
        Assert.assertTrue(result.keySet().contains(1));
        Assert.assertTrue(result.keySet().contains(2));
        Assert.assertTrue(result.keySet().contains(3));
        Assert.assertTrue(result.keySet().contains(4));
        
        Assert.assertTrue(Integer.toHexString(result.get(0)).toUpperCase().equals("1000178C"));
        Assert.assertTrue(Integer.toHexString(result.get(1)).toUpperCase().equals("1000137C"));
	}

	@Test
	public void testGetVCardMappingPropertyToStorageFieldType() 
	throws MultipleTemplateValueException, MappingMissingException {
        PropertyData data = new PropertyData("NOTE", new String[0]);
        Integer result = templateModel.getVCardMappingPropertyToStorageFieldType(data);
        Assert.assertEquals(0, result);
	}

	@Test
	public void testGetVCardMappingPropertyToFieldName()
	throws MultipleTemplateValueException, MappingMissingException {
        
        String[] arr = new String[1];
        arr[0] = "HOME";
        
        PropertyData data = new PropertyData("ADR", arr);
        String result = templateModel.getVCardMappingPropertyToFieldName(data, 2);
        Assert.assertEquals("Home address", result);
        
    	data = new PropertyData("ADR", arr);
        result = templateModel.getVCardMappingPropertyToFieldName(data, 6);
        Assert.assertEquals("Home country", result);
	}

	@Test
	public void testGetVCardMappingPropertyToIndex()
	throws MultipleTemplateValueException, MappingMissingException {
        String[] propertyParameters = new String[3];
        propertyParameters[0] = "HOME";
        propertyParameters[1] = "CELL";
        propertyParameters[2] = "VOICE";
        PropertyData data = new PropertyData("TEL", propertyParameters);
        int result = templateModel.getvCardMappingPropertyToFieldIndex(data);
        Assert.assertEquals(5, result);

        
        propertyParameters = new String[2];
        propertyParameters[0] = "MODEM";
        propertyParameters[1] = "WORK";
        data = new PropertyData("TEL", propertyParameters);
        result = templateModel.getvCardMappingPropertyToFieldIndex(data);
        Assert.assertEquals(32, result);
    
	}
	
	@Test
	public void testTemplateContainsMappingForVCardProperty() 
	throws MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("NOTE", new String[0]);
        boolean res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);
        
        data = new PropertyData("FN", new String[0]);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);
        
        String[] propertyParameters = new String[3];
        propertyParameters[2] = "CELL";
        propertyParameters[1] = "WORK";
        propertyParameters[0] = "VOICE";

        data = new PropertyData("TEL", propertyParameters);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);
        
        
        propertyParameters = new String[3];
        propertyParameters[2] = "CELL";
        propertyParameters[1] = "HOME";
        propertyParameters[0] = "VOICE";

        data = new PropertyData("TEL", propertyParameters);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);
	}

    @Test(expected=MultipleTemplateValueException.class)
    public void testGetVCardMappingPropertyToContactFieldType2() 
    	throws SDBExecutionException, MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("N", new String[0]);
    	Integer result = templateModel.getVCardMappingPropertyToContactFieldType(data);
    }
	
    @Test(expected=MappingMissingException.class)
    public void testNoMapping()	throws MultipleTemplateValueException, MappingMissingException {
        String[] propertyParameters = new String[1];
        propertyParameters[0] = "xxx";
        PropertyData data = new PropertyData("NOTE", propertyParameters);
    	boolean result2 = templateModel.templateContainsMappingForVCardProperty(data);
    	Assert.assertFalse(result2);
    }
    
	@Test
	public void testGetVCardMappingPropertyToFlag()
	throws MultipleTemplateValueException, MappingMissingException {
		
		IField field = templateModel.getFields().get(0);
		List<Flag> flags = field.getFlags();
		Assert.assertEquals(1, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Disabled"));
		
		field = templateModel.getFields().get(2);
		flags = field.getFlags();
		Assert.assertEquals(1, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Disabled"));
	}
	
	@Test
	public void testParseInvalidTemplate() {
		ITemplateManager manager = new TemplateManager();
		try {
			manager.parse("tests/config/template_itests/corrupted2.rss");
			Assert.fail("Should have failed with template parsing exception: No fields found in resource file");
		} catch (TemplateParsingException ex) {
			Assert.assertTrue("Exception expected: No fields found in resource file. Got:" + ex.getMessage(), 
					ex.getMessage().matches(".*No fields found in resource file.*"));
		}
	}

}
