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

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.Test;
import org.w3c.dom.Document;

import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;

public class ConfigurationSqlite1Test {
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigurationSqlite1Test.class); 
    }
    
    private Mockery validatorContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    
    private Mockery platsecContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    private ConfigurationValidator validator;
    private Configuration conf = new Configuration();


    private PlatsecConfigurator platsec;

    @Test
    public void testApplySecurityNone() throws SDBExecutionException, SDBValidationException, Exception {
        DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
        lDocBuilderFact.setNamespaceAware(true);
        DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
        final Document document = lBuilder.parse(new File("tests/config/XML/nextVersion3.xml"));
        
        validator = validatorContext.mock(ConfigurationValidator.class);
        
        validatorContext.checking(new Expectations() {{
            one (validator).loadAndValidate(with(any(File.class))); will(returnValue(document));
            one (validator).getVersion(); will(returnValue(DocumentVersion.V20));
        }});
        
        platsec = platsecContext.mock(PlatsecConfigurator.class);
        platsecContext.checking(new Expectations() {{
            never (platsec).applySecuritySettings(with(any(SecuritySettings.class)));
        }});
        
        conf.initialize(new File("tests/config/XML/nextVersion3.xml"), DBType.SQLITE, validator);
        conf.applySecurity(DBType.SQLITE, platsec);
    }

  

}
