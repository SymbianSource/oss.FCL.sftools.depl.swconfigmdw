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
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Iterator;
import java.util.List;

import junit.framework.Assert;

import org.junit.Test;

import com.symbian.sdb.contacts.dbms.model.AbstractContactHeader;
import com.symbian.sdb.contacts.dbms.model.ContactFieldHeader;
import com.symbian.sdb.contacts.dbms.model.ContactHeaderForTemplate;

/**
 * @author jamesclark
 *
 */
public class CheckTextHeaderTestCase extends BasicDBMSContactsDBComparisonTest {

	// This test currently doesn't pass due to the label mapping not being correctly set.
	@Test
	public void checkHeaderHasAdditionalMappingFlagSet() throws Exception{
		File vcard = new File("testdata/contacts/vcard/vcard2.vcf");
		File genDB = new File(getPathTo("DBS_100065FF_Contacts93_headerTest.cdb"));
		TestConfig test = new TestConfig(new File(getPathTo("93ui.rss")),new File(getPathTo("93_emu_created_vCard2.cdb")), genDB, vcard);
		
		runContactsFlow(test);
		
		Connection emuCon = getDBMSConnection(test.getValidDBPath(), null);
		Connection genCon = getDBMSConnection(test.getGenDBPath(), null);
		
		PreparedStatement statementEMU = emuCon.prepareStatement("select CM_Header FROM contacts");
		statementEMU.execute();
		ResultSet rsEMU = statementEMU.getResultSet();
		
		PreparedStatement statementGEN = genCon.prepareStatement("select CM_Header FROM contacts");
		statementGEN.execute();
		ResultSet rsGEN = statementGEN.getResultSet();
		int idCount = -1;
		while(rsEMU.next()){
			idCount++;
			rsGEN.next();
			AbstractContactHeader Emuheader = new ContactHeaderForTemplate(rsEMU.getBytes(1));
			List<ContactFieldHeader>Emufields = Emuheader.getFieldHeaderList();
			
			AbstractContactHeader Genheader = new ContactHeaderForTemplate(rsGEN.getBytes(1));
			List<ContactFieldHeader>Genfields = Genheader.getFieldHeaderList();
			
			Iterator<ContactFieldHeader> itr = Genfields.iterator();
			ContactFieldHeader genfield = itr.next();
			StringBuilder sb = new StringBuilder();
			for(ContactFieldHeader field : Emufields){
				if(!field.getFieldLabel().getLabel().equals(genfield.getFieldLabel().getLabel())){
					//System.out.println("Skipping comparison; mismatch on field labels. Emu: "+field.getFieldLabel().getLabel()+" Gen: "+genfield.getFieldLabel().getLabel());
					// This is expected while we only support text fields
					continue;
				}
				if(field.hasAdditionalVCardMappings() != genfield.hasAdditionalVCardMappings()){
					//Assert.assertEquals("The generated header for ContactID "+idCount+" Field "+field.getFieldLabel().getLabel()+" should match the emulator header", field.hasAdditionalHintValues(), itr.next().hasAdditionalHintValues());
					sb.append("The generated header for ContactID "+idCount+" Field "+field.getFieldLabel().getLabel()+" should match the emulator header. Emulator = " + field.hasAdditionalVCardMappings()+" Generated = " + genfield.hasAdditionalVCardMappings()+"\n");
				}
				int emuFieldCount=0, genFieldCount=0;
				if(field.getFieldAdditionalUIDValues()!=null){
					emuFieldCount= field.getFieldAdditionalUIDValues().length;
				}
				if(genfield.getFieldAdditionalUIDValues()!=null){
					genFieldCount= genfield.getFieldAdditionalUIDValues().length;
				}
				if(emuFieldCount!=genFieldCount){
					sb.append("The generated header for ContactID "+idCount+" Field "+field.getFieldLabel().getLabel()+" should match the emulator header. Emulator = " + emuFieldCount+" Generated = " + genFieldCount+"\n");
					System.out.print("*");
				}
				else{
					System.out.print(" ");
				}
				System.out.println("The generated header for ContactID "+idCount+" Field "+field.getFieldLabel().getLabel()+" should match the emulator header. Emulator = " + emuFieldCount+" Generated = " + genFieldCount);
				if(itr.hasNext()){
					genfield = itr.next();
				}
			}
			if(sb.length()>0){
				Assert.fail(sb.toString());
			}
		}
		
		
	}
}
