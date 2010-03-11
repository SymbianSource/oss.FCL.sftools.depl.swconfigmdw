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

package com.symbian.sdb.util;

import java.io.File;
import java.io.IOException;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Source;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

public class XmlManager {
	private final Logger logger = Logger.getLogger(XmlManager.class);  
	
	public Document loadDocument(File xmlFile) 
	    throws IOException, SAXException, ParserConfigurationException {
	    DocumentBuilderFactory lDocBuilderFact = DocumentBuilderFactory.newInstance();
	    
	    //Fix for DEF108077, must make namespace aware for schema validation for java 6 +
	    lDocBuilderFact.setNamespaceAware(true);
	    DocumentBuilder lBuilder = lDocBuilderFact.newDocumentBuilder();
	    Document document = lBuilder.parse(xmlFile);
	    return document;
	}

	public Schema loadSchema(String filename) throws SAXException {
		File file = new File(filename);
		Source source = null;
		if (file.exists()) {
			source = new StreamSource(file);
		} else {
			source = new StreamSource(getClass().getClassLoader().getResourceAsStream(filename));
		}
	    SchemaFactory lSchemaFactory = SchemaFactory.newInstance( XMLConstants.W3C_XML_SCHEMA_NS_URI );             
	    Schema schemaXSD = lSchemaFactory.newSchema(source);
	    return schemaXSD;
	}

	public void validate( 
			Document document, 
			Schema schema) 
	    throws SAXException, IOException, ParserConfigurationException{
	    
	    //This stringbuilder will store any error generated
	    final StringBuilder lParsingErrors = new StringBuilder();  
	    
	    Validator lValidator = schema.newValidator();
	    
	    lValidator.setErrorHandler(new ErrorHandler() {
	
	        public void error(SAXParseException ex) throws SAXException {   
	            lParsingErrors.append(ex.getMessage());
	        }
	
	        public void fatalError(SAXParseException ex) throws SAXException {
	            lParsingErrors.append(ex.getMessage());
	        }
	
	        public void warning(SAXParseException ex) throws SAXException {
	           // lParsingErrors.append(ex.getMessage());
	            logger.warn("Warning while parsing the configuration file", ex);
	        }
	        
	    });
	    
	    lValidator.validate(new DOMSource(document));
	    
	    if(lParsingErrors.length()>0) {
	        throw new SAXException(lParsingErrors.toString());
	    }           
	}

}
