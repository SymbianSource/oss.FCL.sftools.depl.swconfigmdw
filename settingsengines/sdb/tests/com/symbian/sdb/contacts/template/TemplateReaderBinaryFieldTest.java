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
// TemplateReaderBinaryFieldTest.java
//

package com.symbian.sdb.contacts.template;


import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Iterator;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

import com.symbian.sdb.contacts.dbms.ContactDaoDBMS;
import com.symbian.sdb.contacts.template.model.dbms.DbmsTemplateReader;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.util.FileUtil;

public class TemplateReaderBinaryFieldTest {

	private static final String TEST_ROOT_PATH = "tests/config/";
	
	ITemplateModel templateModelFromDb;
	ITemplateModel templateModelFromRss;
	DBManager db = new DBManager();
	
	private final String dbName = "sdb_93emul.db";
	private final String rssName = "93ui.rss";
	private final String testConfigPath = TEST_ROOT_PATH + "templateReaderTests/";
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		System.setProperty("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml");
	}

	@Before
	public void setUp() throws Exception {
		
		openDatabaseConnection();
	    readTemplateModelFromDb();
	    readTemplateModelFromRss();
	}
	
	private void readTemplateModelFromRss() throws TemplateParsingException {
		TemplateManager manager = new TemplateManager();
		templateModelFromRss = manager.parse(testConfigPath + rssName);
	}

	private void readTemplateModelFromDb() throws TemplateParsingException {
		ContactDaoDBMS contactDao = new ContactDaoDBMS();
	    contactDao.setConnectionProvider(db);
	    
	    DbmsTemplateReader reader = new DbmsTemplateReader();
	    reader.setContactDao(contactDao);
	    
	    TemplateManager manager = new TemplateManager();
	    manager.setTemplateReader(reader);
	    templateModelFromDb = manager.read();
	}

	private void openDatabaseConnection() throws SDBExecutionException {
		File tmpDbFile = new File( TEST_ROOT_PATH + dbName + ".tmp");
        try {
            FileUtil.copy(testConfigPath + dbName, tmpDbFile.getPath());
        } 
        catch (IOException ex) {
            throw new SDBExecutionException("Failed to copy input DB to temporary location: " + tmpDbFile.getPath() + ": " + ex.getMessage(), ex);
        }
		db.openConnection(DBType.DBMS, tmpDbFile.getAbsolutePath(), null);
	}
	
	//TODO revert when binary fields are finished
	@Test
	public void testPhotoField() throws Exception {
	//	Collection<IField> dbFields = templateModelFromDb.getFields().get("KIntContactFieldVCardMapPHOTO");
	//	Collection<IField> rssFields = templateModelFromRss.getFields().get("KIntContactFieldVCardMapPHOTO");
	//	assertFieldAttributes(dbFields, rssFields);
	}

	private void assertFieldAttributes(Collection<IField> dbFields, Collection<IField> rssFields) {
		Assert.assertEquals(dbFields.size(), rssFields.size());
		for (Iterator dbFieldIterator = dbFields.iterator(),
				rssFieldIterator = rssFields.iterator() ; 
					rssFieldIterator.hasNext(); ) {
			IField dbField = (IField) dbFieldIterator.next();
			IField rssField = (IField) rssFieldIterator.next();
			//Just comparing static value at this time
			/*
			Assert.assertEquals(dbField.getFieldName(), rssField.getFieldName());
			Assert.assertEquals(dbField.getCategory(), rssField.getCategory());
			Assert.assertEquals(dbField.getFieldType(), rssField.getFieldType());
			Assert.assertEquals(dbField.getIndex(), rssField.getIndex());
			*/
			Assert.assertEquals(dbField.getFieldName(), "STRING_r_cntui_new_field_defns48");
			Assert.assertEquals(dbField.getCategory(), (byte)0); //EContactCategoryNone
			Assert.assertEquals(dbField.getFieldType(), "KUidContactFieldPictureValue");
			Assert.assertEquals(dbField.getIndex(), 47);
			assertProperties(dbField, rssField);
			assertFeildFlags(dbField, rssField);
		}
	}
	
	private void assertProperties(IField dbField, IField rssField) {
		//Assert.assertEquals(dbField.getProperties().size(), rssField.getProperties().size());
		Assert.assertEquals(dbField.getProperties().size(), 0);
		for (Iterator dbFieldPropertyIterator = dbField.getProperties().iterator(),
				rssFieldPropertyIterator = rssField.getProperties().iterator(); 
						rssFieldPropertyIterator.hasNext();) {
			Flag dbFieldProperty = (Flag) dbFieldPropertyIterator.next();
			Flag rssFieldProperty = (Flag) rssFieldPropertyIterator.next();
			//Assert.assertEquals(dbFieldProperty.getUID(), rssFielProperty.getUID());
			Assert.assertEquals(dbFieldProperty.getUID(), rssFieldProperty.getUID());
		}
	}

	private void assertFeildFlags(IField dbField, IField rssField) {
		Assert.assertTrue(dbField.getFlags().size() > rssField.getFlags().size());
		for (Iterator dbFieldFlagIterator = dbField.getFlags().iterator(),
				rssFieldFlagIterator = rssField.getFlags().iterator(); 
						rssFieldFlagIterator.hasNext();) {
			Flag dbFieldFlag = (Flag) dbFieldFlagIterator.next();
			Flag rssFieldFlag = (Flag) rssFieldFlagIterator.next();
			Assert.assertEquals(dbFieldFlag.getUID(), rssFieldFlag.getUID());
		}
	}

	@After
	public void tearDown() throws Exception {
		db.closeConnection();
		File tmpDbFile = new File(testConfigPath + dbName + ".tmp");
		tmpDbFile.delete();
	}
	
	@AfterClass
	public static void tearDownAfterClass() throws Exception {
	}
}
