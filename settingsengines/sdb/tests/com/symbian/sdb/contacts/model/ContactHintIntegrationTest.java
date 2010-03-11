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

import java.io.File;
import java.util.Collections;
import java.util.Set;

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Test;

import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.contacts.dbms.model.ContactHintField;
import com.symbian.sdb.contacts.dbms.model.creator.DBMSContactBuilder;
import com.symbian.sdb.contacts.importer.VCardContactImporter;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateManager;


/**
 * @author jamesclark
 *
 */
public class ContactHintIntegrationTest extends BaseIntegrationTestCase	{

	private VCardContactImporter contactImporter;
	private SpeedDialManager speedDialManager;
	
	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(ContactHintIntegrationTest.class);
	}
	
	public static final File contactTemplate = new File("tests/config/contactHintTests/hintFieldCheck.rss");
	
	public void onSetUp(){
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
	}
	
	private enum testFixtures {
		emailable(new File("tests/config/contactHintTests/Emailable.vcf"), ContactHint.MAILABLE),
		home(new File("tests/config/contactHintTests/home.vcf"), ContactHint.HOME),
		landline(new File("tests/config/contactHintTests/landline.vcf"), ContactHint.LAND_LINE),
		phoneable(new File("tests/config/contactHintTests/Phoneable.vcf"), ContactHint.PHONABLE),
		Smsable(new File("tests/config/contactHintTests/Smsable.vcf"), ContactHint.SMSABLE),
		work(new File("tests/config/contactHintTests/work.vcf"), ContactHint.WORK),
		faxable(new File("tests/config/contactHintTests/faxable.vcf"), ContactHint.FAXABLE);
		
		ContactHint _hint;
		File _vCard;
		
		testFixtures(File vCard, ContactHint expectedHint){
			_vCard = vCard;
			_hint = expectedHint;
		}
		
		File getvCard(){
			return _vCard;
		}
		
		ContactHint getExpectedHint(){
			return _hint;
		}
	}
	
	@Test
	public void testHintGeneration() throws Exception{
	    System.setProperty("com.symbian.dbms.lib.path", "lib/");
	    
	    TemplateManager templateManager = new TemplateManager();
		ITemplateModel templateModel = templateManager.parse(contactTemplate.getAbsolutePath());
	
		//Order is relied upon later
		for(testFixtures testFixture: testFixtures.values()){
			Set<Contact> contacts = contactImporter.importContacts(Collections.singletonList(testFixture.getvCard()), templateModel);
		
			DBMSContactBuilder builder = new DBMSContactBuilder(speedDialManager);
			Assert.assertEquals("There should only be one contact created.", 1, contacts.size());
			for(Contact contact : contacts){
				builder.createNewContact(contact, templateModel);
			}
			ContactHintField hint = builder.getDBMSContact().getIdentityTable().getContactHintField();
			Assert.assertTrue("Invalid hint field for "+testFixture.getExpectedHint().toString(),(short)testFixture.getExpectedHint().getValue() == ((short)hint.getValue() & testFixture.getExpectedHint().getValue()));
		}
	}

	/**
	 * @param contactImporter the contactImporter to set
	 */
	public void setContactImporter(VCardContactImporter contactImporter) {
		this.contactImporter = contactImporter;
	}

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}
	
}
