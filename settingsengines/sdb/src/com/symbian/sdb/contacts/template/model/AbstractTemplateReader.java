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



package com.symbian.sdb.contacts.template.model;

import java.util.Map;

import org.apache.log4j.Logger;

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.model.TemplateHint;
import com.symbian.sdb.contacts.template.ContactFlagTypes;
import com.symbian.sdb.contacts.template.ContactMapTypes;
import com.symbian.sdb.contacts.template.Field;
import com.symbian.sdb.contacts.template.FieldContainer;
import com.symbian.sdb.contacts.template.Flag;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.exception.TemplateParsingException;

public abstract class AbstractTemplateReader implements TemplateReader {
	protected static final Logger logger = Logger.getLogger(AbstractTemplateReader.class);
	protected Map<Integer, String> idToTypeMap;
	protected Map<Integer, String> idTovCardMap;
	protected Map<String, String> labelToUIDMap;

	public abstract ITemplateModel readTemplate(long templateId)
			throws TemplateParsingException;

	protected TemplateMapper initialiseMapping() throws MappingMissingException {
		TemplateMapper mapper = TemplateMapper.getInstance();
		labelToUIDMap = mapper.getUidValueToLabelMap();
		idTovCardMap = mapper.getReversedMapping(ContactMapTypes.vcard_mapping);
		idToTypeMap = mapper
				.getReversedMapping(ContactMapTypes.field_type_mapping);
		return mapper;
	}

	protected FieldContainer initialiseFieldContainer(TemplateMapper mapper) {
		FieldContainer fieldContainer = new FieldContainer();
		fieldContainer.setMapper(mapper);
		return fieldContainer;
	}

	protected Field createField(HeaderTemplateField headerField)
			throws MappingMissingException {
		Field field = new Field();

		field.setStorageType((int) headerField.getAttributesContainer()
				.getFieldStorageType());

		field.setFieldName(getLabel(headerField.getFieldLabel()));

		String vcard = idTovCardMap.get(headerField.getFieldVcardMapping());
		field.setVCardMapping(vcard);

		if (headerField.getFieldAdditionalUIDValues() != null) {
			for (Integer value : headerField.getFieldAdditionalUIDValues()) {
				translateUidValue(field, value);
			}
		}

		field.setIndex((int)headerField.getFieldId());

		field.setCategory(headerField.getAttributesContainer().getCategory());

		return field;
	}
	
    protected void translateHintFieldToFieldType(Field field, HeaderTemplateField headerField, TemplateHint[] hints) {
    	long hint = headerField.getFieldHintValue();
    	for (TemplateHint templateHint : hints) {
    		if (hint == templateHint.getValue()) {
    			setFieldType(templateHint.getUid(), field);
    			break;
    		}					 
    	}
    }

	protected String getLabel(ContactFieldLabel contactLabel)
			throws MappingMissingException {
		if (labelToUIDMap.containsKey(new String(contactLabel.getLabel()))) {
			String label = labelToUIDMap
					.get(new String(contactLabel.getLabel()));
			return label;
		} else {
			logger.warn("Mapping missing for label " + contactLabel.getLabel());
			return new String(contactLabel.getLabel());
		}
	}
	
	/**
	 * maps the integer value either to property uid or field type uid 
	 * this is because in the addition hint values array the value can indicate either one of them
	 * without obvious declaration which one is this
	 * @param field field that will have the new value set
	 * @param uidValue integer value mapped to either vCard property or field type uid
	 * @throws MappingMissingException
	 */
	protected void translateUidValue(Field field, Integer uidValue)
	throws MappingMissingException {
		String property = idTovCardMap.get(uidValue);
		if (property != null) {
			field.addProperty(property);
		} else {
			property = idToTypeMap.get(uidValue);
			if (property != null) {
				setFieldType(property, field);
			} else {
				throw new MappingMissingException("missing mapping for 0x" + Integer.toHexString(uidValue).toUpperCase());
			}
		}
	}
	
	/**
	 * to make sure field.setFieldType is called only once
	 * @param fieldTypeUid
	 * @param field
	 */
	protected void setFieldType( String fieldTypeUid, Field field ) {
		if (field.getFieldType() == null) {
			field.setFieldType(fieldTypeUid);
		} else {
			logger.warn("The different value of the field type for field " + field.getFieldType() + " ignored.");
		}
	}
	
	protected void resolveFlags(TemplateMapper mapper,
			HeaderTemplateField headerfield, 
			Field field)
			throws MappingMissingException {
		 Map<String, Long> flagMap = mapper.getMappingToLong(ContactMapTypes.flags.toString());
		 
		 long attributes = headerfield.getAttributesContainer().getAttributes();

		 
		 for (ContactFlagTypes type : ContactFlagTypes.attrValues()) {
			 long attrValue = flagMap.get(type.toString());
			 if ((attributes & attrValue) == attrValue) {
				 Flag flag = new Flag(type.toString(), (int)attrValue);
				 field.addFlag(flag);
			 }
		 }
		 
		 long extAttributes = headerfield.getAttributesContainer().getExtendedAttributes();
		 
		 for (ContactFlagTypes type : ContactFlagTypes.extAttrValues()) {
			 long attrValue = flagMap.get(type.toString());
			 if ((extAttributes & attrValue) == attrValue) {
				 Flag flag = new Flag(type.toString(), (int)attrValue);
				 field.addFlag(flag);
			 }
		 } 
	}
}
