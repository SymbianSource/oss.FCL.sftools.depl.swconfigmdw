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

import java.io.IOException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;

import com.google.common.collect.Multimap;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.dbms.ContactDaoDBMS;
import com.symbian.sdb.contacts.dbms.model.ContactFieldAttributeFlag;
import com.symbian.sdb.contacts.dbms.model.ContactFieldHeader;
import com.symbian.sdb.contacts.dbms.model.ContactHeaderForTemplate;
import com.symbian.sdb.contacts.dbms.model.ContactTextBlob;
import com.symbian.sdb.contacts.dbms.model.DBMSContactAttribute;
import com.symbian.sdb.contacts.dbms.model.DBMSSystemTemplate;
import com.symbian.sdb.contacts.dbms.model.DBMSTemplate;
import com.symbian.sdb.contacts.dbms.model.StoreBlob;
import com.symbian.sdb.contacts.dbms.model.TemplateHintField;
import com.symbian.sdb.contacts.model.Preferences;
import com.symbian.sdb.contacts.model.PreferencesManager;
import com.symbian.sdb.contacts.template.ContactMapTypes;
import com.symbian.sdb.contacts.template.FieldContainer;
import com.symbian.sdb.contacts.template.Flag;
import com.symbian.sdb.contacts.template.IField;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.model.TemplatePersister;
import com.symbian.sdb.contacts.template.model.TemplateReader;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.util.LongArray;
import com.symbian.sdb.util.SymbianSpecificUtils;
import com.symbian.store.StoreException;
import com.symbian.store.StoreOutputStream;

public class DbmsTemplatePersister implements TemplatePersister {
	
	private static final Logger logger = Logger.getLogger(DbmsTemplatePersister.class);
	
	private ContactDaoDBMS contactDao;
	
	private PreferencesManager preferencesManager;

	private TemplateReader templateReader;
	
	public void persistTemplate(ITemplateModel template) {
		if (templateDoesNotExistInDB(template)) {
			DBMSTemplate dbmsTemplate = new DBMSSystemTemplate();
			dbmsTemplate = transformTemplate(template, dbmsTemplate);
			saveTemplateInDB(dbmsTemplate);
			template.setTemplateId(dbmsTemplate.getId());            

			//if the id of the persisted template was not system template id 
			//then this is additional template and should be added to the preference table
			if (dbmsTemplate.getId() != ITemplateModel.SYSTEM_TEMPLATE_ID)  {
				registerAddedTemplateInPreferences(dbmsTemplate.getId()); 	
			}
		} else {
			logger.info("Template already in the database. Using template with id " + template.getTemplateId());
		}
	}

    private void saveTemplateInDB(DBMSTemplate templateCard) {
        contactDao.saveTemplate(templateCard);
		logger.info("DBMS template persisted in database");
    }

    private void registerAddedTemplateInPreferences(long id) {
        Preferences preferences;
        try {
            preferences = preferencesManager.getPreferences();
            preferences.addCardTemplateId((int)id);
        } catch (SDBExecutionException e) {
            throw new SystemException("Cannot add additional template to preferences.", e);
        }
    }


    private DBMSTemplate transformTemplate(ITemplateModel sourceTemplate, DBMSTemplate dbmsTemplate) {
        //Do not set preferred template in preference table 
		dbmsTemplate.setPrefTemplateRefId(-1);
		
		//Set UID String for vCard synchronisation
		long currentSymbianTimestamp = SymbianSpecificUtils.createCurrentSymbianTimestamp();
		dbmsTemplate.setUIDString(Long.toHexString(currentSymbianTimestamp));
		
		//Set contacts creation date
		Date now = Calendar.getInstance().getTime();
		dbmsTemplate.setContactCreationDate(now);
		
		//Set last modified date
		dbmsTemplate.setLastModified(now);
		
		//Set contacts attributes
		dbmsTemplate.setAttributes(DBMSContactAttribute.COMPRESSED_GUID);
		
		//Set replication count
		dbmsTemplate.setReplicationCount(0);
		
		//Set contact header
		try {
			setContactHeaderAndTextBlob(sourceTemplate, dbmsTemplate);
		} catch(MappingMissingException mme) {
			throw new SystemException(mme);
		}
		
		//Set null searchable text 
		dbmsTemplate.setSearchableText(createSearchableTextForFieds(sourceTemplate));

		return dbmsTemplate;
	}

