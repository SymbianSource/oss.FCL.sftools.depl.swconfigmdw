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
// BinaryFieldHeader.java
//



package com.symbian.sdb.contacts.sqlite.model;

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.sqlite.helper.ContactFieldAttributes;
import com.symbian.sdb.contacts.template.model.HeaderTemplateField;

/**
 * Class for retain meta data for binary field headers
 */
public class FieldHeader implements HeaderTemplateField {
	
    private static final long HINT_MASK		            = 0x00FFFFFF;
    private static final long ADD_MAPPING_MASK           = 0x7F000000;
    private static final long HAS_VCARD_MAPPING_MASK     = 0x80000000;
	
	private ContactFieldAttributes attributes;
	
	private int streamId = 0;
	
	private long contactFieldGuid = -1;
	
	private ContactFieldLabel fieldLabel = new ContactFieldLabel();
	
	private int hint = 0;
	private int[] additionalFields;
	private int vCardUidValue;
	
	//private long templateId = 0; the same as field id
	private long fieldId;
	
	//TODO vCard field type object needs to be created and populated 
	//with hint and vCard mappings
	//private ContactFieldVcardType vcardType;

	// Set attribute flags
	public void setAttributes(int attributesValue) {
		attributes = new ContactFieldAttributes(attributesValue);
	}

	public ContactFieldAttributes getAttributesContainer() {
		if (attributes == null) {
			attributes = new ContactFieldAttributes();			
		}
		return attributes;
	}
	
	/**
	 * Retrieve binary field label from BinaryFieldLabel object
	 * @return
	 */
	public ContactFieldLabel getFieldLabel() {
		return fieldLabel;
	}

	/**
	 * Set field label in BinaryFieldLabel object
	 * @param fieldLabel
	 */
	public void setFieldLabel(ContactFieldLabel fieldLabel) {
		this.fieldLabel = fieldLabel;
	}
	
	// Get stream id for binary filed
	public int getStreamId() {
		return streamId;
	}
	
	// Set stream id for binary filed
	public void setStreamId(int streamId) {
		this.streamId = streamId;
	}
	
	//Get contact field GUID, an index in r_cntui_new_field_defn that identifies label and
	//vCard mapping in template
	public long getContactFieldGuid() {
		return contactFieldGuid;
	}
	
	// Set contact field GUID
	public void setContactFieldGuid(long contactFieldGuid) {
		this.contactFieldGuid = contactFieldGuid;
	}
	
	public int getHint() {
		return hint;
	}

	public void setHint(int hint) {
		this.hint = hint;
	}   

	public boolean hasVCardMapping() {
		return ((hint & HAS_VCARD_MAPPING_MASK) == HAS_VCARD_MAPPING_MASK);
	}

	public int getAdditionalFieldCount() {
		return (int)((hint & ADD_MAPPING_MASK) >> 24);
	}

	public void setAdditionalFieldCount(int count) {
		this.hint |= ((count << 24) & ADD_MAPPING_MASK);
	}
	
	public void setHintValue(int hintValue) {
		this.hint |= (hintValue & HINT_MASK);
	}
	
	public long getFieldHintValue() {
		return (hint & HINT_MASK);
	}
	
	public int getFieldVcardMapping() {
		return vCardUidValue;
	}

	public void setFieldVcardMapping(int cardUidValue) {
		this.hint |= HAS_VCARD_MAPPING_MASK;
		vCardUidValue = cardUidValue;
	}

	public void setFieldAdditionalUIDValues(int[] additionalFieldsValue) {
		additionalFields = additionalFieldsValue;
	}
	
	public int[] getFieldAdditionalUIDValues() {
		return additionalFields;
	}
	
    public long getFieldId() {
		return fieldId;
    }

	public void setFieldId(long index) {
		this.fieldId = index;
	}
	
} // end of class
