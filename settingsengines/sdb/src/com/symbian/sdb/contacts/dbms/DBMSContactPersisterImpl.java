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

package com.symbian.sdb.contacts.dbms;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.symbian.sdb.contacts.AbstractContactPersisterImpl;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.dbms.model.AbstractDBMSContact;
import com.symbian.sdb.contacts.dbms.model.ContactExtHintField;
import com.symbian.sdb.contacts.dbms.model.ContactFieldAttribute;
import com.symbian.sdb.contacts.dbms.model.ContactFieldHeader;
import com.symbian.sdb.contacts.dbms.model.ContactHeaderForTemplate;
import com.symbian.sdb.contacts.dbms.model.ContactHintField;
import com.symbian.sdb.contacts.dbms.model.ContactTextBlob;
import com.symbian.sdb.contacts.dbms.model.DBMSContactAttribute;
import com.symbian.sdb.contacts.dbms.model.DBMSContactCard;
import com.symbian.sdb.contacts.dbms.model.DBMSContactGroup;
import com.symbian.sdb.contacts.dbms.model.DBMSEmailAddress;
import com.symbian.sdb.contacts.dbms.model.DBMSPhoneNumber;
import com.symbian.sdb.contacts.dbms.model.IdentityTable;
import com.symbian.sdb.contacts.dbms.model.creator.DBMSContactBuilder;
import com.symbian.sdb.contacts.helper.HexStringConverter;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.model.EmailAddress;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.model.PhoneNumber;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.exception.SDBValidationException;

/**
 * ContactsPersister implementation specific for DBMS database
 * 
 * @author krzysztofZielinski
 *
 */
public class DBMSContactPersisterImpl extends AbstractContactPersisterImpl<DBMSContactCard> {
	// these are hard-coded constants in native for groups
	static final String KGroupLabel = "Group Label";
    static final int KUidContactFieldTemplateLabelValue = 0x10005780;
    
    private SpeedDialManager speedDialManager; 
    
    //~ Injected Fields ========================================================
    private ContactDaoDBMS contactDao;
    
    public DBMSContactCard transformContact(Contact contact, ITemplateModel templateModel) {
        DBMSContactBuilder contactBuilder = new DBMSContactBuilder(speedDialManager);
        contactBuilder.createNewContact(contact, templateModel);
        DBMSContactCard dbmsContact = contactBuilder.getDBMSContact();
        
        transformGroups(contact.getGroups(),dbmsContact);
        dbmsContact.getEmailAddresses().addAll(transformEmails(contact.getEmails()));
        dbmsContact.getPhoneNumbers().addAll(transformPhoneNumbers(contact.getPhoneNumbers()));
        
        return dbmsContact;
    }

	/**
     * @param phoneNumbers
     * @return
     */
    private Collection<DBMSPhoneNumber> transformPhoneNumbers(Set<PhoneNumber> phoneNumbers) {
        Collection<DBMSPhoneNumber> dbmsPhoneNumbers = new HashSet<DBMSPhoneNumber>();

        for (PhoneNumber phoneNumber : phoneNumbers) {
            DBMSPhoneNumber dbmsPhoneNumber = transformPhoneNumber(phoneNumber);
            dbmsPhoneNumbers.add(dbmsPhoneNumber);
        }
        return dbmsPhoneNumbers;
    }

