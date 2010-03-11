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

package com.symbian.sdb.contacts.dbms.model;

import com.symbian.sdb.contacts.model.FieldAttributes;

/**
 * 
 * @author Tanaslam1
 * Class representing contact-item-field's composite attributes
 */
public class ContactFieldAttribute implements FieldAttributes {
	
	/**
	 * Composite field attributes
	 */
	private long fieldAttributes 	= 0x0;
	
	/**
	 * Extended field attributes
	 */
	private long extendedFieldAttributes = 0x0;
	
	// ~ Bit Shift flags ======================================================
	private final int COUNT_BITSHIFT		= 18;
	private final int TYPE_BITSHIFT			= 12;
	private final int TEMPLATEID_BITSHIFT	= 22;
	
	private final int USERMASK_BITSHIFT  = 4 ; 


	// ~ Business methods =====================================================
	/**
	 * Returns field behaviour attributes from composite attributes
	 * @return An integer value contains attribute flags
	 */
	public long getAttributes() {
		return fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_ATTRIB.getValue();
	}
	
	/**
	 * Set field attributes in composite attributes 
	 * @param fieldAttributes
	 */
	public void addAttribute(long fieldAttributes) {
		this.fieldAttributes |= fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_ATTRIB.getValue();
	}

	/**
	 * Returns field storage type from composite attribute integer
	 * @return Integer value masked on storage type
	 */
	public long getFieldStorageType() {
		return (fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_STORAGETYPE.getValue()) >> TYPE_BITSHIFT;
	}

	/**
	 * Set field storage type 
	 * @param fieldType
	 */
	public void setFieldStorageType(long fieldType) {
		this.fieldAttributes |= ( fieldType << TYPE_BITSHIFT ) & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_STORAGETYPE.getValue();
	}

	/**
	 * Return number of additional fields present in contact item 
	 * @return
	 */
	public int getAdditionalFieldCount() {
		return (int) ((fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_ADDITIONALFIELDSCOUNT.getValue()) >> COUNT_BITSHIFT);
	}

	/**
	 * set additional field count in composite attribute integer
	 * @param additionalFieldCount
	 */
	public void setAdditionalFieldCount(int additionalFieldCount) {
		this.fieldAttributes |= ( additionalFieldCount << COUNT_BITSHIFT )& ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_ADDITIONALFIELDSCOUNT.getValue();
	}

	/**
	 * get temple field id on which field gets mapped
	 * @return
	 */
	public long getTemplateId() {
		return (fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_TEMPLATEID.getValue()) >> TEMPLATEID_BITSHIFT ;
	}

	/**
	 * set template field id for contact item field 
	 * @param templateFieldId
	 */
	public void setTemplateId(long templateFieldId) {
		this.fieldAttributes |= ( templateFieldId << TEMPLATEID_BITSHIFT ) & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_TEMPLATEID.getValue();
		
	}

	/**
	 * Return integer value represent bitwise filed attributes, type, 
	 * additional field count and template field id
	 * @return
	 */
	public long getCompositeAttributes() {
		return fieldAttributes;
	}

	/**
	 * set composite attribute value
	 * @param fieldAttributes
	 */
	public void setCompositeAttributes(long fieldAttributes) {
		this.fieldAttributes = fieldAttributes;
	}

	/**
	 * Return integer value representing extended attribute flags 
	 * @return
	 */
	public long getExtendedAttributes() {
		return extendedFieldAttributes;
	}

	/**
	 * Set extended attribute for contact item field
	 * @param extendedFieldAttributes
	 */
	public void setExtendedAttributes(long extendedFieldAttributes) {
		this.extendedFieldAttributes = extendedFieldAttributes;
	}
	/**
	 * Add extended attribute bit flag in extended attributes value. 
	 * @param extendedFieldAttributes
	 */
	public void addExtendedAttribute(long extendedFieldAttributes) {
		this.extendedFieldAttributes |= extendedFieldAttributes;
	}
	
	/**
	 * Return user flags
	 * @return
	 */
	public byte getCategory() {
		return (byte) ((this.fieldAttributes & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_CATEGORY.getValue()) >> USERMASK_BITSHIFT);
	}

	/**
	 * Set user flags for contact-item field
	 * @param fieldCategory
	 */
	public void setCategory(byte fieldCategory) {
		this.fieldAttributes |= ((fieldCategory << this.USERMASK_BITSHIFT ) & ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_CATEGORY.getValue());
	}

	
}// end of class