	private String createSearchableTextForFieds(ITemplateModel template) {
		
		String text = "";
		
		//get  fields from template RSS file
		FieldContainer fields = template.getFields();
		
		for (IField field : fields) {
			//if field type is text put null char in searchable text
			Integer storageType = field.getStorageType();
			if (null == storageType)	{
				// TODO check with S60 source code what to do if there is no storage type for a field   
				logger.warn("No storage type found for field index: "+ field.getIndex() + ", using default - 0");
				storageType = 0;
			}
			if(storageType == 0 )
				text += "\0";	
		}
		
		return text;
	}
	
	private void setContactHeaderAndTextBlob(ITemplateModel template, DBMSTemplate templateCard) 
																throws MappingMissingException {
		List<ContactFieldHeader> fieldHeaders = new ArrayList<ContactFieldHeader>();
		//Get fields from template model
		FieldContainer fields = template.getFields();
		Multimap<Integer, String> flagMap = template.getMapper().getFlagsMapping();

		StoreBlob storeBlob = createNewStoreBlob();

		//Populate header with template data
		for (IField field : fields) {			
			
			
			//create header object 		
			ContactFieldHeader fieldHeader = new ContactFieldHeader();
			
			//Set default attributes
			fieldHeader.getAttributesContainer().addAttribute(
					ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_SYNCH.getValue());
			fieldHeader.getAttributesContainer().addAttribute(
					ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_OVERIDELABEL.getValue());
			fieldHeader.getAttributesContainer().setCategory(field.getCategory().byteValue());
			
			for(Flag flag : field.getFlags()) {
				
				Collection<String> flaguids = flagMap.get(flag.getValue());
				
				if (flag.getUID().contains("Filterable") && (flaguids.contains("KIntFieldFlagFilterable") ||
						flaguids.contains("KIntFieldFlagFilterable1") ||
						flaguids.contains("KIntFieldFlagFilterable2") ||
						flaguids.contains("KIntFieldFlagFilterable3") ||
						flaguids.contains("KIntFieldFlagFilterable4"))) { 
					fieldHeader.getAttributesContainer().addExtendedAttribute(flag.getValue());
				} else {
					fieldHeader.getAttributesContainer().addAttribute(flag.getValue());
				} 
			}
			
			// TODO, clean this up. It is not a nice bit of value construction. The header exposes too
			// much implementation. For example if the field ID is set before the type then setting
			// the type wipes out the ID (same for hasAdditionalVCardMappings)
			
			//set contact field type
			if (null != field.getStorageType())	{
				fieldHeader.getAttributesContainer().setFieldStorageType(field.getStorageType());	
			}
			else	{
				logger.warn("No storage type found for field index: "+ field.getIndex() + ", using default - 0");
				fieldHeader.getAttributesContainer().setFieldStorageType(0);
			}
			
			
			//set number of addition mappings
			
			TemplateHintField hintField = new TemplateHintField(field.getFieldType());
			
			List<Integer> propertyList = new ArrayList<Integer>(field.getPropertiesValue());
			if (hintField.getValue() == 0 && field.getFieldType() != "KUidContactFieldNoneValue") {
				propertyList.add(0, field.getFieldTypeValue());
			}
			fieldHeader.getAttributesContainer().setAdditionalFieldCount(propertyList.size()); 
			fieldHeader.setFieldAdditionalUIDValues(toIntArray(propertyList));
			
			//Set template id 
			fieldHeader.getAttributesContainer().setTemplateId(ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_TEMPLATEID.getValue());
			
			generateTextBlobAndStreamIdForField(template, storeBlob, field, fieldHeader);
			
			// Set the field (hint) attributes
			fieldHeader.setFieldHint(hintField.getValue());
			fieldHeader.setFieldId(field.getIndex());
			//TODO probably the check should be propertyList.size() > 0?
			if(field.getVCardMapping() != null && field.getVCardMapping().length() > 0){
				fieldHeader.setFieldHasAdditionalUIDs();
			}
			
			//Set vCard mapping
			fieldHeader.setFieldVcardMapping(field.getVCardMappingValue());
			
			//Set Label
			String fieldNameValue = null;
			if (field.getFieldName() != null) {
				fieldNameValue = field.getFieldNameValue();
			}
			else	{
				fieldNameValue = "";
			}
			fieldHeader.getFieldLabel().setLength(fieldNameValue.length());
			fieldHeader.getFieldLabel().setLabel(fieldNameValue);

			//insert header into header list
			fieldHeaders.add(fieldHeader);	
		}
		
		commitAndCloseStore(storeBlob);
		setStoreBlobContent(templateCard, storeBlob.getBlob());
		
		//Set populated fields in to contact header
		try {
			//TODO Template header needs to be fixed it's being generated by static blob value
			//AbstractContactHeader  header = new ContactHeaderForTemplate(HexStringConverter.convertHexStringToByteArray("04000000641C01C0FF0000000000000000000200002E40001005000000145469746C651401C0FF0000000000000000200040002E4000100A000000284669727374206E616D651C01C0FF0000000000000000800080002E4000100B0000002C4D6964646C65206E616D651401C0FF00000000000000001000C0002E40001009000000244C617374206E616D651C01C0FF0000000000000000000100012E40001006000000185375666669781401CCFF000000000000000002004001DB390010DD390010713E00102A40001006000000184D6F62696C651401C8FF000000000000000002008001DB390010DD3900102A4000100800000020486F6D652074656C1C01CCFF00000000000000000000C00191170010DB390010DE3900102A4000100800000020486F6D65206661781C01CCFF000000000000000002000002DB390010DD390010723E00102A4000100A00000028486F6D652050616765721C01C8FF000000000000000002004002DB390010D53900102A4000100E0000003842756C6C6574696E20426F6172641C01C8FF000000000000000002008002DB390010D63900102A4000100A00000028486F6D65204D6F64656D1C01CCFF00000000000000000200C002DB390010DD390010D73900102A40001009000000244361722050686F6E651C01C8FF000000000000000002000003DB390010D83900102A4000100900000024486F6D65204953444E1C01C8FF000000000000000002004003DB390010D93900102A4000100A00000028486F6D6520566964656F1401C4FF000000000000000000408003DB390010204000100A00000028486F6D6520656D61696C1C01C8FF00000000000000000000C003F44D0010DB390010EA4D00100B0000002C486F6D6520504F20626F781C01C8FF000000000000000000000004F54D0010DB390010EB4D00101000000040486F6D652065787420616464726573731401C4FF000000000000000040004004DB3900101D4000100C00000030486F6D6520616464726573731401C8FF000000000000000000008004F64D0010DB390010EC4D00100900000024486F6D6520636974791401C8FF00000000000000000000C004F74D0010DB390010ED4D00100B0000002C486F6D6520726567696F6E1401C8FF000000000000000000000005F84D0010DB390010EE4D00100B0000002C486F6D65207027636F64651401C8FF000000000000000000004005F94D0010DB390010EF4D00100C00000030486F6D6520636F756E7472791401C8FF00000000000000000000800535400010DB3900102D4000100D00000034486F6D652057656220706167652401C0FF00000000000000000800C00526400010070000001C436F6D70616E792401C4FF000000000000000000000006989300102C40001009000000244A6F62207469746C652C01CCFF000000000000000002004006DA390010DD390010713E00102A4000100B0000002C576F726B206D6F62696C652401C8FF000000000000000002008006DA390010DD3900102A4000100800000020576F726B2074656C2401CCFF00000000000000000000C00691170010DA390010DE3900102A4000100800000020576F726B206661782C01C8FF000000000000000002000007723E0010DA3900102A4000100A00000028576F726B2070616765722C01C8FF000000000000000002004007DA390010D53900102A400010130000004C576F726B2042756C6C6574696E20426F6172642C01C8FF000000000000000002008007DA390010D63900102A4000100A00000028576F726B204D6F64656D1C01CCFF00000000000000000200C007DA390010DD390010D73900102A4000100E00000038576F726B204361722050686F6E652C01C8FF000000000000000002000008DA390010D83900102A4000100900000024576F726B204953444E2C01C8FF000000000000000002004008DA390010D93900102A4000100A00000028576F726B20566964656F2401C4FF000000000000000000408008DA390010204000100A00000028576F726B20656D61696C2401C8FF00000000000000000000C00835400010DA3900102D4000100D00000034576F726B2057656220706167652C01C8FF000000000000000000000009F44D0010DA390010EA4D00100B0000002C576F726B20504F20626F782C01C8FF000000000000000000004009F54D0010DA390010EB4D00101000000040576F726B2065787420616464726573732401C4FF000000000000000040008009DA3900101D4000100C00000030576F726B20616464726573732401C8FF00000000000000000000C009F64D0010DA390010EC4D00100900000024576F726B20636974792401C8FF00000000000000000000000AF74D0010DA390010ED4D00100B0000002C576F726B20726567696F6E2401C8FF00000000000000000000400AF84D0010DA390010EE4D00100B0000002C576F726B207027636F64652401C8FF00000000000000000000800AF94D0010DA390010EF4D00100C00000030576F726B20636F756E7472792511C4FF00000000040000000000C00AD15D00102340001004000000104C4F474F3C31C4FF00000000080000000000000B344000101F400010080000002042697274686461793401C4FF00000000000000000000400B1C4000102540001005000000144E6F7465730501C0FF00000000000000000000800B2F4000100C00000030446973706C6179206E616D650411C4FF00000000100000000000C00BD15D001027400010050000001450484F544F0C01C0FF00000000000000000000000C2240001005000000144C4142454C0501C4FF00000000000000000000400C805700102E400010160000005847726F7570202F2054656D706C617465204C6162656C"));
			templateCard.setHeader(new ContactHeaderForTemplate(fieldHeaders));
		} catch (Exception e) {
			logger.warn("Template could not be persisted in database. Reason: ", e);
			throw new MappingMissingException(e);
		}
		
	}

