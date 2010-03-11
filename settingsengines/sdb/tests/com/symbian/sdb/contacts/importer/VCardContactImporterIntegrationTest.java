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

package com.symbian.sdb.contacts.importer;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import junit.framework.JUnit4TestAdapter;

import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.template.ITemplateManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;

/**
 * @author krzysztofZielinski
 *
 */
public class VCardContactImporterIntegrationTest extends BaseIntegrationTestCase     {
    
    private static final String VCARD_FILE_NAME = "testdata/contacts/vcard/vcard2.vcf";
    
    private ContactsImporter contactImporter;
    
    public void setContactImporter(ContactsImporter contactImporter) {
        this.contactImporter = contactImporter;
    }

    public void testCreateNewContactDatabaseMocked() throws Exception {
        List<File> vCardFiles = new ArrayList<File>();
        vCardFiles.add(new File(VCARD_FILE_NAME));
        
        ITemplateModel contactsTemplateModel = createTemplateModel();
        Set<Contact> contacts = contactImporter.importContacts(vCardFiles, contactsTemplateModel);

        assertContacts(contacts);
    }
    
    private void assertContacts(Set<Contact> contacts) {
        for (Contact contact : contacts) {
            assertSingleContact(contact);
        }
        
    }

    private void assertSingleContact(Contact contact) {
        assertTrue(contact.getLastName().matches("Rambo[12]"));
        
        if ("Rambo1".equals(contact.getLastName())) {
            assertRambo1(contact);
        }
        else if ("Rambo2".equals(contact.getLastName())) {
            assertRambo2(contact);
        }
        else {
            fail("Unexpected contact found in vCard file!");
        }
    }

    private void assertRambo2(Contact contact) {
        assertEquals("John", contact.getFirstName());
        assertEquals("Rambo2", contact.getLastName());
        assertEquals(1, contact.getEmails().size());
        assertEquals(2, contact.getPhoneNumbers().size());  
        assertEquals(0, contact.getGroups().size());
        assertEquals(9, contact.getFields().size());
    }

    private void assertRambo1(Contact contact) {
        assertEquals("John", contact.getFirstName());
        assertEquals("Rambo1", contact.getLastName());
        assertEquals(1, contact.getEmails().size());
        assertEquals(1, contact.getPhoneNumbers().size());
        assertEquals(0, contact.getGroups().size());
        assertEquals(6, contact.getFields().size());
    }

    private ITemplateModel createTemplateModel() throws SDBExecutionException, TemplateParsingException {
        System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		ITemplateManager manager = new TemplateManager();
        final ITemplateModel templateModel = manager.parse("tests/config/CNTMODEL.RSS");
        return templateModel;
    }
    
    public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(VCardContactImporterIntegrationTest.class);
	}
    
}
