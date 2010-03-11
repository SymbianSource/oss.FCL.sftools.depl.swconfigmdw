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

package com.symbian.sdb.contacts.sqlite.helper;

import com.symbian.sdb.contacts.model.FieldAttributes;
import com.symbian.sdb.contacts.sqlite.BitsOperationsUtil;
import com.symbian.sdb.contacts.sqlite.model.ContactFieldAttribute;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactFieldAttributes;

/**
 * 
 * @author krzysztofZielinski
 *
 */
public class ContactFieldAttributes implements FieldAttributes {

    private static final int ATTRIBUTE_MASK             = 0xF0000FFF;
    private static final int STORAGE_TYPE_MASK          = 0x00F00000;
    private static final int EXTENDED_ATTRIBUTES_MASK   = 0x000FF000;
    
    private int contactFieldAttributes = 0;

    public ContactFieldAttributes() {
    }
    
    public ContactFieldAttributes(int value) {
    	contactFieldAttributes = value;
    }

    public void resetAttributes()   {
        contactFieldAttributes = 0;
    }
    
    public int getValue()  {
        return contactFieldAttributes;
    }

    public void addAttribute(SQLiteContactFieldAttributes sqLiteContactFieldAttributes)  {
        int attributeIntegerValue = mapAttributesToInteger(sqLiteContactFieldAttributes); 
        maskAndSetValue(attributeIntegerValue, ATTRIBUTE_MASK); 
    }
    
    public void addAttribute(ContactFieldAttribute attribute) {
    	contactFieldAttributes |= (attribute.getValue() & ATTRIBUTE_MASK);
    }

    public void addAttribute(Integer attribute) {
    	contactFieldAttributes |= (attribute & ATTRIBUTE_MASK);
    }
    
    private void maskAndSetValue(int value, int mask) {
        int maskedValue = maskValue(value, mask);         
        setFlag(maskedValue);
    }

    /**
     * Maps attributes short value (16bit) to int (32bit): short(ABCD)->int(A0000BCD) where each 2 chars represent one byte (in hex like notation)  
     * 
     * @param sqLiteContactFieldAttributes
     * @return
     */
    private int mapAttributesToInteger(SQLiteContactFieldAttributes sqLiteContactFieldAttributes) {
        short attributeShortValue = sqLiteContactFieldAttributes.getValue();
        
        byte higherByteToMap = BitsOperationsUtil.getHigherByte(attributeShortValue);
        byte lowerByteToMap = BitsOperationsUtil.getLowerByte(attributeShortValue);
        
        // first byte is the highest byte
        byte firstByte = (byte) (higherByteToMap & 0xF0);
        byte secondByte = 0x00;
        byte thirdByte = (byte) (higherByteToMap & 0x0F);
        byte fourthByte = lowerByteToMap;
        
        int attributeInteger = BitsOperationsUtil.getIntFormBytes(firstByte, secondByte, thirdByte, fourthByte);
        
        return attributeInteger;
    }

    private void setFlag(int attribute) {
        contactFieldAttributes |= attribute;
    }

    private int maskValue(int attribute, int mask) {
        return mask & attribute;
    }
    
    public void addExtendedAttributes(long extendedAttributes) {
    	contactFieldAttributes |= ((extendedAttributes << 12) & EXTENDED_ATTRIBUTES_MASK);
    }
    
	/**
	 * Get extended attributes of field 
	 * @return
	 */
	public long getExtendedAttributes() {
		return contactFieldAttributes & EXTENDED_ATTRIBUTES_MASK;
	}

    public void setStorageType(long storageType) {
    	contactFieldAttributes |= ((storageType << 20) & STORAGE_TYPE_MASK);
    }
	
	/**
	 * Get field storage type 
	 * @return Storage type
	 */
	public long getFieldStorageType() {
		return (contactFieldAttributes & STORAGE_TYPE_MASK) >> 20;
	}
    
	public long getAttributes() {
		return contactFieldAttributes & ATTRIBUTE_MASK;
	}
	
	public void setCategory(byte category) {
		contactFieldAttributes &= ~ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERMASKED.getValue();
		contactFieldAttributes |= ((category << 4) & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERMASKED.getValue());
	}
	
	public byte getCategory() {
		return (byte)((contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERMASKED.getValue()) >> 4);
	}
	
	//True if Override label flag is set
	public boolean hasOverridenLabel() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_OVERIDELABEL.getValue()) > 0);
	}

	public boolean usesTemplateData() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USETEMPLATEDATA.getValue()) > 0);
	}
	
	public boolean isHidden() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_HIDDEN.getValue()) > 0);
	}
	
	public boolean isSyncable() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_SYNCH.getValue()) > 0);
	}
	
	public boolean isDisabled() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DISABLED.getValue()) > 0);
	}
	
	public boolean hasUserMask() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERMASKED.getValue()) > 0);
	}
	
	public boolean hasTemplateMask() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_TEMPLATEMASK.getValue()) > 0);
	}
	
	public boolean isUserAddedField() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_USERADDEDFIELD.getValue()) > 0);
	}
	
	public boolean isTemplate() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_TEMPLATE.getValue()) > 0);
	}
	
	public boolean labelUnspecified() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_LABELUNSPECIFIED.getValue()) > 0);
	}
	
	public boolean isDeleted() {
		return ((this.contactFieldAttributes & ContactFieldAttribute.SQLITE_CONTACT_FIELD_ATT_DELETED.getValue()) != 0);
	}
    
}
