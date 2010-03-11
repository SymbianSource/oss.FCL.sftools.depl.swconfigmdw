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

package com.symbian.sdb.contacts.model;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;
import com.symbian.sdb.contacts.template.ContactMapTypes;
import com.symbian.sdb.contacts.template.ContactsUidMap;
import com.symbian.sdb.contacts.template.TemplateMapper;

/**
 * Contacts model class - use for contacts internal representation
 *  
 * @author krzysztofZielinski
 *
 */
public class ContactImpl {
    
    //~ Fields ================================================================
    
    private ContactField firstName;
    private ContactField lastName;
    private ContactField companyName;
    private ContactField firstNamePrn;
    private ContactField lastNamePrn;
    private ContactField companyNamePrn;
    
    private Set<ContactField> fields = new HashSet<ContactField>();
    private Set<Group> groups = new HashSet<Group>();
    private Set<PhoneNumber> phoneNumbers  = new HashSet<PhoneNumber>();
    private Set<EmailAddress> emailAddresses = new HashSet<EmailAddress>();
    
    Set<SpeedDialData> speedDialData = new HashSet<SpeedDialData>();
    
    // ~ Hint field UIDs
    
    private static final String HOME = "KUidContactFieldVCardMapHOME";
    private static final String FAX = "KUidContactFieldFax";
    private static final String IM = "KUidContactFieldIMAddress";
    private static final String PAGER = "KUidContactFieldVCardMapPAGER";
    private static final String CELL = "KUidContactFieldVCardMapCELL";
    private static final String WV = "KUidContactFieldVCardMapWV";
    private static final String WORK = "KUidContactFieldVCardMapWORK";
    
    private static final String VOICE_DIAL = "KUidContactsVoiceDialField";
    
    private static final String FILT1 = "KIntFieldFlagFilterable1";
    private static final String FILT2 = "KIntFieldFlagFilterable2";
    private static final String FILT3 = "KIntFieldFlagFilterable3";
    private static final String FILT4 = "KIntFieldFlagFilterable3";
    // ~ Constructors ==========================================================
    
    public ContactImpl() {
        super();
    }

    // ~ Helper/Util Methods ===================================================
    
    public void addGroup(Group group)   {
        this.groups.add(group);
    }
    
    public void addPhoneNumber(PhoneNumber phoneNumber) {
        this.phoneNumbers.add(phoneNumber);
        addField(phoneNumber);
    }
    
    public void addEmailAddress(EmailAddress emailAddress)  {
        this.emailAddresses.add(emailAddress);
        addField(emailAddress);
    }
    
    public void addField(ContactField contactField) {
        if (fieldNotEmpty(contactField))   {
            this.fields.add(contactField);    
        }
    }

    public Set<Group> getGroups() {
        return groups;
    }

    public Set<ContactField> getFields() {
        return fields;
    }

    public Set<PhoneNumber> getPhoneNumbers() {
        return phoneNumbers;
    }

    public Set<EmailAddress> getEmails() {
        return emailAddresses;
    }

    public ContactField getFirstName() {
        return firstName;
    }

    public ContactField getLastName() {
        return lastName;
    }

    public ContactField getCompanyName() {
        return companyName;
    }

    public ContactField getFirstNamePrn() {
        return firstNamePrn;
    }

    public ContactField getLastNamePrn() {
        return lastNamePrn;
    }

    public ContactField getCompanyNamePrn() {
        return companyNamePrn;
    }

    public void setFirstName(ContactField firstName) {
        this.firstName = firstName;
        addField(firstName);
    }

    public void setLastName(ContactField lastName) {
        this.lastName = lastName;
        addField(lastName);
    }

    public void setCompanyName(ContactField companyName) {
        this.companyName = companyName;
        addField(companyName);
    }

    public void setFirstNamePrn(ContactField firstNamePrn) {
        this.firstNamePrn = firstNamePrn;
        addField(firstNamePrn);
    }

    public void setLastNamePrn(ContactField lastNamePrn) {
        this.lastNamePrn = lastNamePrn;
        addField(lastNamePrn);
    }

    public void setCompanyNamePrn(ContactField companyNamePrn) {
        this.companyNamePrn = companyNamePrn;
        addField(companyNamePrn);
    }
    
    private boolean fieldNotEmpty(ContactField contactField) {
    	if (contactField.getTextValue() == null) {
    		return false;
    	}
        return contactField.getTextValue().length() > 0;
    }

    public boolean hasField(long propertyUID) {
    	for(EmailAddress emailAdr: getEmails()){
    		if(emailAdr.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	
    	for(PhoneNumber phoneNum: getPhoneNumbers()){
    		if(phoneNum.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	
    	for(ContactField field: fields){
    		if(field.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	return false;
    }

    public boolean hasField(String propertyUID){
    	for(EmailAddress emailAdr: getEmails()){
    		if(emailAdr.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	
    	for(PhoneNumber phoneNum: getPhoneNumbers()){
    		if(phoneNum.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	
    	for(ContactField field: fields){
    		if(field.doesImplementID(propertyUID)){
    			return true;
    		}
    	}
    	return false;
    }

 // The UID relation is hardcoded here: http://lon-xref.intra/lxr/source/common/generic/app-engines/cntmodel/cntplsql/src/cpplcontacttable.cpp#799
    // The UID to int value is here http://lon-xref.intra/lxr/source/common/generic/app-engines/cntmodel/inc/cntdef.h#669
    public boolean hasHintField(ContactHint hint) {
    	ContactsUidMap map = TemplateMapper.getInstance().getUidMap();

    	HashMap<String, Long> flagMap = TemplateMapper.getInstance().getMappingToLong(ContactMapTypes.flags.toString());
    	
    	switch (hint) {
		case HOME:
			return hasField(map.map(HOME));

		case FAXABLE:
			return hasField(map.map(FAX));
	
		case LAND_LINE:
			// This seems a little strange but it is as in the OS
			return hasField(map.map(PAGER));
			
		case MAILABLE:
			return !getEmails().isEmpty();
			
		case PHONABLE: // does fax go into phone number
			return 	  !getPhoneNumbers().isEmpty() 
					|| hasField(map.map(FAX));

		case RING_TONE:
			/* TODO: relies on binary field
			 *  if (type.ContainsFieldType(KUidContactFieldRingTone) )
			 *	{
		     *		CContactFieldStorage* storage = aField.Storage();
         	 *		if ( storage && storage->IsFull() )
             *		{
             *		iValue |= CContactDatabase::ERingTone;
             *		}
         	 *	}
			 */
			break;
			
		case SMSABLE:
			return hasField(map.map(CELL));

		case WORK:
			return hasField(map.map(WORK));
			
		case IM_ADDRESS:
			return hasField(map.map(IM));
			
		case WIRELESS_VILLAGE:
			return hasField(map.map(IM)) 
					&& hasField(map.map(WV));
			
		case VOICE_DIAL:
			return hasField(map.map(VOICE_DIAL));
		
		case FILT1:
			return hasField(flagMap.get(FILT1));
		
		case FILT2:
			return hasField(flagMap.get(FILT2));
			
		case FILT3:
			return hasField(flagMap.get(FILT3));
			
		case FILT4:
			return hasField(flagMap.get(FILT4));
			
		default:
			break;
    	}
    	return false;
    }

	/**
	 * @param speedDialVCardPropertiesData
	 */
	public void setSpeedDialData(Set<SpeedDialData> speedDialData) {
		this.speedDialData = speedDialData;
	}

	/**
	 * @return the speedDialData
	 */
	public Set<SpeedDialData> getSpeedDialData() {
		return speedDialData;
	}
    
}
