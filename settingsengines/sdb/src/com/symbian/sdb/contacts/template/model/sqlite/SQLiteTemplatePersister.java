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

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

import org.apache.log4j.Logger;

import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Multimap;
import com.symbian.sdb.contacts.dbms.model.TemplateHintField;
import com.symbian.sdb.contacts.sqlite.ContactDaoSQLite;
import com.symbian.sdb.contacts.sqlite.model.AbstractSQLiteContact;
import com.symbian.sdb.contacts.sqlite.model.ContactFieldAttribute;
import com.symbian.sdb.contacts.sqlite.model.ContactType;
import com.symbian.sdb.contacts.sqlite.model.FieldHeader;
import com.symbian.sdb.contacts.sqlite.model.FieldsHeaderWriter;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactAttribute;
import com.symbian.sdb.contacts.sqlite.model.TypeFlags;
import com.symbian.sdb.contacts.template.Flag;
import com.symbian.sdb.contacts.template.IField;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.model.TemplatePersister;
import com.symbian.sdb.util.SymbianSpecificUtils;

public class SQLiteTemplatePersister implements TemplatePersister {
	
	private static final Logger logger = Logger.getLogger(SQLiteTemplatePersister.class);
	
	private ContactDaoSQLite contactDao;
	
	public void persistTemplate(ITemplateModel template) {
		AbstractSQLiteContact sqliteTemplate = transformTemplate(template);
		saveTemplateInDB(sqliteTemplate);
		template.setTemplateId(sqliteTemplate.getContactId());
	}

    private void saveTemplateInDB(AbstractSQLiteContact templateCard) {
        contactDao.saveContact(templateCard);
		logger.info("SQLite template persisted in database");
    }
	
    private AbstractSQLiteContact transformTemplate(ITemplateModel template) {
    	AbstractSQLiteContact sqliteTemplate = new TemplateSqliteContact();
    	
    	//set flags - template and compressed guid
        TypeFlags typeFlags = new TypeFlags(ContactType.TEMPLATE);
        typeFlags.setContactAttributes(SQLiteContactAttribute.COMPRESSED_GUID);
        sqliteTemplate.setTypeFlags(typeFlags);

        //set creation and modification dates
        long currentDate = new Date().getTime();
        sqliteTemplate.setCreationDate(currentDate);
        sqliteTemplate.setLastModification(currentDate);

        //set guid
		long currentSymbianTimestamp = SymbianSpecificUtils.createCurrentSymbianTimestamp();
		sqliteTemplate.setGuidString(Long.toHexString(currentSymbianTimestamp));
		
       // sqliteTemplate.setGuidString("00e13325fdc48960");
		Multimap<Integer, String> flagMap = null;
		try {
			flagMap = template.getMapper().getFlagsMapping();
		} catch (MappingMissingException ex) {
			logger.warn(ex.getMessage());
			flagMap = new ArrayListMultimap<Integer, String>();
		}
		
        // TODO KZ: blobs - use fixed values 
        //String textFieldsHeader = "04000000E140200000100000001000000140200000300000003000000140200000500000005000000240200001700000017000000240200001800000018000000240200001A0000001A00000034020002B0000002B000000";
        
		List<FieldHeader> textFieldHeaders = new LinkedList<FieldHeader>();
		List<FieldHeader> binaryFieldHeaders = new LinkedList<FieldHeader>();
		
		for (IField field : template.getFields()) {
			try {
				FieldHeader fieldHeader = transformField(field, flagMap);
				if (field.getStorageType() == 0) {
					textFieldHeaders.add(fieldHeader);
				} else {
					binaryFieldHeaders.add(fieldHeader);
				}
			} catch (MappingMissingException ex) {
				logger.warn(ex.getMessage());
			}		
		}

		byte[] textFieldsHeader = FieldsHeaderWriter.write(textFieldHeaders);
        sqliteTemplate.setTextFieldsHeader(textFieldsHeader);
        byte[] binaryFieldsHeader = FieldsHeaderWriter.write(binaryFieldHeaders);
        sqliteTemplate.setBinaryFieldsHeader(binaryFieldsHeader);
        String textFields = "";
        sqliteTemplate.setTextFields(textFields);
        byte[] binaryFields = {0x00, 0x00, 0x00, 0x00, 0x00};
        sqliteTemplate.setBinaryFields(binaryFields);

        return sqliteTemplate;
    }
    
    private FieldHeader transformField(IField field, Multimap<Integer, String> flagMap) throws MappingMissingException {
    	FieldHeader fieldHeader = new FieldHeader();
    	
    	//set field index
    	fieldHeader.setFieldId(field.getIndex());
    	
    	fieldHeader.setContactFieldGuid(4294967295L);
    	
    	//set attributes
    	
    	fieldHeader.getAttributesContainer().setStorageType(field.getStorageType());
    	fieldHeader.getAttributesContainer().setCategory(field.getCategory());
    	
    	fieldHeader.getAttributesContainer().addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_TEMPLATEMASK);
    	fieldHeader.getAttributesContainer().addAttribute(ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_OVERIDELABEL);

		for(Flag flag : field.getFlags()) {
			
			Collection<String> flaguids = flagMap.get(flag.getValue());
			
			if (flag.getUID().contains("Filterable") && (flaguids.contains("KIntFieldFlagFilterable") ||
					flaguids.contains("KIntFieldFlagFilterable1") ||
					flaguids.contains("KIntFieldFlagFilterable2") ||
					flaguids.contains("KIntFieldFlagFilterable3") ||
					flaguids.contains("KIntFieldFlagFilterable4"))) { 
				fieldHeader.getAttributesContainer().addExtendedAttributes(flag.getValue());
			} else {
				fieldHeader.getAttributesContainer().addAttribute(flag.getValue());
			} 
		}

		//create field hint value 
		TemplateHintField hintField = new TemplateHintField(field.getFieldType());
		
		//set additional contact type uid (if required)
		List<Integer> propertyList = new ArrayList<Integer>(field.getPropertiesValue());
		if (hintField.getValue() == 0 && field.getFieldType() != "KUidContactFieldNoneValue") {
			propertyList.add(0, field.getFieldTypeValue());
		}
		
		fieldHeader.setHintValue(hintField.getValue());
		
		//set additional fields
		fieldHeader.setFieldAdditionalUIDValues(toIntArray(propertyList));
		if (propertyList.size() > 0) {
			fieldHeader.setAdditionalFieldCount(propertyList.size());	
		}
		
		if (field.getStorageType() != 0) {
			fieldHeader.setStreamId(1);
		}
		
		//set vcard mapping
		fieldHeader.setFieldVcardMapping(field.getVCardMappingValue());

		//Set Label
		fieldHeader.getFieldLabel().setLength(field.getFieldNameValue().length());
		fieldHeader.getFieldLabel().setLabel(field.getFieldNameValue());
		
    	return fieldHeader;
    }
    
	private int[] toIntArray(List<Integer> integers) {
		int[] ints = new int[integers.size()];
		int index = 0;
		for (Integer integer : integers) {
			ints[index++] = integer;
		}
		return ints;
	}
	
    //~ Getter/Setters ---------------------------------------------------------
    
	public void setContactDao(ContactDaoSQLite contactDao) {
		this.contactDao = contactDao;
	}
}
