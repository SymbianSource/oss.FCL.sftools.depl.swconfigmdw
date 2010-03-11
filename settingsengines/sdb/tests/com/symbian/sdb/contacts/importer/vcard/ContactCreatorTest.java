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
// ContactCreator.java
//



package com.symbian.sdb.contacts.importer.vcard;

import java.util.HashSet;
import java.util.Set;

import org.jmock.Mock;
import org.jmock.cglib.MockObjectTestCase;

import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.model.ContactImpl;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.Field;
import com.symbian.sdb.contacts.template.ITemplateModel;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactCreatorTest extends MockObjectTestCase	{
	
	private Mock parametersMock;
	
	public void testImportPhoto() throws Exception {
        Mock templateModelMock = mock(ITemplateModel.class);
        Mock speedDialManagerMock = mock(SpeedDialManager.class);

        ContactCreator contactCreator = new ContactCreator((ITemplateModel) templateModelMock.proxy(),(SpeedDialManager)speedDialManagerMock.proxy());
        
        Field field = new Field();
        field.setIndex(47);
        templateModelMock.expects(once()).method("vCardMappingPropertyToContactField").withAnyArguments().will(returnValue(field));
        
        parametersMock = mock(IParameters.class);
        Set<String> values = new HashSet<String>();
        values.add("PHOTO");
        parametersMock.expects(atLeastOnce()).method("getValuesForTypeParameter").withAnyArguments().will(returnValue(values));
        
        IVCardContactProperties contactProperties = new VCardContactProperties();
        contactProperties.addSimpleProperty(new PhotoPropertyMock());
        ContactImpl contact = contactCreator.createContactWithProperties(contactProperties);
        
        ContactField contactField = contact.getFields().iterator().next();
        
        assertEquals("1234", contactField.getTextValue());
        assertEquals(47, contactField.getTemplateFieldId());
        
	}
	
	class PhotoPropertyMock extends PhotoProperty	{

		
		public PhotoPropertyMock() {
			super(null);
		}

		@Override
		public byte[] getValue() {
			return "1234".getBytes();
		}

		@Override
		public String getName() {
			return "PHOTO";
		}

		@Override
		public IParameters getParameters() {
			return (IParameters)parametersMock.proxy();
		}
		
	}
}
