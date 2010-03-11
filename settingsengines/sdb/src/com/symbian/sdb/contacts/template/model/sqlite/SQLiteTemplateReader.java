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

package com.symbian.sdb.contacts.template.model.sqlite;

import com.symbian.sdb.contacts.model.TemplateHint;
import com.symbian.sdb.contacts.sqlite.ContactDaoSQLite;
import com.symbian.sdb.contacts.sqlite.model.AbstractSQLiteContact;
import com.symbian.sdb.contacts.sqlite.model.FieldHeader;
import com.symbian.sdb.contacts.sqlite.model.FieldsHeaderReader;
import com.symbian.sdb.contacts.template.Field;
import com.symbian.sdb.contacts.template.FieldContainer;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.contacts.template.TemplateModel;
import com.symbian.sdb.contacts.template.model.AbstractTemplateReader;
import com.symbian.sdb.exception.TemplateParsingException;

public class SQLiteTemplateReader extends AbstractTemplateReader {
	
	private ContactDaoSQLite contactDao;
	
    public ITemplateModel readTemplate(long templateId) throws TemplateParsingException {
        ITemplateModel model = null;
        AbstractSQLiteContact contact = new TemplateSqliteContact();
		
		try {
	        TemplateMapper mapper = initialiseMapping();
	        FieldContainer fieldContainer = initialiseFieldContainer(mapper);
		
			contact = contactDao.getContactFromDatabase(contact, (int)templateId);
			
			if (contact == null) {
				 throw new TemplateParsingException("Template with id " + templateId + " missing from the database");
			}
			
			byte[] textHeader = contact.getTextFieldsHeader();
			byte[] binaryHeader = contact.getBinaryFieldsHeader();
		
			FieldHeader[] textHeaders = FieldsHeaderReader.read(textHeader);
			FieldHeader[] binaryHeaders = FieldsHeaderReader.read(binaryHeader);
			
			TemplateHint[] hintValues = TemplateHint.sqliteTemplateValues();
			
			for (FieldHeader textFieldHeader : textHeaders) {
				transformFieldHeaderToField(mapper, fieldContainer, hintValues,
						textFieldHeader); 
			}
			
			for (FieldHeader binaryFieldHeader : binaryHeaders) {
				transformFieldHeaderToField(mapper, fieldContainer, hintValues,
						binaryFieldHeader); 
			}
			
			model = new TemplateModel(mapper, fieldContainer);
			model.setTemplateId(templateId);
		} catch (Exception e) {
			throw new TemplateParsingException("Error while parsing database template: " + e.getMessage(), e);
		}
		
		return model;
	}

	private void transformFieldHeaderToField(TemplateMapper mapper,
			FieldContainer fieldContainer, TemplateHint[] hintValues,
			FieldHeader binaryFieldHeader) throws MappingMissingException {
		Field field = createField(binaryFieldHeader);
		field.setMapping(fieldContainer);
		resolveFlags(mapper, binaryFieldHeader, field);
		translateHintFieldToFieldType(field, binaryFieldHeader, hintValues);
		fieldContainer.add(field.getVCardMapping(), field);
	}

    // Setters and getters
    
	public void setContactDao(ContactDaoSQLite contactDao) {
		this.contactDao = contactDao;
	}

}
