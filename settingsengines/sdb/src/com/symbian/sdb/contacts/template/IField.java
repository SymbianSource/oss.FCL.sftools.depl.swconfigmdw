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
import java.util.Set;
/**
 * Template FIELD interface
 *
 */
public interface IField extends Comparable<IField> {

	/**
	 * 
	 * @return the index of the FIELD in the template
	 */
	public abstract Integer getIndex();
	
	/**
	 * 
	 * @return storage type
	 */
	public abstract Integer getStorageType();
	
	
	public abstract boolean isBinary();
	
	
	public abstract boolean isText();
	
	public abstract boolean isAgent();
	
	/**
	 * 
	 * @return category
	 */
	public abstract Byte getCategory();
	
	/**
	 * 
	 * @return list of flags
	 */
	public abstract List<Flag> getFlags();

	/**
	 * sets the mapping for FIELD parameter values
	 * @param map
	 */
	public abstract void setMapping(IFieldMapping map);
	
	/**
	 * 
	 * @return the field type as in resource file
	 */
	public abstract String getFieldType();
	
	/**
	 * 
	 * @return the vCard mapping as in resource file
	 */
	public abstract String getVCardMapping();
	
	/**
	 * 
	 * @return field name as in resource file
	 */
	public abstract String getFieldName();
	
	/**
	 * 
	 * @return vCard properties as in resource file extra mapping
	 */
	public abstract Set<String> getProperties();
	
	/**
	 * 
	 * @return contact field type value as in database
	 */
	public abstract Integer getFieldTypeValue() throws MappingMissingException;
	
	/**
	 * 
	 * @return vCard name value as in database
	 */
	public abstract Integer getVCardMappingValue() throws MappingMissingException;
	
	/**
	 * 
	 * @return vCard properties as in database
	 */
	public abstract List<Integer> getPropertiesValue() throws MappingMissingException;
	
	/**
	 * 
	 * @return label, as in database
	 */
	public abstract String getFieldNameValue() throws MappingMissingException;

    /**
     * Checks if fields represents the same data. Used to compare templates.
     * Synchronized flags are skipped as cntmodel modifies them 
     * @param otherField
     * @return
     */
    public boolean isSame(IField otherField); 
}