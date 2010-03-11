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

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.log4j.Logger;

import com.symbian.sdb.contacts.importer.vcard.PropertyData;

/**
 * Template model class used by vCard parsing utilities to transform vCard into Contact
 */
public class TemplateModel implements ITemplateModel {
	
	private TemplateMapper mapper;
	private FieldContainer memory;
	private long templateId;
	
	private static final Logger logger = Logger.getLogger(TemplateModel.class);
	
	public TemplateModel(TemplateMapper mapper, FieldContainer model) {
		this.memory = model;
		this.mapper = mapper;
	}
	
	/**
	 * 
	 * @param vCardParams The set of vCard parameters to translate into the set of contact model IDs
	 * @return the set of contacts model IDs for the set of vCard parameters. Never null. 
	 * @throws MappingMissingException if one of the vCard parameters has no corresponding ID
	 */
	private Set<String> mapVCardProperties(Set<String> vCardParams) throws MappingMissingException {
    	Set<String> vCardParamsMapping = new HashSet<String>();
    	if (vCardParams != null) {
    		for (String param : vCardParams) {
    			vCardParamsMapping.add(mapper.getMappingFromvCard(param, 0));
    		}
    	}
    	return vCardParamsMapping;
	}
	
	/**
	 * 
	 * @param vCardProperty. The main vCard field identifier. For example TEL 
	 * @param vCardParams. The set of vCard parameters defining the property. For example HOME;VOICE;CELL
	 * @param failForMultiple. Set to true if the field is not structured. If the field has multiple matches the MultipleTemplateValueException is thrown
	 * @param fieldNo. The field number of the relevant field if the property represents a structured field
	 * @return The list of matched fields from the template. If none, an empty list is returned. Never null.
	 * @throws MultipleTemplateValueException thrown if the template matches multiple fields and the failForMultiple flag is true
	 * @throws MappingMissingException thrown if the vCard property/parameters don't have a mapping to the contacts model id's (found in the contacts xml configuration file).
	 */
    private List<IField> getFieldsFromVCardParameters(
    		String vCardProperty, 
    		Set<String> vCardParams,
    		boolean failForMultiple,
    		int fieldNo)
    throws MultipleTemplateValueException, MappingMissingException {

    	// For a given vCard property get the set of fields
    	//
		Collection<IField> propertyFields = memory.get(vCardProperty, fieldNo);
		
    	// Convert the list of vCard parameters into the template identifiers
    	//
    	Set<String> vCardParamsMapping = mapVCardProperties(vCardParams);
		
		List<IField> result = new ArrayList<IField>();
		
    	// Iterate through the each of the template fields represented by
		// the vCard property
		//
		for (IField field : propertyFields) {
	    	Set<String> values = new HashSet<String>(field.getProperties());
	    	
	    	// For each attempt to match the template values against the 
	    	// vCard parameters - order is not important
	    	//
	        if (values.equals(vCardParamsMapping)) {
	        	
	            if (failForMultiple && result.size() > 0) {
	            	throw new MultipleTemplateValueException("More than one match for '" + vCardProperty + "' and given properties");
	            } else {
	            	result.add(field);
	            }
	        }
	         else {
	        	 logger.debug("vCard parameters don't match for field: "+ field.getFieldName()+ " Index: "+field.getIndex());
	        	 logger.debug("vCard parameters : " + vCardParamsMapping);
	        	 logger.debug("Field parameters : " + values);
			}
    	}	
    	if(result.size() == 0){
    		logger.debug("No mapping found for "+ formatForMessage(vCardProperty, vCardParams));
    	}
    	return result;
    }
    
    /**
	 * @param cardProperty The vCardProperty to be described
	 * @param cardParams The set of vCardParameters to be listed
	 * @return describes the vCard property and parameters in a readable string
	 */
	private String formatForMessage(String cardProperty, Set<String> cardParams) {
		StringBuilder messageBuilder = new StringBuilder(cardProperty);
		for(String parameter: cardParams){
			messageBuilder.append(";").append(parameter);
		}
		return messageBuilder.toString();
	}

	private IField getField(PropertyData data, int fieldNo) 
    throws MultipleTemplateValueException, MappingMissingException {
    	IField result = null;
    	List<IField> list = getFieldsFromVCardParameters(data.getName(), data.getParameters(), true, fieldNo);
    	if (list != null && list.size() == 1) {
    		result = list.iterator().next();
    	}
    	return result;
    }
    
    private List<IField> getFields(PropertyData data) throws MultipleTemplateValueException, MappingMissingException {
    	List<IField> list = getFieldsFromVCardParameters(data.getName(), data.getParameters(), false, 0);
    	//TODO: not guarenteed to work.
    	List<IField> fields = new ArrayList<IField>();
    	for(IField field: list) {
    		fields.add(field);
    	}
    	Collections.sort(fields);
    	return fields;
    }
    
    /* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.ITemplateManager#getVCardMappingPropertyToContactFieldType(com.symbian.sdb.contacts.importer.vcard.PropertyData)
	 */
    public Integer getVCardMappingPropertyToContactFieldType(PropertyData data, int fieldNo)
    throws MultipleTemplateValueException, MappingMissingException {
    	Integer result = null;
    	IField field = getField(data, fieldNo);
    	if (field != null) {
    		result = field.getFieldTypeValue();
    	}
    	return result;
    }

    public IField vCardMappingPropertyToContactField(PropertyData data, int fieldNo) throws MultipleTemplateValueException, MappingMissingException {
    	return getField(data, fieldNo);
    }
    public List<IField> vCardMappingPropertyToContactFields(PropertyData data)
    throws MultipleTemplateValueException, MappingMissingException {
    	return getFields(data);
    }
    
