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
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

import org.apache.log4j.Logger;

public class Field implements IField {
	private static final Logger logger = Logger.getLogger(Field.class);
	
	Integer index;
	String vCardMapping;

	String fieldName;
	
	private Integer storageType;
	String fieldType;
	Byte category;
	
	List<Flag> flags = new ArrayList<Flag>();

	Set<String> properties = new LinkedHashSet<String>();
	
	private IFieldMapping map;

	public void setMapping(IFieldMapping map) {
		this.map = map;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getStorageType()
	 */
	public Integer getStorageType() {
		return storageType;
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setStorageType(java.lang.String)
	 */
	public void setStorageType(String storageType) {
		if (storageType != null) {
			try {
				this.storageType = Integer.parseInt(storageType);
			} catch (NumberFormatException ex) {
				logger.warn("Mapping missing for " + storageType);
			}
		} 
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getFieldType()
	 */
	public String getFieldType() {
		return fieldType;
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setFieldType(java.lang.String)
	 */
	public void setFieldType(String fieldType) {
		this.fieldType = fieldType;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getVCardMapping()
	 */
	public String getVCardMapping() {
		return vCardMapping;
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setVCardMapping(java.lang.String)
	 */
	public void setVCardMapping(String cardMapping) {
		vCardMapping = cardMapping;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getCategory()
	 */
	public Byte getCategory() {
		return category;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setCategory(java.lang.String)
	 */
	public void setCategory(Byte category) {
			this.category = category;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setCategory(java.lang.String)
	 */
	public void setCategory(String category) {
		if (category != null) {
			this.category = Byte.parseByte(category);
		}
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getFieldName()
	 */
	public String getFieldName() {
		return fieldName;
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setFieldName(java.lang.String)
	 */
	public void setFieldName(String fieldName) {
		this.fieldName = fieldName;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getFlags()
	 */
	public List<Flag> getFlags() {
		return flags;
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#addFlag(java.lang.String)
	 */
	public void addFlag(Flag flag) {
		if (flag != null) {
			flags.add(flag);
		}
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getProperties()
	 */
	public Set<String> getProperties() {
		return properties;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#addProperty(java.lang.String)
	 */
	public void addProperty(String property) {
		if (properties.contains(property)) {
			logger.debug("Property " + property 
					+ " is declared multiple times for " + getVCardMapping()
					+ ". Successive declarations are ignored.");
		}
		properties.add(property);
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#getIndex()
	 */
	public Integer getIndex() {
		return index;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.template.IField#setIndex(java.lang.Integer)
	 */
	public void setIndex(Integer index) {
		this.index = index;
	}
	
	
	public Integer getFieldTypeValue() throws MappingMissingException {
		return map.getFieldType(fieldType);
	}
	
	public Integer getVCardMappingValue() throws MappingMissingException {
		return map.getValueFromvCardMapping(vCardMapping);
	}
	
	public List<Integer> getPropertiesValue() throws MappingMissingException {
		List<Integer> set = new LinkedList<Integer>();
		for (String property : properties) {
			Integer mappedValue = map.getValueFromvCardMapping(property);
			set.add(mappedValue);
		}
		return set;
	}
	
	public String getFieldNameValue() throws MappingMissingException {
		return map.getLabel(fieldName);
	}
	
	public int compareTo(IField field) {
		return this.index - field.getIndex();
	}
	
	public void setStorageType(Integer storageType) {
		this.storageType = storageType;
	}

    public boolean isSame(IField field) {
        boolean equals = true;

        equals &= this.index.equals(field.getIndex());
        equals &= this.vCardMapping.equals(field.getVCardMapping());
        equals &= this.fieldName.equals(field.getFieldName());
        equals &= isSameFieldTypes(field);
        equals &= this.category.equals(field.getCategory());
        equals &= areFlagsEqual(field.getFlags());
        equals &= arePropertiesEqual(field.getProperties());
        equals &= storageType.equals(field.getStorageType());
        
        return equals;
    }

    private boolean isSameFieldTypes(IField field) {
        if ((null != this.fieldType) && (null != field.getFieldType())) {
            return this.fieldType.equals(field.getFieldType());    
        } else {
            return true;
        }
    }

    boolean arePropertiesEqual(Set<String> otherProperties) {
    	return properties.equals(otherProperties);
    }
    
    boolean areFlagsEqual(List<Flag> otherFlags) {
    	Set<Integer> localFlags = toIntegerSet(flags);
    	
    	Set<Integer> comparingFlags = toIntegerSet(otherFlags);

    	return (localFlags.equals(comparingFlags));
    }

	private Set<Integer> toIntegerSet(List<Flag> flags) {
		Set<Integer> flagsSet = new HashSet<Integer>();
		for (Flag flag : flags) {
			//ignore the synchronize flag as cnt model always sets it
    		if (!flag.getUID().toLowerCase().matches(".*synchronize.*")) {
    			flagsSet.add(flag.getValue());
    		}
    	}
		return flagsSet;
	}

	public boolean isBinary() {
		return storageType.equals(1) || storageType.equals(3);
	}
	
	public boolean isText() {
		return storageType.equals(0);
	}
    
	public boolean isAgent() {
		return storageType.equals(2);
	}
	
}