	 public DBMSPhoneNumber transformPhoneNumber(PhoneNumber phoneNumber) {
		 DBMSPhoneNumber dbmsPhoneNumber = new DBMSPhoneNumber();
		 
		 String aTextualNumber = phoneNumber.getTextValue();
		 StringBuilder aRawNumber = new StringBuilder();

		 int length = aTextualNumber.length();

		 if (length == 0) {
			 return null;
		 }

		 aTextualNumber = aTextualNumber.trim();

		 char firstChar = aTextualNumber.charAt(0);

		 // Get left hand side
		 if (firstChar == '*' || firstChar == '#') {
			 // Check if there is plus on first five chars:
			 int newStartPlace = aTextualNumber.indexOf('+');

			 if (newStartPlace >= 5 || newStartPlace == -1) {
				 // There is always star or hash...
				 newStartPlace = Math.max(
						 aTextualNumber.lastIndexOf('*'), 
						 aTextualNumber.lastIndexOf('#'));
			 }

			 length = length - newStartPlace - 1;

			 if (length <= 0) {
				 return dbmsPhoneNumber;
			 }

			 aTextualNumber = aTextualNumber.substring(aTextualNumber.length() - length).trim();
			 firstChar = aTextualNumber.charAt(0);
		 }

		 // test condition to satisfy the removal of '(' the next if statement removes the '+' if needed
		 if (firstChar == '(') {
			 aTextualNumber = aTextualNumber.substring(1).trim();

			 length = aTextualNumber.length();
			 // This may be the only character in the descriptor so only access if 1 or more characters left.
			 if (length > 0) {
				 firstChar = aTextualNumber.charAt(0);
			 }
		 }

		 if (firstChar == '+') {
			 aTextualNumber = aTextualNumber.substring(1).trim();
		 }

		 if (aTextualNumber.length() == 0) {
			 aRawNumber = new StringBuilder();
		 }

		 // Find right hand side
		 for (char nextChar :aTextualNumber.toCharArray()) {
			 if (Character.isDigit(nextChar)) {
				 aRawNumber.append(nextChar);
				 continue;
			 } else if (nextChar == '*' || nextChar == '#') {
				 return dbmsPhoneNumber;
			 } else {
				 nextChar = Character.toLowerCase(nextChar);
				 if (nextChar == 'p' || nextChar == 'w'	|| nextChar == '+') {
					 break;
				 }
			 }
		 }

		 String reversedPhoneNumber = aRawNumber.reverse().toString();

		 StringBuilder phoneMatching = new StringBuilder();
		 StringBuilder phoneExtendedMatching = new StringBuilder();

		 if (reversedPhoneNumber.length() > 7)   {
			 // phone numbers last 7 digits
			 phoneMatching.append(Integer.parseInt(reversedPhoneNumber.substring(0,7)));

			 if (reversedPhoneNumber.length() > 15) {
				 phoneExtendedMatching.append(Integer.parseInt(reversedPhoneNumber.substring(7, 15)));
			 }
			 else {
				 phoneExtendedMatching.append(Integer.parseInt(reversedPhoneNumber.substring(7, reversedPhoneNumber.length())));
				 // Pad the number with 0's
				 while (phoneExtendedMatching.length() < 8) {
							 phoneExtendedMatching.append(0);
				 }
			 }
		 }
		 else    {
			 phoneMatching.append(reversedPhoneNumber.substring(0,reversedPhoneNumber.length()));
			 // Pad the number with 0's
			 while (phoneMatching.length() < 7) {
				 phoneMatching.append(0);
			 }
		 }
		 
		 if (phoneMatching.length() > 0 && Integer.parseInt(phoneMatching.toString()) != 0) {
			 dbmsPhoneNumber.setPhoneMatching(Integer.parseInt(phoneMatching.toString()));
			 
			 if (phoneExtendedMatching.length() > 0) {
				 dbmsPhoneNumber.setExtendedPhoneMatching(Integer.parseInt(phoneExtendedMatching.toString()));
			 }
			 else {
				 dbmsPhoneNumber.setExtendedPhoneMatching(0);			 
			 }
		 }
	
		 return dbmsPhoneNumber;
	 }


    private Collection<DBMSEmailAddress> transformEmails(Set<EmailAddress> emails) {
        Collection<DBMSEmailAddress> dbmsEmailAddresses = new HashSet<DBMSEmailAddress>();
        
        for (EmailAddress emailAddress : emails) {
            DBMSEmailAddress dbmsEmailAddress = transformEmailAddress(emailAddress);
            dbmsEmailAddresses.add(dbmsEmailAddress);
        }
        return dbmsEmailAddresses;
    }

