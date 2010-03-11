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

import java.util.Collection;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.log4j.Logger;

import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Multimap;

public class FieldContainer implements IFieldMapping, Iterable<IField> {

	protected Multimap<String, IField> map = new ArrayListMultimap<String, IField>();
    protected Map<Integer, IField> sortOrder = new LinkedHashMap<Integer, IField>();
	private static final Logger logger = Logger.getLogger(FieldContainer.class);
	
    private TemplateMapper mapper;
   
    private boolean onlyText = false;
    
	private class FieldIterator implements Iterator<IField>{
	    
		Map<Integer, IField> sortOrder;
		Iterator<Integer> iter;
		
		public FieldIterator(Map<Integer, IField> list){
			sortOrder = list;
			iter = sortOrder.keySet().iterator();
		}

		public boolean hasNext() {
			return iter.hasNext();
		}

		public IField next() {
			return sortOrder.get(iter.next());
		}

		public void remove() {
			throw new UnsupportedOperationException("Cannot remove from a NodeList");
		}
		
	}
    
	public Iterator<IField> iterator() {
		return new FieldIterator(sortOrder);
	}
    
    public void setMapper(TemplateMapper mapper) {
    	this.mapper = mapper; 	
    }
    
    /**
     * adds a FIELD 
     * @param key vCard name, e.g. KIntContactFieldVCardMapCOUNTRY
     * @param field FIELD structure
     */
    public void add(String key, Field field) {
    	if (!onlyText || (field.getStorageType() != null && field.getStorageType() == 0)) {
        	field.setMapping(this);
     //   	field.setIndex(sortOrder.size());
        	map.put(key, field);
        	sortOrder.put(field.getIndex(), field);
    	} else {
    		logger.debug("Only storage type text supported. Field '" + field.getFieldType() + "' ignored");
    	}
    }
 

    /**
     * @param key vCard name mapped to UID, e.g. KIntContactFieldVCardMapCOUNTRY
     * @return the collection of fields for given vCard mapping
     */
    public Collection<IField> get(String key) {
    	return map.get(key);
    }
    
    /**
     * 
     * @param key vCard name, eg. ADR
     * @param structuredField index of the structured field, 0 if irrelevant
     * @return
     */
    public Collection<IField> get(String key, Integer structuredField) throws MappingMissingException {
    	String mappedValue = mapper.getMappingFromvCard(key, structuredField);
    	return map.get(mappedValue);
    }
    
    /**
     * 
     * @param index index of the field in the template
     * @return FIELD structure
     */
    public IField get(Integer index) {
    	return sortOrder.get(index);
    }
    
    /**
     * @return count of FIELDs
     */
    public int getSize() {
    	return sortOrder.size();
    }

    public Integer getFieldType(String key) throws MappingMissingException {
    	return mapper.getFieldType(key);
	}

	public String getLabel(String key) throws MappingMissingException {
		return mapper.getLabel(key);
	}

	public Integer getValueFromvCardMapping(String key) throws MappingMissingException {
		return mapper.getValueFromvCardMapping(key);
	}

	public void setOnlyText(boolean onlyText) {
		this.onlyText = onlyText;
	}

}