	/**
	 * @param storeBlob
	 */
	private void commitAndCloseStore(StoreBlob storeBlob) {
		try {
			storeBlob.closeStore();
		} catch (StoreException e1) {
			throw new SystemException("Error when generating store blob for template", e1);
		}
	}

	/**
	 * @param template
	 * @param storeBlob
	 * @param field
	 * @param fieldHeader
	 */
	private void generateTextBlobAndStreamIdForField(ITemplateModel template,
			StoreBlob storeBlob, IField field, ContactFieldHeader fieldHeader) {
		// generate textBlob and set streamId
		try {
			fieldHeader.setStreamId(0);
			
			Map<String,Long>storageTypeMapping = template.getMapper().getMappingToLong(ContactMapTypes.storage.toString());
			
			Integer storageType = field.getStorageType();
			if (null == storageType)	{
				logger.warn("No storage type found for field index: "+ field.getIndex() + ", using default - 0");
				storageType = 0;
			}
			
			if (storageType.equals(storageTypeMapping.get("KStorageTypeDateTime").intValue()))	{
				StoreOutputStream stream = setupStream(storeBlob, fieldHeader);
				// write 0x8000000000000000
				stream.writeInt64(0x8000000000000000L);	
			}
			else	{
				if (storageType.equals(storageTypeMapping.get("KStorageTypeStore").intValue()))	{
					StoreOutputStream stream = setupStream(storeBlob,fieldHeader);
					stream.writeInt32(0);	
				}
			}
			
		} catch (StoreException e) {
			throw new SystemException("Error when writing to text blob store", e);
		} catch (IOException e) {
			throw new SystemException("Error when writing to text blob store", e);
		}
	}

