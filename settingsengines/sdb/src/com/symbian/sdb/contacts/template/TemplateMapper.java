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

import java.io.File;
import java.io.IOException;
import java.util.HashMap;

import javax.xml.parsers.ParserConfigurationException;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.google.common.collect.HashMultimap;
import com.google.common.collect.Multimap;
import com.symbian.sdb.contacts.ContactsConfigurationException;
import com.symbian.sdb.util.XMLBrowser;
import com.symbian.sdb.util.XmlManager;

/**
 * Utility to map the values from template resource file to values 
 */
public class TemplateMapper implements IFieldMapping {
	private XMLBrowser browser = new XMLBrowser();
	private Document configuration = null;
	private Document locale = null;
	
	private static final Logger logger = Logger.getLogger(TemplateMapper.class);
	
	private static TemplateMapper instance;
	
	private TemplateMapper() {}
	
	public static TemplateMapper getInstance() throws ContactsConfigurationException  {
		if (instance == null) {
			instance = new TemplateMapper();
			instance.init();
		}
		return instance;
	}

	public void init() throws ContactsConfigurationException {
		if (configuration == null) {
			String configPath = System.getProperty("sdb.contacts.configuration");
			String localePath = System.getProperty("sdb.contacts.configuration.locale");
			loadDocument(configPath, localePath);
		}
	}
	
	public Document getDocument() {
		try {
			init();
		} catch (ContactsConfigurationException ex) {
			logger.warn("Configuration file for contacts creation not found.");
		}
		return configuration;
	}

	private boolean isLocaleFile(String localePath) {
		if (localePath == null) {
			return false;
		}
		File localeFile = new File(localePath);
		if (!localeFile.isFile() || !localeFile.exists()) {
			logger.warn("Locale file for contacts creation not found: " + localePath + ". Please set the sdb.contacts.configuration.locale property.");
			return false;
		}
		return true;
	}
	
	private void loadDocument(String configPath, String localePath) throws ContactsConfigurationException {
		XmlManager manager = new XmlManager();
		if (configPath == null) {
			throw new ContactsConfigurationException(
					"Configuration file for contacts creation not found. Set the sdb.contacts.configuration property. ");
		}
		File configFile = new File(configPath);
		if (!configFile.isFile() || !configFile.exists()) {
			throw new ContactsConfigurationException(
					"Configuration file for contacts creation not found: "+configPath+". Set the sdb.contacts.configuration property.");
		}
		try {
			configuration = manager.loadDocument(configFile);
			if (isLocaleFile(localePath)) {
				locale = manager.loadDocument(new File(localePath));
			} else {
				locale = manager.loadDocument(new File(configPath));
			}
		} catch (IOException e) {
			throw new ContactsConfigurationException (
					"Loading configuration file failed: "
							+ e.getLocalizedMessage());
		} catch (SAXException e) {
			throw new ContactsConfigurationException(
					"Loading configuration file failed: "
							+ e.getLocalizedMessage());
		} catch (ParserConfigurationException e) {
			throw new ContactsConfigurationException(
					"Loading configuration file failed: "
							+ e.getLocalizedMessage());
		}
	}
	
	private Long translateLongValue(String value) {
		Long result = null; 
		try {
			if (value.startsWith("0x")) {
				result = Long.parseLong(value.replace("0x", ""), 16);
			} else {
				result = Long.parseLong(value);
		    }
		} catch (NumberFormatException ex) {
			logger.warn("Value " + value + " is not a number.");
		}
		return result;
	}
	
	private Integer translateIntegerValue(String value) {
		Integer result = null; 
		try {
			if (value.startsWith("0x")) {
				result = Integer.parseInt(value.replace("0x", ""), 16);
			} else {
				result = Integer.parseInt(value);
		    }
		} catch (NumberFormatException ex) {
			logger.warn("Value " + value + " is not a number.");
		}
		return result;
	}
	
