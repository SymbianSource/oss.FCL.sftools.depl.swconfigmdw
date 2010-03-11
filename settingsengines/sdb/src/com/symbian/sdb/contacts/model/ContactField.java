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

import com.symbian.sdb.contacts.template.Flag;
import com.symbian.sdb.contacts.template.IField;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactField {

    private byte[] value;
	private IField templateField;
    
    public static ContactField newTextFieldInstance(String value, IField templateField)	{
    	return new ContactField(value.getBytes(), templateField);
    }
    
    public static ContactField newBinaryFieldInstance(byte[] value, IField templateField)	{
    	return new ContactField(value, templateField);
    }

    public ContactField(byte[] value, IField templateField) {
        super();
    	
        this.value = value;
        this.templateField = templateField;
    }

    /**
     * Should only be used for text fields e.g. first name
     * 
     * @return
     */
    public String getTextValue() {
        return new String(value);
    }

    /**
     * Should only be used for binary fields e.g. photo
     * 
     * @return
     */
    public byte[] getBinaryValue() {
        return value;
    }

    public int getTemplateFieldId() {
        return templateField.getIndex();
    }

	/**
	 * @param propertyUID 
	 * @return true if the ID matches with the ID provided by the template field
	 */
	public boolean doesImplementID(String propertyUID) {
		//checks the field type matches
		if (doIDsMatch(propertyUID, templateField.getFieldType())){
			return true;
		}
		
		//checks the extra mappings / vcard properties contains property
		if (isIDSupportedByField(propertyUID, templateField)) {
			return true;
		}

		return false;
	}
	
	public boolean doesImplementID(long propertyUID) {
		for (Flag flag : templateField.getFlags()) {
			if (flag.getValue() == propertyUID) {
				return true;
			}
		}
		return false;
	}
	
	/**
	 * @param id1 the first ID to match against
	 * @param id2 the second ID to match against
	 * @return true if the two IDs correspond to the same property
	 */
	private boolean doIDsMatch(String id1, String id2) {
		return id1.equals(id2);
	}

	/**
	 * 
	 * @param uid
	 * @param field
	 * @return
	 */
	private boolean isIDSupportedByField(String uid, IField field){
		for(String mapping: field.getProperties()){
			if(doIDsMatch(uid, mapping)){
				return true;
			}
		}
		return false;
	}
	
	public Byte getCategory()   {
	    return templateField.getCategory();
	}
}
