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

package com.symbian.sdb.contacts.dbms.model.creator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.log4j.Logger;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.dbms.model.AbstractContactHeader;
import com.symbian.sdb.contacts.dbms.model.ContactExtHintField;
import com.symbian.sdb.contacts.dbms.model.ContactFieldAttribute;
import com.symbian.sdb.contacts.dbms.model.ContactFieldAttributeFlag;
import com.symbian.sdb.contacts.dbms.model.ContactFieldExtendedAttributeFlag;
import com.symbian.sdb.contacts.dbms.model.ContactFieldHeader;
import com.symbian.sdb.contacts.dbms.model.ContactHeaderForContact;
import com.symbian.sdb.contacts.dbms.model.ContactHintField;
import com.symbian.sdb.contacts.dbms.model.ContactTextBlob;
import com.symbian.sdb.contacts.dbms.model.DBMSContactAttribute;
import com.symbian.sdb.contacts.dbms.model.DBMSContactCard;
import com.symbian.sdb.contacts.dbms.model.IdentityTable;
import com.symbian.sdb.contacts.dbms.model.TemplateHintField;
import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.model.ContactHint;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialUids;
import com.symbian.sdb.contacts.template.ContactMapTypes;
import com.symbian.sdb.contacts.template.IField;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.exception.ContactHeaderCreationException;
import com.symbian.sdb.mode.flow.SpeedDialModeType;
import com.symbian.sdb.util.SymbianSpecificUtils;

/**
 * Class responsible for DBMS specific contacts creation
 * 
 * @author krzysztofZielinski
 *
 */
public class DBMSContactBuilder {

    private DBMSContactCard dbmsContact;
	private static final Logger logger = Logger.getLogger(DBMSContactBuilder.class);
	private SpeedDialManager speedDialManager;
	
	/**
	 * @param speedDialManager
	 */
	public DBMSContactBuilder(SpeedDialManager speedDialManager) {
		super();
		this.speedDialManager = speedDialManager;
	}

	public void createNewContact(Contact genericContact, ITemplateModel templateModel)    {
        dbmsContact = new DBMSContactCard();
        
        if (speedDialManager.getMode().equals(SpeedDialModeType.NONE))	{
        	Set<SpeedDialData> emptySpeedDialDataSet = Collections.emptySet();
        	dbmsContact.setSpeedDialData(emptySpeedDialDataSet);
        }
        else	{
        	dbmsContact.setSpeedDialData(genericContact.getSpeedDialData());
        }
        
        // set the template id
        dbmsContact.setPrefTemplateRefId((int)templateModel.getTemplateId());
        
        setDateBasedFields();

        dbmsContact.setAttributes(DBMSContactAttribute.COMPRESSED_GUID);
        
        dbmsContact.setReplicationCount(0);
        
        handleContactFields(genericContact, templateModel);
        
        // set fields for identityTable
        IdentityTable identityTable = dbmsContact.getIdentityTable();
        
        identityTable.setFirstName(genericContact.getFirstName());
        identityTable.setLastName(genericContact.getLastName());
        identityTable.setCompanyName(genericContact.getCompanyName());
        
        identityTable.setFirstNamePrn(genericContact.getFirstNamePrn());
        identityTable.setLastNamePrn(genericContact.getLastNamePrn());
        identityTable.setCompanyNamePrn(genericContact.getCompanyNamePrn());
        
        identityTable.setAttribute(dbmsContact.getAttributes());
        
        identityTable.setContactHintField(createHintField(genericContact));
        identityTable.setContactExtHintField(createExtHintField(genericContact));
    }

    private void setDateBasedFields() {
        Date currentDateTime = new Date();
        
        dbmsContact.setUIDString(createContactGuid(currentDateTime));
        dbmsContact.setLastModified(currentDateTime);
        dbmsContact.setContactCreationDate(currentDateTime);
    }

    /**
     * Creates symbian contact GUID based on date e.g. "00e1339b8cfaed20" - hex representation of symbian timestamp
     * 
     * @param currentDateTime
     * @return
     */
    private String createContactGuid(Date currentDateTime) {
        long currentSymbianTimestamp = SymbianSpecificUtils.convertToSymbianTimestamp(currentDateTime.getTime());
        
        String hexSymbianTimestamp = Long.toHexString(currentSymbianTimestamp); 

        StringBuffer guid = new StringBuffer();
        
        // add leading zeros if necessary (GUID should be 16 characters long)
        int guidLength = 16;
        for (int i = 0; i < (hexSymbianTimestamp.length() - guidLength); i++) {
            guid.insert(0, '0');    
        }
        guid.append(hexSymbianTimestamp);

        return guid.toString();
    }


