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

import com.symbian.sdb.cmd.CommandLinev2Test;
import com.symbian.sdb.cmd.InputFileValidatorTest;
import com.symbian.sdb.cmd.ModeValidatorTest;
import com.symbian.sdb.configuration.ConfOptionsTest;
import com.symbian.sdb.configuration.ConfigValidatorTest;
import com.symbian.sdb.configuration.ConfigurationDbmsTest;
import com.symbian.sdb.configuration.ConfigurationParserTest;
import com.symbian.sdb.configuration.ConfigurationSqlite1Test;
import com.symbian.sdb.configuration.ConfigurationSqliteTest;
import com.symbian.sdb.configuration.DocumentVersionTest;
import com.symbian.sdb.configuration.PlatsecConfiguratorTest;
import com.symbian.sdb.configuration.SystemSettingsTest;
import com.symbian.sdb.configuration.policy.ParserTest;
import com.symbian.sdb.configuration.policy.PolicyAlwaysTest;
import com.symbian.sdb.configuration.policy.PolicyIDTest;
import com.symbian.sdb.configuration.policy.PolicySetTest;
import com.symbian.sdb.configuration.security.SymbianSecuritySettingsTest;
import com.symbian.sdb.contacts.BitsOperationUtilTest;
import com.symbian.sdb.contacts.SQLiteContactDatabaseCreationIntegrationTest;
import com.symbian.sdb.contacts.SQLiteContactFlowIntegrationTest;
import com.symbian.sdb.contacts.template.FieldContainerTest;
import com.symbian.sdb.contacts.model.ContactFieldTest;
import com.symbian.sdb.contacts.template.DbmsTemplateReaderTest;
import com.symbian.sdb.contacts.template.FieldTest;
import com.symbian.sdb.contacts.template.TemplateManagerNTest;
import com.symbian.sdb.contacts.template.TemplateManagerTest;
import com.symbian.sdb.contacts.template.TemplateMapperTest;
import com.symbian.sdb.database.DBManagerTest;
import com.symbian.sdb.database.SqlExecuterTest;
import com.symbian.sdb.mode.ModeParserTest;
import com.symbian.sdb.mode.flow.CedFlowTest;
import com.symbian.sdb.mode.flow.ContactsFlowTest;
import com.symbian.sdb.mode.flow.GenericFlowDbmsIntegrationTest;
import com.symbian.sdb.mode.flow.GenericFlowIntegrationTest;
import com.symbian.sdb.mode.flow.WorkflowFactoryTest;
import com.symbian.sdb.mode.flow.ced.CedProcessTest;
import com.symbian.sdb.mode.flow.ced.CedSchemaTest;
import com.symbian.sdb.settings.SettingsTest;
import com.symbian.sdb.util.ByteUtilTest;
import com.symbian.sdb.util.FileUtilTest;
import com.symbian.sdb.util.ValidationExceptionTest;

public class AllTests {

    public static Test suite() {
        TestSuite suite = new TestSuite("Test for com.symbian.sdb");
        // $JUnit-BEGIN$

        suite.addTest(WorkflowFactoryTest.suite());

        suite.addTest(ModeParserTest.suite());

        suite.addTest(ModeValidatorTest.suite());

        suite.addTest(CommandLinev2Test.suite());

        suite.addTest(SqlExecuterTest.suite());

        suite.addTest(GenericFlowDbmsIntegrationTest.suite());
        
        suite.addTest(ConfigValidatorTest.suite());
        
        suite.addTest(DbmsTemplateReaderTest.suite());
        
        suite.addTest(TemplateManagerNTest.suite());
        suite.addTest(TemplateManagerTest.suite());
        
        suite.addTest(TemplateMapperTest.suite());

        suite.addTest(FieldContainerTest.suite());
        suite.addTest(FieldTest.suite());
        
        suite.addTest(ConfOptionsTest.suite());
        suite.addTest(SystemSettingsTest.suite());
        suite.addTest(ConfigurationDbmsTest.suite());
        suite.addTest(ConfigurationSqliteTest.suite());
        suite.addTest(ConfigurationSqlite1Test.suite());
        suite.addTest(DocumentVersionTest.suite());
        suite.addTest(ConfigurationParserTest.suite());
        suite.addTest(CedFlowTest.suite());
        suite.addTest(CedProcessTest.suite());
        suite.addTest(CedSchemaTest.suite());
        suite.addTest(InputFileValidatorTest.suite());
        suite.addTest(ContactsFlowTest.suite());
        
        suite.addTestSuite(SQLiteContactDatabaseCreationIntegrationTest.class);
        suite.addTestSuite(SQLiteContactFlowIntegrationTest.class);
        
        suite.addTestSuite(PlatsecConfiguratorTest.class);

        suite.addTestSuite(DBManagerTest.class);

        suite.addTestSuite(SettingsTest.class);

        suite.addTestSuite(FileUtilTest.class);

        suite.addTestSuite(ByteUtilTest.class);

        suite.addTestSuite(PolicyAlwaysTest.class);
        suite.addTestSuite(PolicyIDTest.class);
        suite.addTestSuite(PolicySetTest.class);

        suite.addTestSuite(ValidationExceptionTest.class);
        suite.addTestSuite(ParserTest.class);
        suite.addTestSuite(SymbianSecuritySettingsTest.class);
        
        suite.addTest(BitsOperationUtilTest.suite());
        
        suite.addTest(ContactFieldTest.suite());

        // $JUnit-END$
        return suite;
    }

}
