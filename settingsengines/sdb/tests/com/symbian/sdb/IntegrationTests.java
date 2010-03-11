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

package com.symbian.sdb;

import junit.framework.Test;
import junit.framework.TestSuite;

import com.symbian.sdb.configuration.ConfigurationIntegrationTest;
import com.symbian.sdb.contacts.DBMSContactFlowIntegrationTest;
import com.symbian.sdb.contacts.SQLiteContactDatabaseCreationIntegrationTest;
import com.symbian.sdb.contacts.SQLiteContactFlowIntegrationTest;
import com.symbian.sdb.contacts.SQLiteGroupHandlingIntegrationTest;
import com.symbian.sdb.contacts.importer.VCardContactImporterIntegrationTest;
import com.symbian.sdb.contacts.model.ContactHintIntegrationTest;
import com.symbian.sdb.contacts.template.DBMSTemplateIntegrationTest;
import com.symbian.sdb.contacts.template.DbmsTemplateReaderIntegrationTest;

public class IntegrationTests {

    public static Test suite() {
        TestSuite suite = new TestSuite("Integration tests for com.symbian.sdb");
        // $JUnit-BEGIN$
/*
        suite.addTest(ConfigurationIntegrationTest.suite());
        suite.addTest(SQLiteGroupHandlingIntegrationTest.suite());
        suite.addTest(SQLiteContactDatabaseCreationIntegrationTest.suite());
        suite.addTest(DBMSTemplateIntegrationTest.suite());
        suite.addTest(ContactHintIntegrationTest.suite());
        suite.addTest(DBMSContactFlowIntegrationTest.suite());
        suite.addTest(SQLiteContactFlowIntegrationTest.suite());
        suite.addTest(VCardContactImporterIntegrationTest.suite());
        suite.addTest(DbmsTemplateReaderIntegrationTest.suite());*/
        
        // $JUnit-END$
        return suite;
    }

}