	/**
	 * @param storeBlob
	 * @param fieldHeader
	 * @return
	 * @throws StoreException
	 */
	private StoreOutputStream setupStream(StoreBlob storeBlob, ContactFieldHeader fieldHeader) throws StoreException {
		StoreOutputStream stream = storeBlob.createStream();
		//Set stream id 
		fieldHeader.setStreamId(stream.getStreamId());
		return stream;
	}

	/**
	 * @param templateCard
	 * @param blobContent 
	 * @param storeBlob
	 */
	private void setStoreBlobContent(DBMSTemplate templateCard, byte[] blobContent) {
		// contactTextBlob needs to be refactored to support multiple binary field types  
		templateCard.setTextBlob(new ContactTextBlob(blobContent));
	}

	/**
	 * @return
	 */
	private StoreBlob createNewStoreBlob() {
		StoreBlob storeBlob = new StoreBlob();
		try {
			storeBlob.createStore();
		} catch (StoreException e2) {
			throw new SystemException("Error when creating new store blob for template", e2);
		}
		return storeBlob;
	}

	private int[] toIntArray(List<Integer> integers) {
		int[] ints = new int[integers.size()];
		int index = 0;
		for (Integer integer : integers) {
			ints[index++] = integer;
		}
		return ints;
	}
	
