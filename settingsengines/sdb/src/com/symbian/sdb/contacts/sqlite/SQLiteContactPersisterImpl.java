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

package com.symbian.sdb.contacts.sqlite;

import java.util.Collection;
import java.util.Date;
import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.AbstractContactPersisterImpl;
import com.symbian.sdb.contacts.helper.HexStringConverter;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.EmailAddress;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.model.PhoneNumber;
import com.symbian.sdb.contacts.sqlite.model.ContactType;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactAttribute;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactCard;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactGroup;
import com.symbian.sdb.contacts.sqlite.model.SQLiteEmailAddress;
import com.symbian.sdb.contacts.sqlite.model.SQLitePhoneNumber;
import com.symbian.sdb.contacts.sqlite.model.TypeFlags;
import com.symbian.sdb.contacts.sqlite.model.creator.SQLiteContactBuilder;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.exception.SDBValidationException;

/**
 * ContactsPersister implementation specific for SQLite database
 * 
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactPersisterImpl extends AbstractContactPersisterImpl<SQLiteContactCard> {

    //~ Injected Fields ========================================================

    private ContactDaoSQLite contactDao;
    
    public SQLiteContactCard transformContact(Contact contact, ITemplateModel templateModel) {
        SQLiteContactBuilder contactBuilder = new SQLiteContactBuilder();
        contactBuilder.createNewContact(contact);
        SQLiteContactCard sqLiteContact = contactBuilder.getSqLiteContact();
        
        transformGroups(contact.getGroups(),sqLiteContact);
        sqLiteContact.getEmailAddresses().addAll(transformEmails(contact.getEmails()));
        sqLiteContact.getPhoneNumbers().addAll(transformPhoneNumbers(contact.getPhoneNumbers()));
        
        return sqLiteContact;
    }

    private Collection<SQLitePhoneNumber> transformPhoneNumbers(Set<PhoneNumber> phoneNumbers) {
        Collection<SQLitePhoneNumber> sqLitePhoneNumbers = new HashSet<SQLitePhoneNumber>();

        for (PhoneNumber phoneNumber : phoneNumbers) {
            SQLitePhoneNumber sqLitePhoneNumber = transformPhoneNumber(phoneNumber);
            sqLitePhoneNumbers.add(sqLitePhoneNumber);
        }
        return sqLitePhoneNumbers;
    }

    private SQLitePhoneNumber transformPhoneNumber(PhoneNumber phoneNumber) {
        SQLitePhoneNumber sqlitePhoneNumber = new SQLitePhoneNumber();
        
        String reversedPhoneNumber = new StringBuffer(phoneNumber.getTextValue()).reverse().toString();
        
        String reversedPhoneNumberSuffix = "";
        String reversedPhoneNumberPrefix = "";
        
        // 
        if (reversedPhoneNumber.length() > 7)   {
            // phone numbers last 7 digits
            reversedPhoneNumberSuffix = reversedPhoneNumber.substring(0,7);
            reversedPhoneNumberPrefix = reversedPhoneNumber.substring(7, reversedPhoneNumber.length());
        }
        else    {
            reversedPhoneNumberSuffix = reversedPhoneNumber.substring(0,reversedPhoneNumber.length());
            reversedPhoneNumberPrefix = "";
        }
            
        sqlitePhoneNumber.setValue(reversedPhoneNumberSuffix);
        sqlitePhoneNumber.setExtraValue(reversedPhoneNumberPrefix);
        
        return sqlitePhoneNumber;
    }

    /**
     * @param emails
     * @return
     */
    private Collection<SQLiteEmailAddress> transformEmails(Set<EmailAddress> emails) {
        Collection<SQLiteEmailAddress> sqLiteEmailAddresses = new HashSet<SQLiteEmailAddress>();
        
        for (EmailAddress emailAddress : emails) {
            SQLiteEmailAddress sqLiteEmailAddress = transformEmailAddress(emailAddress);
            sqLiteEmailAddresses.add(sqLiteEmailAddress);
        }
        return sqLiteEmailAddresses;
    }

    /**
     * @param emailAddress
     * @return
     */
    private SQLiteEmailAddress transformEmailAddress(EmailAddress emailAddress) {

        SQLiteEmailAddress sqLiteEmailAddress = new SQLiteEmailAddress();
        sqLiteEmailAddress.setValue(emailAddress.getTextValue());
        return sqLiteEmailAddress;
    }

    /**
     * @param contactGroups
     * @param sqLiteContact adds transformed groups to this contact
     */
    public void transformGroups(Set<Group> contactGroups, SQLiteContactCard sqLiteContact) {

        for (Group group : contactGroups) {
            SQLiteContactGroup sqLiteGroup = transformGroup(group);
            
            sqLiteContact.addGroup(sqLiteGroup);
        }
    }

    public SQLiteContactGroup transformGroup(Group group) {
        SQLiteContactGroup sqLiteGroup = new SQLiteContactGroup();
        sqLiteGroup.setTemplateId(-1);

        //int typeFlags = 50593792;
        // // TODO KZ: 4 instead of 3 (group)
        TypeFlags typeFlags = new TypeFlags(ContactType.GROUP);
        typeFlags.setContactAttributes(SQLiteContactAttribute.COMPRESSED_GUID);
        sqLiteGroup.setTypeFlags(typeFlags);
        
        sqLiteGroup.setAccessCount(0);
        
        //long creationDate = 63388108024220000L;
        long currentDate = new Date().getTime();
        sqLiteGroup.setCreationDate(currentDate);
        
        //long lastModification = 63388108024220000L;
        sqLiteGroup.setLastModification(currentDate);
        
        // TODO KZ: how to generate guid? temporarily use fixed guid
        //String guidString = "00e13325fdc48960";
        sqLiteGroup.setGuidString("00e1334dae0669e3");
        
        // TODO KZ: blobs - use fixed values 
        String textFieldsHeader = "040000000E140200000100000001000000140200000300000003000000140200000500000005000000240200001700000017000000240200001800000018000000240200001A0000001A000000340200002B0000002B000000";
        sqLiteGroup.setTextFieldsHeader(HexStringConverter.convertHexStringToByteArray(textFieldsHeader));
        String binaryFieldsHeader = "0400000000";
        sqLiteGroup.setBinaryFieldsHeader(binaryFieldsHeader);
        sqLiteGroup.setTextFields(group.getName());
        byte[] binaryFields = {0x00, 0x00, 0x00, 0x00};
        sqLiteGroup.setBinaryFields(binaryFields);
        return sqLiteGroup;
    }

    /**
     * Persists contact card for contact
     * 
     * @param sqLiteContact
     */
    public void createContactCard(SQLiteContactCard sqLiteContact) {
        contactDao.save(sqLiteContact);
    }

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.ContactsPersister#validateContactsDbSchema()
	 */
	public void validateContactsDbSchema() throws SDBValidationException {
		this.contactDao.validateContactsDbSchema();
	}
    
    // ~ Getters/Setters =======================================================

    public void setContactDao(ContactDaoSQLite contactDao) {
        this.contactDao = contactDao;
    }

 }
