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

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.w3c.dom.Document;

import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.util.NodeWrapper;

public class ConfigurationParserTest {

    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigurationParserTest.class); 
    }
    
    @Before
    public void setUp() {
        System.setProperty("sdb.schema.location.1.0", "tests//config//XML//sdb.xsd");
        System.setProperty("sdb.schema.location.2.0", "sdb2.0.xsd");
    }

    @Test
    public void testSqlitePass() throws SDBValidationException {
      
        ConfigurationValidator validator = new ConfigurationValidator();
        Document document = validator.loadAndValidate(new File("tests//config//XML//nextVersion.xml"));

        ConfigurationParser parser = new ConfigurationParser(DBType.SQLITE, validator.getVersion());
        
        NodeWrapper nodes = parser.getConfigurationNodes(document);
        NodeWrapper nodes2 = parser.getPoliciesNodes(document);
        Assert.assertTrue(nodes.getSize() == 3);
        Assert.assertTrue(nodes2.getSize() == 3);
    }
    
    @Test
    public void testDBMSPass() throws SDBValidationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        Document document = validator.loadAndValidate(new File("tests//config//XML//nextVersion.xml"));

        ConfigurationParser parser = new ConfigurationParser(DBType.DBMS, validator.getVersion());
        
        NodeWrapper nodes = parser.getConfigurationNodes(document);
        NodeWrapper nodes2 = parser.getPoliciesNodes(document);
        Assert.assertTrue(nodes.getSize() == 4);
        Assert.assertTrue(nodes2.getSize() == 1);
    }
}
