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
import org.jmock.States;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.w3c.dom.Document;

import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;

public class ConfigurationDbmsTest {
    

    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigurationDbmsTest.class); 
    }
    Mockery validatorContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    States test = validatorContext.states("test").startsAs("pass");
    
    ConfigurationValidator validator;
    Configuration conf = new Configuration();
    
    @Before
    public void setUp() throws Exception {
        DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
        lDocBuilderFact.setNamespaceAware(true);
        DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
        final Document document = lBuilder.parse(new File("tests/config/XML/nextVersion2.xml"));
        
        validator = validatorContext.mock(ConfigurationValidator.class);
        
        validatorContext.checking(new Expectations() {{
            one (validator).loadAndValidate(with(any(File.class))); will(returnValue(document));
            one (validator).getVersion(); will(returnValue(DocumentVersion.V20)); when(test.is("pass"));
        }});
    }

    @After
    public void tearDown() throws Exception {
    }

    @Test
    public void testInitialize() throws SDBExecutionException, SDBValidationException, Exception {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.DBMS, validator);
        validatorContext.assertIsSatisfied();
        Assert.assertTrue(DbOptions.LOCALE.getValue().toLowerCase().contains("library.dll"));
        Assert.assertTrue(DbOptions.BLOCK_SIZE.getValue().contains("2048"));
        Assert.assertTrue(DbOptions.CLUSTER_SIZE.getValue().contains("2048"));
    }

    @Test
    public void testInitializeFail() throws SDBExecutionException, SDBValidationException, Exception {
        test.become("testfail");
        
        DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
        lDocBuilderFact.setNamespaceAware(true);
        DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
        final Document document = lBuilder.parse(new File("tests/config/XML/sec.xml"));
 
        final ConfigurationValidator validator2 = validatorContext.mock(ConfigurationValidator.class, "newstate");
        
        validatorContext.checking(new Expectations() {{
            one (validator2).loadAndValidate(with(any(File.class))); will(returnValue(document));
            one (validator2).getVersion(); will(returnValue(DocumentVersion.V10));
        }});
        
        boolean result = conf.initialize(new File("tests/config/XML/sec.xml"), DBType.DBMS, validator2);
        Assert.assertFalse(result);
        
        test.become("pass");
    }
    
    @Test
    public void testGetPragmaStm() throws SDBExecutionException, SDBValidationException {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.DBMS, validator);
        List<String> list = conf.getPragmaStm(DBType.DBMS);
        Assert.assertNotNull(list);
        Assert.assertTrue(list.size() == 0);
    }

    @Test
    public void testGetConnectionString() throws SDBExecutionException, SDBValidationException {
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.DBMS, validator);
        String string = conf.getConnectionString(DBType.DBMS);
        Assert.assertNotNull(string);
        Assert.assertEquals(
                DbOptions.BLOCK_SIZE.getValue() 
                + "&" 
                + DbOptions.CLUSTER_SIZE.getValue() 
                + "&" 
                + DbOptions.LOCALE.getValue()
                , string);

    }
    
    @Test
    public void testApplySecurity() throws SDBExecutionException, SDBValidationException {
        Mockery platsecContext = new Mockery() {{
            setImposteriser(ClassImposteriser.INSTANCE);
        }};
        
        final PlatsecConfigurator platsec = platsecContext.mock(PlatsecConfigurator.class);

        platsecContext.checking(new Expectations() {{
            never (platsec).applySecuritySettings(with(any(SecuritySettings.class)));
        }});
        conf.initialize(new File("tests/config/XML/nextVersion2.xml"), DBType.DBMS, validator);
        conf.applySecurity(DBType.DBMS, platsec);
    }

}