    private void handleContactFields(Contact genericContact, ITemplateModel templateModel) {
    	
    	List<ContactFieldHeader> contactFieldHeaders = new ArrayList<ContactFieldHeader>();
    	
    	byte [] data = {0, 0, 0, 0}; 
    	ContactTextBlob binaryTextBlob = new ContactTextBlob(data);
    	
    	StringBuffer textFieldsBuffer = new StringBuffer();

        ContactFieldHeader contactFieldHeader = null;

    	for (ContactField contactField : genericContact.getFields()) {
    		
    		IField templateField = templateModel.getFields().get(contactField.getTemplateFieldId());
    		
    		if (templateField.isAgent() || templateField.isBinary()) {
    			//Agent type not handled at the moment
    			//Binary type not handled at the moment
    			continue;
    		}
    		
    		try {
    			contactFieldHeader = createFieldHeader(contactField, templateModel);
    		} catch (MappingMissingException e) {
    			throw new SystemException("Error while generating header for field: " + contactField.getTemplateFieldId(), e);
			}
    		
    		// if binary add to blob and get stream id
    		if (templateField.isBinary()) {
    			int streamID = 0;
    	        try {
    	        	streamID = binaryTextBlob.persistToBlob(contactField.getBinaryValue());
    			} catch (ContactsExeption e) {
    				throw new SystemException("Error when generating textBlob for field: " + contactField.getTemplateFieldId(), e);
    			}
    			contactFieldHeader.setStreamId(streamID);
    			contactFieldHeader.getAttributesContainer().setFieldStorageType(templateField.getStorageType());
    		} else if (templateField.isText()) { // searchable text
	            textFieldsBuffer.append(contactField.getTextValue());
	            textFieldsBuffer.append('\0');   
	            contactFieldHeader.setStreamId(0);
    		}
        	
    		//add to field headers
        	contactFieldHeaders.add(contactFieldHeader);
    	}

        AbstractContactHeader contactHeader = createContactHeader(contactFieldHeaders);
        dbmsContact.setHeader(contactHeader);
    	
    	dbmsContact.setTextBlob(binaryTextBlob);
    	dbmsContact.setSearchableText(textFieldsBuffer.toString());
    }
    
  
    private AbstractContactHeader createContactHeader(List<ContactFieldHeader> contactFieldHeaders) {
        try {
            AbstractContactHeader contactHeader = new ContactHeaderForContact(contactFieldHeaders);
            return contactHeader;
        } catch (ContactHeaderCreationException e) {
            throw new SystemException("Problem generating header for contact",e);
        }
    }

     
    private ContactFieldHeader createFieldHeader(ContactField contactField, 
    												ITemplateModel templateModel) throws MappingMissingException {
    	
        ContactFieldHeader contactFieldHeader = new ContactFieldHeader();
        ContactFieldAttribute contactFieldAttribute = new ContactFieldAttribute();
        
        contactFieldAttribute.setCategory(contactField.getCategory().byteValue());
        contactFieldAttribute.addAttribute(ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_SYNCH.getValue());
        contactFieldAttribute.setExtendedAttributes(0);
        contactFieldAttribute.setTemplateId(contactField.getTemplateFieldId());
        
        IField templateField = templateModel.getFields().get(contactField.getTemplateFieldId());
        
        if (hasSpeedDial(contactField, dbmsContact.getSpeedDialData()) && isSpeedDialSupportedField(templateField, templateModel))	{
        	SpeedDialData speedDialData = getSpeedDialDataForField(contactField, dbmsContact.getSpeedDialData());
        	int currentSpeedDialNumber = speedDialData.getSpeedDialIndex();
        	
        	contactFieldAttribute.addAttribute(ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_USERADDEDFIELD.getValue());
        	contactFieldAttribute.addExtendedAttribute(ContactFieldExtendedAttributeFlag.SPEEDIAL.getValue());
        	
        	/*get field properties from template model
        	and add speed dial UID to additional UIDs*/
        	List<Integer> fieldUids = new ArrayList<Integer>();
        	fieldUids.addAll(templateField.getPropertiesValue());
        	fieldUids.add(getSpeedDialUidFromIndex(currentSpeedDialNumber));
        	contactFieldHeader.setFieldAdditionalUIDValues(toArray(fieldUids));
        	
        	contactFieldAttribute.setAdditionalFieldCount(fieldUids.size());
        	contactFieldHeader.setFieldHint(new TemplateHintField(templateField.getFieldType()).getValue());
            contactFieldHeader.setFieldVcardMapping(templateField.getVCardMappingValue());
        }
        else
        {
        	contactFieldAttribute.addAttribute(ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_USETEMPLATEDATA.getValue());
        	 // intentionally set fieldHint to 0 (hints for a field are set in the template) 
            contactFieldHeader.setFieldHint(0);
        }
        
        contactFieldHeader.setAttributesContainer(contactFieldAttribute);
        
       
        return contactFieldHeader;
    }

