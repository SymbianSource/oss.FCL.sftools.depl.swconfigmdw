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

import static org.junit.Assert.fail;

import java.io.File;
import java.io.IOException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.validation.Schema;

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;

import com.symbian.sdb.exception.SDBValidationException;

public class ConfigValidatorTest {
    ConfigurationValidator validator;

    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfigValidatorTest.class); 
    }
    
    @Before
    public void setUp() throws Exception {
        System.setProperty("sdb.schema.location.1.0", "tests//config//XML//sdb.xsd");
    }

    @Test
    public void testLoadDocument() throws SAXException, IOException, ParserConfigurationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        Document document = validator.manager.loadDocument(new File("tests//config//XML//sec.xml"));
        Assert.assertNotNull(document);
    }

    @Test(expected=IOException.class)
    public void testLoadFailNonExistingFile() throws SAXException, IOException, ParserConfigurationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        validator.manager.loadDocument(new File("idontexist"));
    }
        
    @Test
    public void testGetVersion()  {   
        try {
            ConfigurationValidator validator = new ConfigurationValidator();
            DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
            lDocBuilderFact.setNamespaceAware(true);
            DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
            Document document = lBuilder.parse(new File("tests/config/XML/sec.xml"));
            String version = validator.getVersion(document);
            Assert.assertEquals("1.0", version);

            Document document2 = lBuilder.parse(new File("tests/config/XML/nextVersion.xml"));
            validator = new ConfigurationValidator();
            String version2 = validator.getVersion(document2);
            Assert.assertEquals("2.0", version2);
        } catch (Exception e) {
            fail("shouldn't get here " + e.getMessage());
        }
    }

    @Test
    public void testNoVersion()  {   
        try {
            ConfigurationValidator validator = new ConfigurationValidator();
            validator.loadAndValidate(new File("tests/config/XML/secNoVersion.xml"));
            DocumentVersion version = validator.getVersion();
            Assert.assertEquals(DocumentVersion.V10, version);
        } catch (Exception e) {
            fail("shouldn't get here " + e.getMessage());
        }
    }
    

    @Test(expected=SDBValidationException.class)
    public void testBadVersion() throws SDBValidationException {   
            ConfigurationValidator validator = new ConfigurationValidator();
            validator.loadAndValidate(new File("tests/config/XML/secBadVersion.xml"));
    }
    
    @Test
    public void testLoadSchema() throws SAXException {
        ConfigurationValidator validator = new ConfigurationValidator();
        Schema schema = validator.manager.loadSchema(System.getProperty("sdb.schema.location.1.0"));
        Assert.assertNotNull(schema);
    }

    @Test
    public void testValidatePass() throws SDBValidationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        File fTestXmlFile = new File("tests//config//XML//sec.xml");
        validator.loadAndValidate(fTestXmlFile);
    }
    
    @Test
    public void testValidatePassVersion2() throws SDBValidationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        System.setProperty("sdb.schema.location.2.0", "sdb2.0.xsd");
        File fTestXmlFile = new File("tests//config//XML//nextVersion.xml");
        validator.loadAndValidate(fTestXmlFile);
    }

    @Test(expected=SAXException.class)
    public void testValidateFailIncorrectFile() throws SAXException, IOException, ParserConfigurationException {
        ConfigurationValidator validator = new ConfigurationValidator();
        Document document = validator.manager.loadDocument(new File("tests//config//XML//bad.xml"));
        Schema schema = validator.manager.loadSchema(System.getProperty("sdb.schema.location.1.0"));
        validator.manager.validate(document, schema);
    }
}
