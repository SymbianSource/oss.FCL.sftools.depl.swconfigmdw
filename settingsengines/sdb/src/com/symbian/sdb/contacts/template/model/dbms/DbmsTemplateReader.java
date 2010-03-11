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

package com.symbian.sdb.contacts.template.model.dbms;

import java.util.List;

import com.symbian.sdb.contacts.dbms.ContactDaoDBMS;
import com.symbian.sdb.contacts.dbms.model.AbstractContactHeader;
import com.symbian.sdb.contacts.dbms.model.ContactFieldHeader;
import com.symbian.sdb.contacts.dbms.model.ContactHeaderForTemplate;
import com.symbian.sdb.contacts.model.TemplateHint;
import com.symbian.sdb.contacts.template.Field;
import com.symbian.sdb.contacts.template.FieldContainer;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.contacts.template.TemplateModel;
import com.symbian.sdb.contacts.template.model.AbstractTemplateReader;
import com.symbian.sdb.exception.TemplateParsingException;

public class DbmsTemplateReader extends AbstractTemplateReader {
	
	private ContactDaoDBMS contactDao;

    public ITemplateModel readTemplate(long templateId) throws TemplateParsingException {
        ITemplateModel model = null;

		try {
	        TemplateMapper mapper = initialiseMapping();
	        FieldContainer fieldContainer = initialiseFieldContainer(mapper);
			
			 byte[] header = contactDao.readContactHeader(templateId);
			 
			 if (header == null) {
				 throw new TemplateParsingException("Template with id " + templateId + " missing from the database");
			 }
			 
			 AbstractContactHeader cm_header = new ContactHeaderForTemplate(header);
			 List<ContactFieldHeader> templateHeaderFields = cm_header.getFieldHeaderList();
			 TemplateHint[] hintValues = TemplateHint.dbmsTemplateValues();
			 
			 for (ContactFieldHeader headerField : templateHeaderFields) {
				 Field field = createField(headerField);		
				 field.setMapping(fieldContainer);
				 resolveFlags(mapper, headerField, field);
				 translateHintFieldToFieldType(field, headerField, hintValues);	 
				 fieldContainer.add(field.getVCardMapping(), field); 
			 }
			 
			 model = new TemplateModel(mapper, fieldContainer);
			 model.setTemplateId(templateId);
		} catch (Exception e) {
			throw new TemplateParsingException("Error while parsing database template: " + e.getMessage(), e);
		}
		return model;
    }

	// Setters and getters
	
	public void setContactDao(ContactDaoDBMS contactDao) {
		this.contactDao = contactDao;
	}

}
