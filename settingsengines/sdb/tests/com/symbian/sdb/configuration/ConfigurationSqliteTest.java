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

package com.symbian.sdb.configuration;

import java.io.File;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.w3c.dom.Document;

import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;

public class ConfigurationSqliteTest {
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigurationSqliteTest.class); 
    }
    
    Mockery validatorContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    
    Mockery settingsContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    Mockery platsecContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    ConfigurationValidator validator;
    Configuration conf = new Configuration();

    SystemSettings settings;
    PlatsecConfigurator platsec;
    
    @Before
    public void setUp() throws Exception {
        DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
        lDocBuilderFact.setNamespaceAware(true);
        DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
        final Document document = lBuilder.parse(new File("tests/config/XML/nextVersion2.xml"));
        
        validator = validatorContext.mock(ConfigurationValidator.class);
        
        validatorContext.checking(new Expectations() {{
            one (validator).loadAndValidate(with(any(File.class))); will(returnValue(document));
            one (validator).getVersion(); will(returnValue(DocumentVersion.V20));
        }});
              
    }

    @Test
    public void testInitialize() throws SDBExecutionException, SDBValidationException, Exception {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.SQLITE, validator);
        validatorContext.assertIsSatisfied();
        Assert.assertTrue(DbOptions.ENCODING.getValue().contains("UTF-8"));
        Assert.assertTrue(DbOptions.PAGE_SIZE.getValue().contains("2048"));
        
    }

    @Test
    public void testApplySettingsUpdateHasSettings() throws SDBExecutionException {
        settings = settingsContext.mock(SystemSettings.class);
        
        settingsContext.checking(new Expectations() {{
            one (settings).hasSettingsTable(); will(returnValue(true));
            never (settings).applySystemSettings();
        }});
        
       
        conf.applySettings(true, settings);
    }
    
    @Test
    public void testApplySettingsUpdateNoSettings() throws SDBExecutionException {
        settings = settingsContext.mock(SystemSettings.class);
        settingsContext.checking(new Expectations() {{
            one (settings).hasSettingsTable(); will(returnValue(false));
            one (settings).applySystemSettings();
        }});
        
        conf.applySettings(true, settings);
    }

    @Test
    public void testApplySettings() throws SDBExecutionException {
        settings = settingsContext.mock(SystemSettings.class);
        settingsContext.checking(new Expectations() {{
            one (settings).hasSettingsTable(); will(returnValue(false));
            one (settings).applySystemSettings();
        }});
        
        conf.applySettings(false, settings);
    }
    
    @Test
    public void testApplySecurity() throws SDBExecutionException, SDBValidationException {
        platsec = platsecContext.mock(PlatsecConfigurator.class);
        platsecContext.checking(new Expectations() {{
            one (platsec).applySecuritySettings(with(any(SecuritySettings.class)));
        }});
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.SQLITE, validator);
        conf.applySecurity(DBType.SQLITE, platsec);
    }
    

    @Test
    public void testGetPragmaStm() throws SDBExecutionException, SDBValidationException {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.SQLITE, validator);
        List<String> list = conf.getPragmaStm(DBType.SQLITE);
        Assert.assertNotNull(list);
        Assert.assertTrue(list.size() == 2);
        Assert.assertEquals(DbOptions.PAGE_SIZE.getValue(), list.get(0));
        Assert.assertEquals(DbOptions.ENCODING.getValue(), list.get(1));
    }

    @Test
    public void testGetConnectionString() throws SDBExecutionException, SDBValidationException {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.SQLITE, validator);
        String string = conf.getConnectionString(DBType.SQLITE);
        Assert.assertNull(string);
    }

}