	public Integer getVCardMappingPropertyToContactFieldType(
			PropertyData propertyData) throws MultipleTemplateValueException, MappingMissingException {
		return getVCardMappingPropertyToContactFieldType(propertyData, 0);
	}
    
    /* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.ITemplateManager#getVCardMappingPropertyToStorageFieldType(com.symbian.sdb.contacts.importer.vcard.PropertyData)
	 */
    public Integer getVCardMappingPropertyToStorageFieldType(PropertyData data, int fieldNo) 
    throws MultipleTemplateValueException, MappingMissingException {
    	Integer result = null;
    	IField field = getField(data, fieldNo);
    	if (field != null) {
    		result = field.getStorageType();
    	}
    	return result;
    }
    
	public Integer getVCardMappingPropertyToStorageFieldType(
			PropertyData propertyData) throws MultipleTemplateValueException, MappingMissingException {
		return getVCardMappingPropertyToStorageFieldType(propertyData, 0);
	}
    
    /* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.ITemplateManager#getVCardMappingPropertyToFieldName(com.symbian.sdb.contacts.importer.vcard.PropertyData)
	 */
    public String getVCardMappingPropertyToFieldName(PropertyData data, int fieldNo) 
    throws MultipleTemplateValueException, MappingMissingException {
    	String result = null;
    	IField field = getField(data, fieldNo);
    	if (field != null) {
    		result = field.getFieldNameValue();
    	}
    	return result;
    }
    
	public String getVCardMappingPropertyToFieldName(
			PropertyData propertyData) throws MultipleTemplateValueException, MappingMissingException {
		return getVCardMappingPropertyToFieldName(propertyData, 0);
	}
    
	public int getvCardMappingPropertyToFieldIndex(PropertyData data, int fieldNo) 
	throws MultipleTemplateValueException, MappingMissingException {
    	int result = -1;
    	IField field = getField(data, fieldNo);
    	if (field != null) {
    		result = field.getIndex();
    	}
    	return result;
	}
	
	public int getvCardMappingPropertyToFieldIndex(PropertyData propertyData) 
	throws MultipleTemplateValueException, MappingMissingException {
		return getvCardMappingPropertyToFieldIndex(propertyData, 0);
	}
	
	public Map<Integer, Integer> getvCardMappingPropertyToFieldIndexTypeSet(PropertyData data)
	throws MappingMissingException { 
		List<IField> list = null;
		try {
			list = getFieldsFromVCardParameters(data.getName(), data.getParameters(), false, 0);
		} catch (MultipleTemplateValueException e) {
    		logger.warn(e.getMessage());
    	}
    	if (list == null || list.size() == 0) {
    		return null;
    	} else {
    		HashMap<Integer, Integer> map = new HashMap<Integer, Integer>();
    		for (IField m : list) {
    			Integer index = m.getIndex();
    			String type = m.getFieldType();
    			map.put(index, mapper.getFieldType(type));
    		}
    		return map;
    	}
	}

    
    /* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.ITemplateManager#templateContainsMappingForVCardProperty(com.symbian.sdb.contacts.importer.vcard.PropertyData)
	 */
    public boolean templateContainsMappingForVCardProperty(PropertyData propertyData, int fieldNo) 
    throws MappingMissingException { 
    	// for example for vCard property: TEL;WORK;VOICE:(111) 555-1212
        // propertyData.getName() = TEL - data mapped from vCardMapping
        // propertyData.getParameters() = [WORK,VOICE] - data mapped from extra mapping
    	List<IField> list = null;
    	try {
    		list = getFieldsFromVCardParameters(propertyData.getName(), propertyData.getParameters(), false, fieldNo);
    	} catch (MultipleTemplateValueException e) {
    		logger.warn(e.getMessage());
    	}
    	if (list == null || list.size() == 0) {
    		return false;
    	} else {
    		return true;
    	}
    }
    
    public boolean templateContainsMappingForVCardProperty(PropertyData propertyData) 
    throws MappingMissingException{
    	return templateContainsMappingForVCardProperty(propertyData, 0);
    }
    
    public void setTemplateId(long templateId) {
    	this.templateId = templateId;
    }
    
    public long getTemplateId() {
    	return templateId;
    }

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.ITemplateModel#getFields()
	 */
	public FieldContainer getFields() {
		return memory;
	}
	
	public TemplateMapper getMapper() {
		return mapper;
	}

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.template.ITemplateModel#isSame(com.symbian.sdb.contacts.template.ITemplateModel)
     */
    public boolean isSame(ITemplateModel dbTemplate) {
        if (dbTemplate instanceof TemplateModel) {
            FieldContainer dbTemplateMemory = ((TemplateModel)dbTemplate).memory;
            return isSameMemory(dbTemplateMemory);
        } else {
            return false;
        }
    }

    /**
     * Checks if fields in fieldContainers (in given and current templates) are equal 
     * 
     * @param dbTemplateMemory
     * @return
     */
    private boolean isSameMemory(FieldContainer dbTemplateMemory) {
        if (this.memory.getSize() != dbTemplateMemory.getSize())    {
            return false;
        }
        for (Iterator<IField> thisMemoryIterator = this.memory.iterator(), dbTemplateMemoryIterator = dbTemplateMemory.iterator();
                thisMemoryIterator.hasNext();) {
            IField thisTemplateField = thisMemoryIterator.next();
            IField dbTemplateField = dbTemplateMemoryIterator.next();
            if (!thisTemplateField.isSame(dbTemplateField)) {
                return false;
            }
        }
        return true;
    }
}
