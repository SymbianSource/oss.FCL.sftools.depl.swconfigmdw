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

package com.symbian.sdb.contacts;

import java.io.File;

import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.template.ITemplateManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateManager;
import com.symbian.sdb.contacts.template.TemplateModel;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.mode.flow.ContactsFlow;
import com.symbian.sdb.settings.Settings;


/**
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactDatabaseCreationIntegrationTest extends BaseIntegrationTestCase {

    public static final String databaseFilePath = "testdata/contacts/test_contact.sdb";
    
    private ContactsFlow contactsFlow;
    
    @Override
    protected void onTearDown() throws Exception {
        // delete existing database
        deleteFile(databaseFilePath);
    }

    @Override
    protected void onSetUp() throws Exception {
        super.onSetUp();
        
        deleteFile(databaseFilePath);
        
	
    }
    
    private void deleteFile(String filePath) {
        File file = new File(filePath);
        if (file.exists())  {
            file.delete();            
        }
    }
    
    public void testCreateRealNewContactDatabase() throws Exception {
    	  File dbFile = new File(databaseFilePath);
//        List<File> vCardFiles = new ArrayList<File>();
//        vCardFiles.add(new File("testdata/contacts/vcard/vcard2.vcf"));
//        ITemplateModel templateModel = createMockTemplateModel();
//        Group group = new Group("Group1");
//        Set<Group> groups = new HashSet<Group>();
//        groups.add(group);        
        
        assertTrue(!dbFile.exists());
        
		String[] args = {"-m", "sqlite.contacts", 
				"-t", "tests/config/CNTMODEL.RSS", 
				"-o", databaseFilePath,
				"testdata/contacts/vcard/vcard2.vcf"};
		try {
			
			CmdLinev2 cmd = new CmdLinev2();
			boolean result = cmd.parseArguments(args);
			
			new Settings().configure(cmd);	
			contactsFlow.setSqliteTemplateManager(createMockTemplateManager());
			contactsFlow.validateOptions(cmd);
			contactsFlow.start(cmd);

		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
        
        
       // contactFlow.createContacts(vCardFiles, templateModel, groups);
		
		// TODO is this really testing anything.
        assertTrue(dbFile.exists());
    }

    /**
     * @return
     */
    public static TemplateManager createMockTemplateManager() throws SDBExecutionException, TemplateParsingException {
    	
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		ITemplateManager manager = new TemplateManager();
		final ITemplateModel templateModel = manager.parse("tests/config/CNTMODEL.RSS");
    	
        Mockery templateManagerMockery = new Mockery() {{
            setImposteriser(ClassImposteriser.INSTANCE);
        }};
        final TemplateManager templateManagerMock = templateManagerMockery.mock(TemplateManager.class);
        try {
        	templateManagerMockery.checking(new Expectations() {{ 
                    atLeast(1).of(templateManagerMock).parse(with(any(String.class)));will(returnValue(templateModel));
                    allowing (templateManagerMock).persistTemplate(with(any(TemplateModel.class)));
                    }});
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return templateManagerMock;
    }
    
    public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(SQLiteContactDatabaseCreationIntegrationTest.class);
	}

    public void setContactsFlow(ContactsFlow contactsFlow) {
        this.contactsFlow = contactsFlow;
    }
}
