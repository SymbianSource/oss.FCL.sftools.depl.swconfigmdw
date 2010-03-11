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

package com.symbian.sdb.contacts.template;

import java.util.List;
import java.util.Map;

import com.symbian.sdb.contacts.importer.vcard.PropertyData;

public interface ITemplateModel {
	
	public final long SYSTEM_TEMPLATE_ID = 0L;
	
	/**
	 * Returns contact field type for given property.
	 * 
	 * @param propertyData
	 * @return
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract Integer getVCardMappingPropertyToContactFieldType(
			PropertyData propertyData, int fieldNo) 
	throws MultipleTemplateValueException, MappingMissingException;

	/**
	 * Returns contact field type for given property.
	 * 
	 * @param propertyData
	 * @return
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract Integer getVCardMappingPropertyToContactFieldType(
			PropertyData propertyData)
	throws MultipleTemplateValueException, MappingMissingException;
	
	/**
	 *  returns storage field type for given vCard name and properties
	 * @param propertyData
	 * @return storage field type [0..3]
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract Integer getVCardMappingPropertyToStorageFieldType(
			PropertyData propertyData, int fieldNo) 
	throws MultipleTemplateValueException, MappingMissingException;

	
	/**
	 *  returns storage field type for given vCard name and properties
	 * @param propertyData
	 * @return storage field type [0..3]
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract Integer getVCardMappingPropertyToStorageFieldType(
			PropertyData propertyData) 
	throws MultipleTemplateValueException, MappingMissingException;
	
	/**
	 * 
	 * @param propertyData
	 * @return field name e.g. STRING_r_cntui_new_field_defns48
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract String getVCardMappingPropertyToFieldName(
			PropertyData propertyData, int fieldNo) 
	throws MultipleTemplateValueException, MappingMissingException;

	/**
	 * 
	 * @param propertyData
	 * @return field name e.g. STRING_r_cntui_new_field_defns48
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract String getVCardMappingPropertyToFieldName(
			PropertyData propertyData) 
	throws MultipleTemplateValueException, MappingMissingException;
	
	/**
	 * returns the index of the field as in the resource file
	 * @param propertyData
	 * @param fieldNo
	 * @return  the index of the field as in the resource file
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract int getvCardMappingPropertyToFieldIndex(
			PropertyData propertyData, int fieldNo) 
	throws MultipleTemplateValueException, MappingMissingException;
	
	
	/**
	 * returns the index of the field as in the resource file
	 * @param propertyData
	 * @return  the index of the field as in the resource file
	 * @throws MultipleTemplateValueException if more than one field matches the property data
	 * @throws MappingMissingException TODO
	 */
	public abstract int getvCardMappingPropertyToFieldIndex(
			PropertyData propertyData)
	throws MultipleTemplateValueException, MappingMissingException;
	
	/**
	 * returns the set of maps (index and field type) for given property data 
	 * @return
	 * @throws MappingMissingException TODO
	 */
	public abstract Map<Integer, Integer> 
	getvCardMappingPropertyToFieldIndexTypeSet(PropertyData propertyData)
	throws MappingMissingException;
	
	/**
	 * checks whether the mapping is present
	 * @param propertyData
	 * @param fieldNo
	 * @return
	 * @throws MappingMissingException TODO
	 */
	public abstract boolean 
	templateContainsMappingForVCardProperty(PropertyData propertyData, int fieldNo)
	 throws MappingMissingException;
	
	/**
	 * checks whether the mapping is present
	 * @param propertyData
	 * @return
	 * @throws MappingMissingException TODO
	 */
	public abstract boolean 
	templateContainsMappingForVCardProperty(PropertyData propertyData)
	 throws MappingMissingException;
	
	/**
	 * returns the template id as stored in database
	 * @return
	 */
	public abstract long getTemplateId();
	
	/**
	 * returns the template id as stored in database
	 * @return
	 */
	public abstract void setTemplateId(long templateId);
	
	/**
	 * returns the template field as stored in database
	 * @return field container object
	 */
	public abstract FieldContainer getFields();
	
	/**
	 * 
	 * @param data
	 * @param fieldNo
	 * @return the template field denoted by the property data instance and the required field number.
	 * @throws MultipleTemplateValueException 
	 */
	public IField vCardMappingPropertyToContactField(PropertyData data, int fieldNo) throws MultipleTemplateValueException, MappingMissingException;
	
	/**
	 * 
	 * @param data
	 * @return the set of fields denoted by the property data instance.
	 * @throws MultipleTemplateValueException
	 */
    public List<IField> vCardMappingPropertyToContactFields(PropertyData data) throws MultipleTemplateValueException, MappingMissingException;

	public TemplateMapper getMapper();

    /**
     * Checks if two template model represent the same template (possibly the same RSS file).
     * Used to determine if template loaded from RSS file is same as one of templates already existing in database. 
     * 
     * @param dbTemplate
     * @return
     */
    public abstract boolean isSame(ITemplateModel dbTemplate);

}