	private boolean isSpeedDialSupportedField(IField templateField, ITemplateModel template) {
		boolean isSpeedDialSupportedField = false;
		
		Map<String,Long>storageTypeMapping = template.getMapper().getMappingToLong(ContactMapTypes.storage.toString());
		if (templateField.getStorageType().equals(storageTypeMapping.get("KStorageTypeText").intValue()))	{
			isSpeedDialSupportedField = true;
		}
		
		if (!templateField.getFieldType().equals("KUidContactFieldPhoneNumberValue") && !templateField.getFieldType().equals("KUidContactFieldPhoneNumberValue"))	{
			logger.warn("Speed dial assigned to a field of potentially unsupported storage type (StorageType=" + templateField.getStorageType() + "), speed dial should be assigned to a phone number");
		}

		return isSpeedDialSupportedField;
	}

	/**
	 * @param contactField
	 * @param speedDialData
	 * @return
	 */
	private SpeedDialData getSpeedDialDataForField(ContactField contactField, Set<SpeedDialData> speedDialDataSet) {
		for (SpeedDialData speedDialData : speedDialDataSet) {
			if (contactField.getTextValue().equals(speedDialData.getSpeedDialValue()))	{
				return speedDialData;
			}
		}
		throw new ContactsExeption("No speedDial value found for field with value (" + contactField.getTextValue() + ")");
	}

	/**
	 * Checks if given field has speedDial assigned to it
	 * 
	 * @param contactField
	 * @param speedDialData
	 * @return
	 */
	private boolean hasSpeedDial(ContactField contactField, Set<SpeedDialData> speedDialDataSet) {
		
		for (SpeedDialData speedDialData : speedDialDataSet) {
			if (contactField.getTextValue().equals(speedDialData.getSpeedDialValue()))	{
				return true;
			}
		}
		return false;
	}

	private int[] toArray(List<Integer> fieldUids) {
		int[] fieldUidsArray = new int[fieldUids.size()];
		for (int index = 0; index < fieldUids.size(); index++)	{
			fieldUidsArray[index] = fieldUids.get(index);
		}
		return fieldUidsArray;
	}

	private int getSpeedDialUidFromIndex(int speedDialIndex) {
		int speedDialUid = SpeedDialUids.UIDSPEEDDIAL_NULL.getValue();
		
		switch(speedDialIndex)
		{
			case 1:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_ONE.getValue();
				break;
			case 2:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_TWO.getValue();
				break;
			case 3:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_THREE.getValue();
				break;
			case 4:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_FOUR.getValue();
				break;
			case 5:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_FIVE.getValue();
				break;
			case 6:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_SIX.getValue();
				break;
			case 7:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_SEVEN.getValue();
				break;
			case 8:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_EIGHT.getValue();
				break;
			case 9:
				speedDialUid = SpeedDialUids.UIDSPEEDDIAL_NINE.getValue();
				break;	
		}
		return speedDialUid;
	}


    public DBMSContactCard getDBMSContact() {
        return dbmsContact;
    }
    
	/**
	 * @param contact
	 * @return
	 */
	private ContactHintField createHintField(Contact contact) {
		ContactHintField field = new ContactHintField();
		for(ContactHint hint: ContactHint.dbmsValues()){
			if(contact.hasHintField(hint)){
				field.setField(hint);
			}
		}
		return field;
	}

	private ContactExtHintField createExtHintField(Contact contact) {
		ContactExtHintField field = new ContactExtHintField();
		for(ContactHint hint: ContactHint.dbmsExtValues()){
			if(contact.hasHintField(hint)){
				field.setField(hint);
			}
		}
		return field;
	}
	
	
}