	public Multimap<Integer, String> getFlagsMapping() throws MappingMissingException {
		NodeList list = browser.findXPathList("//group[@type='flags']/item", configuration);
		
		Multimap<Integer, String> map = new HashMultimap<Integer, String>();
		if (list != null) {
			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);
				String name = node.getAttributes().getNamedItem("name")
						.getNodeValue();
				String value = node.getAttributes().getNamedItem("value")
						.getNodeValue();
				map.put(translateIntegerValue(value), name);
			}
		} else {
			logger.debug("Mapping missing for flags type");
			throw new MappingMissingException("Mapping missing for flags type");
		}
		return map;
		
	}

	public HashMap<String, Long> getMappingToLong(String type) throws ContactsConfigurationException {
		NodeList list = browser.findXPathList("//group[@type='" + type + "']/item", configuration);
		HashMap<String, Long> map = new HashMap<String, Long>();
		if (list != null) {
			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);
	
				String name = node.getAttributes().getNamedItem("name")
						.getNodeValue();
				String value = node.getAttributes().getNamedItem("value")
						.getNodeValue();
				map.put(name, translateLongValue(value));
			}
		} else {
			logger.debug("Mapping missing for key " + type);
			throw new ContactsConfigurationException("Mapping missing for key " + type);
		}
		
		return map;
	}
	
	public HashMap<String, String> getMapping(ContactMapTypes type) throws MappingMissingException {
		Document document;
		if (type.equals(ContactMapTypes.labels)) {
			document = this.locale;
		} else {
			document = this.configuration;
		}
		NodeList list = browser.findXPathList("//group[@type='" + type.toString() + "']/item", document);
		HashMap<String, String> map = new HashMap<String, String>();
		if (list != null) {
			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);
	
				String name = node.getAttributes().getNamedItem("name")
						.getNodeValue();
				String value = node.getAttributes().getNamedItem("value")
						.getNodeValue();
				map.put(name, value);
			}
		} else {
			logger.debug("Mapping missing for key " + type);
			throw new MappingMissingException("Mapping missing for key " + type);
		}
		
		return map;
	}
	
	public HashMap<Integer, String> getReversedMapping(ContactMapTypes type) throws MappingMissingException {
		NodeList list = browser.findXPathList("//group[@type='" + type.toString()
				+ "']/item", configuration);
		HashMap<Integer, String> map = new HashMap<Integer, String>();
		if (list != null) {
			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);
	
				String name = node.getAttributes().getNamedItem("name")
						.getNodeValue();
				String value = node.getAttributes().getNamedItem("value")
						.getNodeValue();
				map.put(translateIntegerValue(value), name);
			}
		} else {
			logger.debug("Mapping missing for key " + type);
			throw new MappingMissingException("Mapping missing for key " + type);
		}
		
		return map;
	}
	
	public HashMap<String, String> getUidValueToLabelMap() throws MappingMissingException {
		NodeList list = browser.findXPathList("//group[@type='" + ContactMapTypes.labels
				+ "']/item", locale);
		HashMap<String, String> map = new HashMap<String, String>();
		if (list != null) {
			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);
	
				String name = node.getAttributes().getNamedItem("name")
						.getNodeValue();
				String value = node.getAttributes().getNamedItem("value")
						.getNodeValue();
				map.put(value, name);
			}
		} else {
			logger.warn("No label mapping available");
		}
		return map;
	}
	
	public Integer getFieldType(String key) throws MappingMissingException {
		Node node = browser.findXPathNode("//group[@type='field_type_mapping']/item[@name='"
				+key
				+"']", configuration);
		Integer result = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("value") != null) {
			String r = node.getAttributes().getNamedItem("value").getNodeValue();
			if (r.startsWith("0x")) {
				result = Integer.parseInt(r.replace("0x", ""), 16);
			} else {
				result = Integer.parseInt(r);
			}
		} else {
			logger.debug("Mapping missing for field type " + key);
			throw new MappingMissingException("Mapping missing for field type " + key);
		}
		return result;
	}
	
	
	/**
	 * 
	 * @param key the field name
	 * @param fieldNo If the key  is used multiple times (for example a structured field) this is used to define which value should be returned
	 * @return The field value corresponding to the key and field number. Never null.
	 * @throws MappingMissingException thrown if the key and/or field number do not have a corresponding value
	 */
	public String getMappingFromvCard(String key, int fieldNo) throws MappingMissingException {
		StringBuilder query = new StringBuilder("//group[@type='vcard_mapping']/item[@vCard='%s'");
		if (fieldNo > 0) {
			query.append(" and @structuredField='%d'");
		}
		query.append("]");

		String temp = String.format(query.toString(), key, fieldNo);

		Node node = browser.findXPathNode(temp, configuration);
		String result = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("name") != null) {
			result = node.getAttributes().getNamedItem("name").getNodeValue();
		} else {
			logger.debug("Mapping missing for vCard Mapping " + key);
			throw new MappingMissingException("Mapping missing for vCard Mapping " + key);
		}
		return result;
	}
	
	public Integer getValueFromvCardMapping(String key) throws MappingMissingException {
		Integer result = null;
		StringBuilder query = new StringBuilder("//group[@type='vcard_mapping']/item[@name='%s']");

		String temp = String.format(query.toString(), key);

		Node node = browser.findXPathNode(temp, configuration);
		String r = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("value") != null) {
			
			r = node.getAttributes().getNamedItem("value").getNodeValue();
			if (r.startsWith("0x")) {
				result = Integer.parseInt(r.replace("0x", ""), 16);
			} else {
				result = Integer.parseInt(r);
		    }
		} else {
			logger.debug("Mapping missing for vCardMapping " + key);
			throw new MappingMissingException("Mapping missing for vCardMapping " + key);
		}
		
		return result;
	}
	
	public String getLabel(String key) throws MappingMissingException {
		String query = String.format("//group[@type='labels']/item[@name='%s']", key);
		Node node = browser.findXPathNode(query, locale);
		String result = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("value") != null) {
			result = node.getAttributes().getNamedItem("value").getNodeValue();
		} else {
			logger.warn("Mapping missing for label uid: " + key);
			result = key;
		}
		return result;
	}

	public String getLabelID(String key) throws MappingMissingException {
		String query = String.format("//group[@type='labels']/item[@value='%s']", key);
		Node node = browser.findXPathNode(query, locale);
		String result = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("name") != null) {
			result = node.getAttributes().getNamedItem("name").getNodeValue();
		} else {
			logger.warn("Mapping missing for label: " + key);
			result = key;
		}
		return result;
	}
	
	public Integer getContactTypeMapping(String key) throws MappingMissingException {
		String query = String.format("//group[@type='contact_type']/item[@name='%s']", key);
		Node node = browser.findXPathNode(query, configuration);
		Integer result = null;
		if (node != null 
				&& node.getAttributes() != null 
				&& node.getAttributes().getNamedItem("value") != null) {
			result = translateIntegerValue(
					node.getAttributes().getNamedItem("value").getNodeValue());
		} else {
			logger.debug("Mapping missing for contact type " + key);
			throw new MappingMissingException("Mapping missing for contact type " + key);
		}
		return result;
	}
	
	private ContactsUidMap getMap(ContactMapTypes mapType) {
		ContactsUidMap map = null;
		try {
			map = new ContactsUidMap(getMapping(mapType));
		} catch (MappingMissingException ex) {
			logger.warn("Missing mapping for " + mapType.toString());
			map = new ContactsUidMap(new HashMap<String, String>());
		} 
		return map;
	}
	
	public ContactsUidMap getUidMap() {
		return getMap(ContactMapTypes.uid_mapping);
	}
	
}