    private DBMSEmailAddress transformEmailAddress(EmailAddress emailAddress) {

        DBMSEmailAddress dbmsEmailAddress = new DBMSEmailAddress();
        dbmsEmailAddress.setValue(emailAddress.getTextValue());
        return dbmsEmailAddress;
    }

    /**
     * Iterates over the group set, creates group objects and adds them to the contact. 
     * 
     * @param contactGroups
     * @param dbmsContact
     */
    public void transformGroups(Set<Group> contactGroups, AbstractDBMSContact dbmsContact) {

        for (Group group : contactGroups) {
            DBMSContactGroup dbmsGroup = transformGroup(group);
            
            dbmsContact.addGroup(dbmsGroup);
        }
    }

    /**
     * Creates a DBMSContactGroup object from the group name.
     * @param group
     * @return
     */
    public DBMSContactGroup transformGroup(Group group) {

        DBMSContactGroup dbmsGroup = new DBMSContactGroup();
        dbmsGroup.setName(group.getName());

        // fill in data for contacts table
        Date currentDate = new Date();
        dbmsGroup.setUIDString("00e133b27cdb1f9d");
        dbmsGroup.setLastModified(currentDate);
        dbmsGroup.setContactCreationDate(currentDate);

        dbmsGroup.setAttributes(DBMSContactAttribute.COMPRESSED_GUID);

        // mimic the headers added in the native cntmodel 
        ContactFieldHeader header = new ContactFieldHeader();

        // create and set attributes
        ContactFieldAttribute attrib = new ContactFieldAttribute();
        attrib.setAdditionalFieldCount(1); //why one ? 
        attrib.setFieldStorageType(0);
        attrib.setCategory((byte) 0);
        attrib.setTemplateId(0x3ff);// why?
        attrib.addAttribute(0x104); // why?
        
        header.setAttributesContainer(attrib);
        
        // set other header fields
        header.setStreamId(0);
        header.setFieldHint(0);
        int[] additionalFields = {KUidContactFieldTemplateLabelValue};  
        header.setFieldAdditionalUIDValues(additionalFields);
        header.setFieldVcardMapping(0);
        
        // field label
        ContactFieldLabel header1Label = new ContactFieldLabel();
        header1Label.setLabel(KGroupLabel);
        header1Label.setLength(KGroupLabel.length());
        header.setFieldLabel(header1Label);

        // now generate blob
        List<ContactFieldHeader> headers = new ArrayList<ContactFieldHeader>();
        headers.add(header);
        try {
            dbmsGroup.setHeader(new ContactHeaderForTemplate(headers));
        }
        catch (Exception e) {
            throw new SystemException("Error when generating Header for Group (" + group.getName() + ")",e);
        }
        // text blob is 0x00000000
        byte [] blankTextBlob = HexStringConverter.convertHexStringToByteArray("00000000");
        dbmsGroup.setTextBlob(new ContactTextBlob(blankTextBlob));
        dbmsGroup.setSearchableText(group.getName()+"\0");
        
        // fill in data for identityTable table
        IdentityTable identityTable = dbmsGroup.getIdentityTable();
        
        identityTable.setAttribute(dbmsGroup.getAttributes());
        identityTable.setContactHintField(new ContactHintField());
        identityTable.setContactExtHintField(new ContactExtHintField());
        
        return dbmsGroup;
    }

    
    /**
     * Persists contact card for contact
     * 
     * @param dbmsContact
     */
    public void createContactCard(DBMSContactCard dbmsContact) {
        contactDao.save(dbmsContact);
    }

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.ContactsPersister#validateContactsDbSchema()
	 */
	public void validateContactsDbSchema() throws SDBValidationException {
		this.contactDao.validateContactsDbSchema();
	}

    // ~ Getters/Setters =======================================================

    public void setContactDao(ContactDaoDBMS contactDao) {
        this.contactDao = contactDao;
    }

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}

 }
