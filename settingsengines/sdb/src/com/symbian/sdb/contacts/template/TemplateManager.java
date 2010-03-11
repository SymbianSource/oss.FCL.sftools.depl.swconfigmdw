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

import java.util.HashMap;
import org.antlr.runtime.RecognitionException;
import org.apache.log4j.Logger;
import com.symbian.sdb.contacts.template.RSSFactory.RSSParserKit;
import com.symbian.sdb.contacts.template.model.TemplatePersister;
import com.symbian.sdb.contacts.template.model.TemplateReader;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.resource.RSSLexer;
import com.symbian.sdb.resource.RSSParser;

/**
 * Entry point for templates use cases
 */
public class TemplateManager implements ITemplateManager {

    private static final Logger logger = Logger.getLogger(TemplateManager.class);
	
	private FieldContainer container;
	private ITemplateModel model;
	
	private TemplateReader templateReader;
	private TemplatePersister templatePersister;
	
    protected FieldContainer parseResource(RSSParser resourceParser) 
    throws TemplateParsingException {
    	FieldContainer model = null;
    	try {
	        resourceParser.document();
	        model = resourceParser.getContainer();
    	} catch (RecognitionException e) {
    		throw new TemplateParsingException("Parsing resource file error: " + e.getLocalizedMessage());
        }
    	return model;
    }
    
    public ITemplateModel parse(String resourceFilename) throws TemplateParsingException {
    	TemplateMapper mapper = TemplateMapper.getInstance();

    	RSSParserKit resourceParserKit = RSSFactory.getRSSParserKit(resourceFilename);
    	RSSParser resourceParser = resourceParserKit.getParser();
    	RSSLexer resourceLexer = resourceParserKit.getLexer();
    	
    	try { 
	        HashMap<String, String> storagemap = mapper.getMapping(ContactMapTypes.storage);
	        HashMap<String, String> categorymap = mapper.getMapping(ContactMapTypes.category);
	        HashMap<String, String> flagmap = mapper.getMapping(ContactMapTypes.flags);
	        
	        resourceParser.setCategoryMapping(categorymap);
	        resourceParser.setFlagMapping(flagmap);
	        resourceParser.setStorageMapping(storagemap);
    	} catch (MappingMissingException ex) {
    		throw new TemplateParsingException("Configuration file error: " + ex.getMessage());
    	}

        container = parseResource(resourceParser);
        StringBuilder errors = new StringBuilder();
        for(RecognitionException exception : resourceLexer.getExceptions()){
            errors.append(resourceLexer.getErrorMessage(exception, resourceLexer.getTokenNames())).append("\n");
            logger.debug("Template parser encountered an error: "+ resourceLexer.getErrorMessage(exception, resourceLexer.getTokenNames()), exception);
        }
        for(RecognitionException exception : resourceParser.getExceptions()){
            errors.append(resourceParser.getErrorMessage(exception, resourceParser.getTokenNames())).append("\n");
            logger.debug("Template parser encountered an error: "+ resourceParser.getErrorMessage(exception, resourceParser.getTokenNames()), exception);
        }
        if(errors.length()>0){
            throw new TemplateParsingException(errors.toString());
        }
        container.setMapper(mapper);
        
        if (container.getSize() == 0) {
        	throw new TemplateParsingException("No fields found in resource file.");
        }
        
        model = new TemplateModel(mapper, container);
        
    	return model; 
    }

    public ITemplateModel read() throws TemplateParsingException {
    	return templateReader.readTemplate(ITemplateModel.SYSTEM_TEMPLATE_ID);
    }
    
    public void persistTemplate(ITemplateModel template) throws SDBExecutionException {
       templatePersister.persistTemplate(template);    
    }

    //Getters and setters

    public void setTemplateReader(TemplateReader templateReader) {
		this.templateReader = templateReader;
	}

	public void setTemplatePersister(TemplatePersister templatePersister) {
		this.templatePersister = templatePersister;
	}
	
}
