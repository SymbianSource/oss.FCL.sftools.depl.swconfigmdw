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

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.template.model.HeaderTemplateField;


/**
 * Class structure for storing contact-item field
 * @author Tanaslam1
 *
 */
public class ContactFieldHeader implements HeaderTemplateField {

	private static final int FIELD_ID_BITSHIFT = 22;
	/**
	 * Composite attribute structure containing field and extended attributes 
	 */
	private ContactFieldAttribute attributes = new ContactFieldAttribute();
	/**
	 * Stream Id of data store in blob column, only exist if field type is non-text 
	 */
	private long streamId = -1;
	
	/**
	 * Field's hint value 
	 */
	private long fieldHint = -1;
	
	/**
	 * Field's additional UID values (custom value) 
	 */
	private int[] fieldAdditionalUIDValues = null;
	
	/**
	 *Field's vCard mapping  
	 */
	private int fieldVcardMapping = -1;
	
	/**
	 * Contact item field label 
	 */
	private ContactFieldLabel fieldLabel = new ContactFieldLabel();
	
	// ~ Constructors ==========================================================
	public ContactFieldHeader() {
		super();
	}
	
	
	// ~ Business Methods ====================================================== 
	/**
	 * 
	 * @return
	 */
	public ContactFieldAttribute getAttributesContainer() {
		return attributes;
	}
	
	/**
	 * 
	 * @param attributes
	 */
	public void setAttributesContainer(ContactFieldAttribute attributes) {
		this.attributes = attributes;
	}
	
	/**
	 * 
	 * @return
	 */
	public long getStreamId() {
		return streamId;
	}
	
	/**
	 * 
	 * @param streamId the ID of the store stream containing the field data.
	 */
	public void setStreamId(long streamId) {
		this.streamId = streamId;
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
	 * @param label
	 */
	public void setFieldLabel(ContactFieldLabel label) {
		this.fieldLabel = label;
	}

	/**
	 * Return contact-item field hint value
	 * @return
	 */
	public long getFieldHint() {
		return fieldHint;
	}

	public long getFieldHintValue() {
		return fieldHint & ContactFieldHintMask.DBMS_CONTACT_FIELD_MASK_HINT.getValue();
	}
	
	/**
	 * Set hint value for contact-item field this clears the id and "has additional mapping flags";
	 * @param fieldHint
	 */
	public void setFieldHint(long fieldHint) {
		this.fieldHint = fieldHint;
	}
	

	
	/**
	 * Perform test whether flag for override label is set  
	 * @return True if Override label flag is set
	 */
	public boolean hasOverridenLabel() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_OVERIDELABEL.getValue()) > 0);
	}
	
	/**
	 * Test if field uses template data
	 * @return True if flag is set
	 */
	public boolean usesTemplateData() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_USETEMPLATEDATA.getValue()) > 0);
	}
	
	/**
	 * Test if field is hidden
	 * @return True if this flag is set
	 */
	public boolean isHidden() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_HIDDEN.getValue()) > 0);
	}
	
	/**
	 * Test if field is being used in contact synchronisation 
	 * @return True if this flag is set
	 */
	public boolean isSyncable() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_SYNCH.getValue()) > 0);
	}
	
	/**
	 * Test if field is marked disabled
	 * @return True if this flag is set
	 */
	public boolean isDisabled() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_DISABLED.getValue()) > 0);
	}
	
	/**
	 * Test if field has category value 
	 * @return True if this flag is set else false
	 */
	public boolean hasUserMask() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_CATEGORY.getValue()) > 0);
	}
	
	/**
	 * Test if field contains template mask
	 * @return True if this flag is set else false
	 */
	public boolean hasTemplateMask() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_TEMPLATEMASK.getValue()) > 0);
	}
	
	/**
	 * Test if field is user-added field
	 * @return True if this flag is set else false
	 */
	public boolean isUserAddedField() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_USERADDEDFIELD.getValue()) > 0);
	}
	
	/**
	 * Test if field is template field
	 * @return True if this flag is set else false
	 */
	public boolean isTemplate() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_TEMPLATE.getValue()) > 0);
	}
	
	/**
	 * Test whether label is specified
	 * @return True if this flag is set else false
	 */
	public boolean labelUnspecified() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_LABELUNSPECIFIED.getValue()) > 0);
	}
	
	/**
	 * Test if field has been deleted
	 * @return True if this flag is set else false
	 */
	public boolean isDeleted() {
		return ((this.attributes.getAttributes() & 
				ContactFieldAttributeFlag.DBMS_CONTACT_FIELD_ATT_DELETED.getValue()) > 0);
	}
	
	/**
	 * Test if field is of text type
	 * @return True if this flag is set else false
	 */ 
	public boolean isTextType() {
		//TODO field type values should be retrieved from contacts.xml
		return (this.attributes.getFieldStorageType() == 0);
	}

	/**
	 * Test if field has binary type
	 * @return True if this flag is set else false
	 */
	public boolean isBinaryType() {
		//TODO field type values should be retrieved from contacts.xml
		return (this.attributes.getFieldStorageType() == 1);
	}
	
	/**
	 * ???
	 * @return True if this flag is set else false
	 */
	public boolean isContactIdType() {
		//TODO field type values should be retrieved from contacts.xml
		return (this.attributes.getFieldStorageType() == 2);
	}
	
	
	/**
	 * Test if field is of Date type
	 * @return True if this flag is set else false
	 */
	public boolean isDateType() {
		//TODO field type values should be retrieved from contacts.xml
		return (this.attributes.getFieldStorageType() == 3);
	}

	/**
	 * Get additional UID values for the field
	 * @return 
	 */
	public int[] getFieldAdditionalUIDValues() {
		return fieldAdditionalUIDValues;
	}

	/**
	 * Set additional field UIDs for the contact field 
	 * @param fieldAdditionalUIDValues
	 */
	public void setFieldAdditionalUIDValues(int[] fieldAdditionalUIDValues) {
		this.fieldAdditionalUIDValues = fieldAdditionalUIDValues;
	}
	
	/**
	 * @return true if any additional uid values have been set (vCard or contact type)
	 */
	public boolean hasAdditionalVCardMappings() {
		return (this.fieldHint & ContactFieldHintMask.DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS.getValue()) > 0;
	}

	/**
	 * Get vCard mapping for this field
	 * @return
	 */
	public int getFieldVcardMapping() {
		return fieldVcardMapping;
	}

	/**
	 * Set vCard mapping for this field
	 * @param fieldVcardMapping
	 */
	public void setFieldVcardMapping(int fieldVcardMapping) {
		this.fieldVcardMapping = fieldVcardMapping;
	}

    /**
     * Set template field index in hint field
     * @param fieldIndex field id
     */
    public void setFieldId(int fieldIndex) {
        this.fieldHint |= fieldIndex << FIELD_ID_BITSHIFT;
    }
	
    public long getFieldId() {
    	return ((this.fieldHint & ContactFieldHintMask.DBMS_CONTACT_FIELD_MASK_INDEX.getValue()) >> FIELD_ID_BITSHIFT);
    }
    
	 /**
     * Test if hint field has addition UIDs flag set 
     */
    public void setFieldHasAdditionalUIDs(){
    	 this.fieldHint |= ContactFieldHintMask.DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS.getValue();
    }
}
