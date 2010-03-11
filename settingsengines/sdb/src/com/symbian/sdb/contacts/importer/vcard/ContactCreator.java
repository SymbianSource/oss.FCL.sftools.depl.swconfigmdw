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

package com.symbian.sdb.contacts.importer.vcard;

import java.util.List;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.model.ContactFieldType;
import com.symbian.sdb.contacts.model.ContactImpl;
import com.symbian.sdb.contacts.model.EmailAddress;
import com.symbian.sdb.contacts.model.PhoneNumber;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.ContactsUidMap;
import com.symbian.sdb.contacts.template.IField;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.MultipleTemplateValueException;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactCreator {

    private ITemplateModel templateModel;
    private IVCardContactProperties contactProperties;
    private SpeedDialManager speedDialManager;
    
    public ContactCreator(ITemplateModel templateModel, SpeedDialManager speedDialManager) {
        super();
        this.templateModel = templateModel;
        this.speedDialManager = speedDialManager;
    }

    /**
     * Create contact based from given properties (with values) - only supported properties are used 
     * 
     * @param contactProperties
     */
    public ContactImpl createContactWithProperties(IVCardContactProperties contactProperties)  {
    	this.contactProperties = contactProperties;
    	return createContactFromProperties();
    }

	// TODO KZ: fix it
    public static PropertyData getPropertyData(IProperty property) {
		PropertyData propertyData = PropertyData.newInstance(property);
		
		// TODO KZ: temporary solution
		removeExtendedMappingsForPhoto(propertyData);
		
		return propertyData;
	}

	private ContactImpl createContactFromProperties() {
		ContactImpl contact = new ContactImpl();
		
		for (SimpleProperty property : this.contactProperties.getSimpleProperties()) {
			PropertyData propertyData = getPropertyData(property);
			readSimpleProperty(contact, propertyData, property);
		}

		for (ListProperty property : this.contactProperties.getListProperties()) {
			PropertyData propertyData = getPropertyData(property);
			readListProperty(contact, propertyData, property);
		}
		
		for (StructuredProperty property : this.contactProperties.getStructuredProperties()) {
			PropertyData propertyData = getPropertyData(property);
			readStructuredProperty(contact, propertyData, property);
		}

    	return contact;
	}
    
    private void readSimpleProperty(ContactImpl contact, PropertyData propertyData, SimpleProperty property)  {
        byte[] fieldValue = property.getValue();
        addFieldToContact(contact, propertyData, fieldValue);	
    }

	/**
	 * For photo data like JPEG, BASE64 etc. shouldn't be propagated i.e. matched with template fields
	 * 
	 * @param propertyData
	 * @return
	 */
	private static void removeExtendedMappingsForPhoto(PropertyData propertyData) {
		if (PropertyUtil.isPhoto(propertyData.getName()))    {
        	propertyData.getParameters().clear();
        }
	}

    private void addFieldToContact(ContactImpl contact, PropertyData propertyData, byte[] fieldValue) {
        
        if (propertyData.getName().equals(ContactFieldType.TEL)) {
            PhoneNumber phoneNumber = new PhoneNumber(fieldValue, getTemplateField(propertyData));
            contact.addPhoneNumber(phoneNumber);
            return;
        }
        if (propertyData.getName().equals(ContactFieldType.EMAIL)) {
            EmailAddress emailAddress = new EmailAddress(fieldValue, getTemplateField(propertyData));
            contact.addEmailAddress(emailAddress);
            return;
        }
        ContactField contactField;
		
		contactField = new ContactField(fieldValue, getTemplateField(propertyData));
		contact.addField(contactField);
        
    }

    private IField getTemplateField(PropertyData propertyData) {
    	return getTemplateField(propertyData, 0);
    }
    
    private IField getTemplateField(PropertyData propertyData, int fieldID) {
        try {
            return templateModel.vCardMappingPropertyToContactField(propertyData,fieldID);
        } catch (MultipleTemplateValueException e) {
            throw new SystemException(e);
        } catch (MappingMissingException e) {
        	throw new SystemException(e);
		}
    }
    
    private List<IField> getTemplateFields(PropertyData propertyData) {
        try {
            return templateModel.vCardMappingPropertyToContactFields(propertyData);
        } catch (MultipleTemplateValueException e) {
            throw new SystemException(e);
        } catch (MappingMissingException e) {
            throw new SystemException(e);
		}
    }
    
    private void readListProperty (ContactImpl contact, PropertyData propertyData, ListProperty listProperty) {
    	byte[] fieldValue = listProperty.getValue();
    	addFieldToContact(contact, propertyData, fieldValue);
	}
    
    private void readStructuredProperty(ContactImpl contact, PropertyData propertyData, StructuredProperty structuredProperty)  {
        
        if (structuredProperty.getName().equals("N"))   {
        	List<IField> fields = getTemplateFields(propertyData);
        	
        	String lastName = structuredProperty.getItemValue(1);
            ContactField contactField = createField(fields, lastName, StructurecFieldTemplateFieldIDs.LAST_NAME.getValue());
            if (contactField != null) contact.setLastName(contactField);

            String firstName = structuredProperty.getItemValue(2);
            contactField = createField(fields, firstName, StructurecFieldTemplateFieldIDs.FIRST_NAME.getValue());
            if (contactField != null) contact.setFirstName(contactField);
            
            String additionalName = structuredProperty.getItemValue(3);
            contactField = createField(fields, additionalName, StructurecFieldTemplateFieldIDs.ADDITIONAL_NAME.getValue());
            if (contactField != null) contact.addField(contactField);
            
            String prefix = structuredProperty.getItemValue(4);
            contactField = createField(fields, prefix, StructurecFieldTemplateFieldIDs.NAME_PREFIX.getValue());
            if (contactField != null) contact.addField(contactField);
            
            String suffix = structuredProperty.getItemValue(5);
            contactField = createField(fields, suffix, StructurecFieldTemplateFieldIDs.NAME_SUFFIX.getValue());
            if (contactField != null) contact.addField(contactField);

        }
        else if (structuredProperty.getName().equals("GEO"))    {
        	String geo = structuredProperty.getItemValue(1) + "; " + structuredProperty.getItemValue(2); 
            
        	// GEO is treated as a single string
        	ContactField contactField = ContactField.newTextFieldInstance(geo, getTemplateField(propertyData));
        	contact.addField(contactField);
        }
        else if (structuredProperty.getName().equals("ADR"))    {
        	// see http://www.rfc-ref.org/RFC-TEXTS/2426/chapter3.html
        	for (int i = 0; i <= 6; i++) {
        		contact.addField(ContactField.newTextFieldInstance(structuredProperty.getItemValue(i), getTemplateField(propertyData, i+1)));
        	}
        }
        else if (structuredProperty.getName().equals("ORG"))    {
        	ContactField contactField = ContactField.newTextFieldInstance(structuredProperty.getItemValuesAsString(), getTemplateField(propertyData));
        	contact.setCompanyName(contactField);
        }
        else {
        	throw new ContactsExeption(structuredProperty.getName() + " Not Implemented!!!");
        }
    }

	/**
	 * @param fields
	 * @param fieldValue
	 * @param fieldType 
	 * @return
	 */
	private ContactField createField(List<IField> fields, String fieldValue, String fieldType) {
		ContactField contactField; 
			try	{
				contactField = ContactField.newTextFieldInstance(fieldValue, getFieldWith(fields, fieldType));
			}
			catch (FieldNotFoundException e) {
				contactField = null;
			}
		return contactField;
	}

	/**
	 * @param fields
	 * @param string
	 * @return
	 */
	private IField getFieldWith(List<IField> fields, String fieldKUid) {
		for (IField field : fields) {
			if (isTheSameType(fieldKUid, field))	{
				return field;
			}
		}
		throw new FieldNotFoundException("Field not found. Filed type: " + fieldKUid);
	}

	/**
	 * Check if two KUIDs are the same, take into account any aliases defined in contacts.xml file.
	 * 
	 * @param fieldKUid
	 * @param field
	 * @return
	 */
	private boolean isTheSameType(String fieldKUid, IField field) {
		if (field.getFieldType().equals(fieldKUid))	{
			return true;
		}
		else	{
			// check if field type matches fieldKUid 
			ContactsUidMap contactsUidMap = templateModel.getMapper().getUidMap();
			if (field.getFieldType().equals(contactsUidMap.map(fieldKUid)))	{
				return true;
			}
		}
		return false;
	}
}
