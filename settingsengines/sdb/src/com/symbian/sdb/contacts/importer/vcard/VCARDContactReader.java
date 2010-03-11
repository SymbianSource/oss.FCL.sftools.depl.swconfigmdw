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

package com.symbian.sdb.contacts.importer.vcard;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import net.sf.vcard4j.parser.DomParser;
import net.sf.vcard4j.parser.VCardParseException;
import net.sf.vcard4j.util.XpathUtil;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import com.sun.org.apache.xerces.internal.dom.DocumentImpl;
import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.importer.ContactReader;
import com.symbian.sdb.contacts.model.ContactImpl;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;

/**
 * Class responsible for importing vCard contacts.
 * 
 * @author krzysztofZielinski
 *
 */
public class VCARDContactReader implements ContactReader    {
    
    private static final String CONTACT_XPATH_LOCATION = "/addressBook/*";
    private SpeedDialManager speedDialManager;
    
    public ITemplateModel contactTemplateModel;
        
    public Set<ContactImpl> readContacts(List<File> vCardFiles, ITemplateModel contactsTemplateModel) {
        
    	SpeedDialValidator speedDialValidator = new SpeedDialValidator();
    	
        contactTemplateModel = contactsTemplateModel;
        
        Set<ContactImpl> contactsFromAllFiles = new HashSet<ContactImpl>();
        
        for (File singleVCardFile : vCardFiles) {
            
            Set<ContactImpl> contacts;
            try {
                contacts = importContactsFromFile(singleVCardFile);
            } catch (Exception e) {
                throw new ContactsExeption(e);
            }
            contactsFromAllFiles.addAll(contacts);
            speedDialValidator.addSpeedDialDataFromFile(singleVCardFile, contacts);
        }
        
        speedDialValidator.validate();
        
        return contactsFromAllFiles;
    }

    /**
     * Create contacts based on given vCard file and supported vCard properties (only supported properties are imported).
     * 
     * @param vCardFile
     * @return
     * @throws IOException 
     * @throws FileNotFoundException 
     * @throws VCardParseException 
     * @throws XPathExpressionException 
     */
    private Set<ContactImpl> importContactsFromFile(File vCardFile) throws VCardParseException, FileNotFoundException, IOException, XPathExpressionException, MappingMissingException {

        Document document = createDOMDocumentForVCardFile(vCardFile);
        Set<ContactImpl> contacts = readContactsFromDocument(document);
        
        return contacts;
    }

    /**
     * @param document
     * @return
     * @throws XPathExpressionException 
     */
    private Set<ContactImpl> readContactsFromDocument(Document document) throws XPathExpressionException, MappingMissingException {
        
        Set<ContactImpl> readContacts = new HashSet<ContactImpl>();
        
        NodeList vCardNodes = findVCardNodes(document);
        
        for (int i = 0; i < vCardNodes.getLength(); i++) {
            Node singleVCardNode = vCardNodes.item(i);
            ContactImpl contact = readContactFromNode(singleVCardNode);
            readContacts.add(contact);
        }
        
        return readContacts;
    }


    /**
     * @param singleVCardNode
     * @return
     * @throws XPathExpressionException 
     */
    private ContactImpl readContactFromNode(Node singleVCardNode) throws XPathExpressionException, MappingMissingException {
        IVCardContactProperties contactProperties = readContactProperties(singleVCardNode);
        ContactImpl contact = createContactWithSupportedProperties(contactProperties);
        contact.setSpeedDialData(contactProperties.getSpeedDialData());
        return contact;
    }

    /**
     * Create contact based from given properties (with values) - only supported properties are used 
     * 
     * @param contactProperties
     */
    private ContactImpl createContactWithSupportedProperties(IVCardContactProperties contactProperties)  throws MappingMissingException {
        ContactCreator contactCreator = new ContactCreator(this.contactTemplateModel, speedDialManager);
        ContactImpl createdContact = contactCreator.createContactWithProperties(contactProperties);
        
        return createdContact;
    }

    private IVCardContactProperties readContactProperties(Node cardNode) throws XPathExpressionException {
        PropertyCreator propertyCreator = new PropertyCreator(this.contactTemplateModel);
        Node[] cardTypeNodes = XpathUtil.getNodeArray(cardNode, "type");
        
        for (int i = 0; i < cardTypeNodes.length; i++) {
            propertyCreator.readProperty(cardTypeNodes[i]);
        }
        
        setAllSpeedDialValues(propertyCreator.getProperties(), propertyCreator.getSpeedDialVCardPropertiesData());
        
        return propertyCreator.getProperties();
    }

    /**
	 * @param properties
	 * @param speedDialVCardPropertiesData
	 */
	private void setAllSpeedDialValues(IVCardContactProperties properties, Set<SpeedDialVCardTemporaryData> speedDialVCardPropertiesData) {
		for (SpeedDialVCardTemporaryData speedDialVCardTemporaryData : speedDialVCardPropertiesData) {
			findAndSetSpeedDialValue(speedDialVCardTemporaryData, properties);
		}
	}

	/**
	 * @param speedDialVCardTemporaryData
	 * @param properties
	 */
	private void findAndSetSpeedDialValue(SpeedDialVCardTemporaryData speedDialVCardTemporaryData, IVCardContactProperties properties) {
		for (SimpleProperty simpleProperty : properties.getSimpleProperties()) {
			if (speedDialVCardTemporaryData.matchesVCardProperty(simpleProperty))	{
				speedDialVCardTemporaryData.setValue(simpleProperty);
			}
		}
	}

	private NodeList findVCardNodes(Document document) throws XPathExpressionException {
        
        String xpathExpression = CONTACT_XPATH_LOCATION;
        
        XPathExpression expression = createXPathExpression(xpathExpression);
        
        NodeList nodeList = (NodeList) expression.evaluate(document,XPathConstants.NODESET);

        return nodeList;
    }

    private javax.xml.xpath.XPathExpression createXPathExpression(String xpathExpression) throws XPathExpressionException {
        XPath xpath = getXpath();
        XPathExpression expression;
        expression = xpath.compile(xpathExpression);

        return expression;
    }

    private Document createDOMDocumentForVCardFile(File vCardFile) throws VCardParseException, IOException, FileNotFoundException {
        DomParser parser = new DomParser();
        Document document = new DocumentImpl();
        
        parser.parseAndDecode(new FileInputStream(vCardFile), document);
        return document;
    }

    private XPath getXpath() {
        XPathFactory factory = XPathFactory.newInstance();
        XPath xpath = factory.newXPath();
     
        return xpath;
    }

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}
}
