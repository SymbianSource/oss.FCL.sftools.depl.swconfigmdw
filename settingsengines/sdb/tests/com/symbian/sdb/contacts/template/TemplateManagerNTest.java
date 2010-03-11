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

import java.util.Map;

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.exception.SDBExecutionException;

public class TemplateManagerNTest {

    public static junit.framework.Test suite() {
        return new JUnit4TestAdapter(TemplateManagerNTest.class);
    }

    @BeforeClass
    public static void setUpBeforeClass() {
        System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
    }

    ITemplateModel templateModel = null;

    @Before
    public void setUp() throws SDBExecutionException, Exception {
        ITemplateManager manager = new TemplateManager();
        templateModel = manager.parse("tests/config/cntmodel_n.rss");
    }

    @Test
    public void testGetVCardMappingPropertyToContactFieldType() throws MultipleTemplateValueException,
            MappingMissingException {
        PropertyData data = new PropertyData("NOTE", new String[0]);
        Integer result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertNotNull(result);
        Assert.assertEquals("1000401c", Integer.toHexString(result));

        data = new PropertyData("FN", new String[0]);
        result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertNull(result);

        String[] propertyParameters = new String[2];
        propertyParameters[0] = "VOICE";
        propertyParameters[1] = "HOME";
        data = new PropertyData("TEL", propertyParameters);
        result = templateModel.getVCardMappingPropertyToContactFieldType(data);
        Assert.assertEquals("1000130e", Integer.toHexString(result));

   //     data = new PropertyData("PHOTO", new String[0]);
   //     result = templateModel.getVCardMappingPropertyToContactFieldType(data);
   //     Assert.assertEquals("10005dd1", Integer.toHexString(result));
    }

    @Test
    public void testGetVCardMappingPropertyToContactSetIndexFieldType() throws MappingMissingException {
        String[] propertyParameters = new String[2];
        propertyParameters[0] = "HOME";
        propertyParameters[1] = "VOICE";
        PropertyData data = new PropertyData("TEL", propertyParameters);
        Map<Integer, Integer> result = templateModel.getvCardMappingPropertyToFieldIndexTypeSet(data);
        Assert.assertEquals(2, result.keySet().iterator().next());
    }

    @Test
    public void testGetVCardMappingPropertyToStorageFieldType() throws MultipleTemplateValueException,
            MappingMissingException {
        PropertyData data = new PropertyData("BDAY", new String[0]);
        Integer result = templateModel.getVCardMappingPropertyToStorageFieldType(data);
    //    Assert.assertEquals(3, result);

        data = new PropertyData("NOTE", new String[0]);
        result = templateModel.getVCardMappingPropertyToStorageFieldType(data);
        Assert.assertEquals(0, result);
    }

    @Test
    public void testGetVCardMappingPropertyToFieldName() throws MultipleTemplateValueException, MappingMissingException {
        PropertyData data = new PropertyData("BDAY", new String[0]);
        String result = templateModel.getVCardMappingPropertyToFieldName(data);
        Assert.assertNotNull(result);
    }

    @Test
    public void testGetVCardMappingPropertyToIndex() throws MultipleTemplateValueException, MappingMissingException {
        String[] propertyParameters = new String[2];
        propertyParameters[0] = "HOME";
        propertyParameters[1] = "VOICE";
        PropertyData data = new PropertyData("TEL", propertyParameters);
        int result = templateModel.getvCardMappingPropertyToFieldIndex(data);
        Assert.assertEquals(2, result);
    }

    @Test(expected = MappingMissingException.class)
    public void test() throws MultipleTemplateValueException, MappingMissingException {
        PropertyData data = new PropertyData("xxx", new String[0]);
        boolean res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertFalse(res);
    }

    @Test
    public void testTemplateContainsMappingForVCardProperty() throws MultipleTemplateValueException,
            MappingMissingException {
        PropertyData data = new PropertyData("NOTE", new String[0]);
        boolean res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);

        data = new PropertyData("FN", new String[0]);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertFalse(res);

        String[] propertyParameters = new String[3];
        propertyParameters[2] = "CELL";
        propertyParameters[1] = "WORK";
        propertyParameters[0] = "VOICE";
        data = new PropertyData("TEL", propertyParameters);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertFalse(res);

        propertyParameters = new String[2];
        propertyParameters[1] = "WORK";
        propertyParameters[0] = "VOICE";
        data = new PropertyData("TEL", propertyParameters);
        res = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertTrue(res);
    }

    @Test(expected = MultipleTemplateValueException.class)
    public void testGetVCardMappingPropertyToContactFieldType2() throws SDBExecutionException,
            MultipleTemplateValueException, MappingMissingException {
        PropertyData data = new PropertyData("N", new String[0]);
        templateModel.getVCardMappingPropertyToContactFieldType(data);
    }

    @Test(expected = MappingMissingException.class)
    public void testNoMapping() throws MultipleTemplateValueException, MappingMissingException {
        String[] propertyParameters = new String[1];
        propertyParameters[0] = "xxx";
        PropertyData data = new PropertyData("NOTE", propertyParameters);
        boolean result2 = templateModel.templateContainsMappingForVCardProperty(data);
        Assert.assertFalse(result2);
    }

}