    public boolean templateDoesNotExistInDB(ITemplateModel template) {
        List<ITemplateModel> templatesInDB = findAllTemplatesInDB();
        return !contains(templatesInDB, template);
    }

    private boolean contains(List<ITemplateModel> dbTemplates, ITemplateModel template) {
        for (ITemplateModel dbTemplate : dbTemplates) {
            if (template.isSame(dbTemplate)) {
            	template.setTemplateId(dbTemplate.getTemplateId());
                return true;
            }
        }
        return false;
    }

    private List<ITemplateModel> findAllTemplatesInDB() {
        // find all templates from preferences + system template
        List<Long> templatesIds = findAllTemplatesIds();

        List<ITemplateModel> templates = new ArrayList<ITemplateModel>();
        for (Long templateId : templatesIds) {
            ITemplateModel template = readTemplate(templateId);
            templates.add(template);
        }
        return templates;
    }

    private ITemplateModel readTemplate(Long templateId) {
        try {
            return templateReader.readTemplate(templateId);
        } catch (TemplateParsingException e) {
            throw new SystemException(e);
        }
    }
    
    private List<Long> findAllTemplatesIds() {
        List<Long> templateIds = getTemplateIds();

        if (systemTemplateExistsInDB()) {
            templateIds.add(ITemplateModel.SYSTEM_TEMPLATE_ID);    
        }
        
        return templateIds;
    }
      
    public boolean systemTemplateExistsInDB() {
    	return contactDao.templateExistsInDB(ITemplateModel.SYSTEM_TEMPLATE_ID);
    }
    
    private List<Long> convertToList(LongArray longArray) {
        List<Long> convertedList = new ArrayList<Long>();
        for (int i = 0; i < longArray.getAsArray().length; i++) {
            Long arrayElement = longArray.getAsArray()[i];
            convertedList.add(arrayElement);
        }
        return convertedList;
    }

    private List<Long> getTemplateIds() {
        Preferences preferences;
        try {
            preferences = preferencesManager.getPreferences();
            LongArray templateIds = preferences.getCardTemplateIds();
            return convertToList(templateIds); 
        } catch (SDBExecutionException e) {
            throw new SystemException(e);
        }
    }      
    
	//~ Getter/Setters ---------------------------------------------------------
	/**
	 * Set data access object for template persistence
	 * @param contactDao
	 */
	public void setContactDao(ContactDaoDBMS contactDao) {
		this.contactDao = contactDao;
	}
	
    public void setPreferencesManager(PreferencesManager preferencesManager) {
        this.preferencesManager = preferencesManager;
    }
    
    public void setTemplateReader(TemplateReader templateReader) {
		this.templateReader = templateReader;
	}

}
