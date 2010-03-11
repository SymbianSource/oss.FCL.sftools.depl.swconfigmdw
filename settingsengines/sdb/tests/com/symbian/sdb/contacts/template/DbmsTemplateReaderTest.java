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

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.contacts.dbms.ContactDaoDBMS;
import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.contacts.template.model.dbms.DbmsTemplateReader;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.util.FileUtil;

public class DbmsTemplateReaderTest {
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(DbmsTemplateReaderTest.class); 
    }
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		System.setProperty("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml");
	}

	ITemplateModel templateModel;
	DBManager db;

	@Before
	public void setUp() throws Exception {
		File tmpDbFile = new File("tests/config/sdb_94rss.db.tmp");
        try {
            FileUtil.copy("tests/config/templateReaderTests/sdb_94rss.db", tmpDbFile.getPath());
        } catch (IOException ex) {
            throw new SDBExecutionException("Failed to copy input DB to temporary location: " + tmpDbFile.getPath() + ": " + ex.getMessage(), ex);
        }
        
		db = new DBManager();
		db.openConnection(DBType.DBMS, tmpDbFile.getAbsolutePath(), null);
		
		TemplateManager manager = new TemplateManager();
	    DbmsTemplateReader reader = new DbmsTemplateReader();
	    ContactDaoDBMS contactDao = new ContactDaoDBMS();
	    contactDao.setConnectionProvider(db);
	    
	    reader.setContactDao(contactDao);
	    manager.setTemplateReader(reader);
	    templateModel = manager.read();
	}

	@After
	public void tearDown() throws Exception {
		db.closeConnection();
		File tmpDbFile = new File("tests/config/templateReaderTests/sdb_94rss.db.tmp");
		tmpDbFile.delete();
	}

	@Test
	public void testGetVCardMappingPropertyToContactFieldType() 
	throws MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("NOTE", new String[0]);
   //     Integer result = templateModel.getVCardMappingPropertyToContactFieldType(data);
   //     Assert.assertNotNull(result);
   //     Assert.assertEquals("1000401c", Integer.toHexString(result));

       // data = new PropertyData("FN", new String[0]);
       // result = templateModel.getVCardMappingPropertyToContactFieldType(data);
       // Assert.assertEquals("0", Integer.toHexString(result));

        
        String[] propertyParameters = new String[3];
        propertyParameters[0] = "VOICE";
        propertyParameters[1] = "HOME";
        propertyParameters[2] = "CELL";
        
        data = new PropertyData("TEL", propertyParameters);
 //       Integer  result = templateModel.getVCardMappingPropertyToContactFieldType(data);
  //      Assert.assertEquals("1000130e", Integer.toHexString(result));

        
      //  data = new PropertyData("PHOTO", new String[0]);
      //  result = templateModel.getVCardMappingPropertyToContactFieldType(data);
      //  Assert.assertEquals("10005dd1", Integer.toHexString(result));
	}

	@Test
	public void testGetVCardMappingPropertyToStorageFieldType() 
	throws MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("X-ANNIVERSARY", new String[0]);
    	//TODO only storage fields done 
        //Integer result = templateModel.getVCardMappingPropertyToStorageFieldType(data);
        //Assert.assertEquals(3, result);
        
        data = new PropertyData("NOTE", new String[0]);
        Integer result = templateModel.getVCardMappingPropertyToStorageFieldType(data);
        Assert.assertEquals(0, result);
	}

	@Test
	public void testGetVCardMappingPropertyToFieldName()
	throws MultipleTemplateValueException, MappingMissingException {
    	PropertyData data = new PropertyData("X-ANNIVERSARY", new String[0]);
        String result = templateModel.getVCardMappingPropertyToFieldName(data);
     //   Assert.assertEquals("Anniversary", result);
        
        String[] arr = new String[1];
        arr[0] = "HOME";
        
    	data = new PropertyData("ADR", arr);
        result = templateModel.getVCardMappingPropertyToFieldName(data, 2);
        Assert.assertEquals("Home address", result);
        
    	data = new PropertyData("ADR", arr);
        result = templateModel.getVCardMappingPropertyToFieldName(data, 6);
        Assert.assertEquals("Home country", result);
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

	@Test
	public void testGetVCardMappingPropertyToFlag()
	throws MultipleTemplateValueException, MappingMissingException {
		
		IField field = templateModel.getFields().get(0);
		List<Flag> flags = field.getFlags();
		Assert.assertEquals(2, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Disabled") || 
				flags.get(1).getUID().contains("Disabled"));
		
		field = templateModel.getFields().get(2);
		flags = field.getFlags();
		Assert.assertEquals(2, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Disabled") || 
				flags.get(1).getUID().contains("Disabled"));
/*	
		Collection<IField> fields = templateModel.getFields().get("KIntContactFieldVCardMapLOGO");
		Assert.assertEquals(1, fields.size());
		field = fields.iterator().next();
		flags = field.getFlags();
		Assert.assertEquals(1, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Hidden"));
		
		Collection<IField> fields = templateModel.getFields().get("KIntContactFieldVCardMapPHOTO");
		Assert.assertEquals(1, fields.size());
		field = fields.iterator().next();
		flags = field.getFlags();
		Assert.assertEquals(1, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Hidden"));
*/	
		field = templateModel.getFields().get(templateModel.getFields().getSize() - 11);
		flags = field.getFlags();
		Assert.assertEquals(2, flags.size());
		Assert.assertTrue(flags.get(0).getUID().contains("Hidden"));
		Assert.assertTrue(flags.get(1).getUID().contains("Synchronize"));
	}
	
	@Test
	public void testCategory() {
		IField field = templateModel.getFields().get(0);
		Assert.assertEquals((byte)1, field.getCategory());

		Collection<IField> fields = templateModel.getFields().get("KIntContactFieldVCardMapORG");
		Assert.assertTrue(fields.size() == 1);
		field = fields.iterator().next();
		//TODO update this test
		//Assert.assertEquals(2, field.getCategory());
	}
}
