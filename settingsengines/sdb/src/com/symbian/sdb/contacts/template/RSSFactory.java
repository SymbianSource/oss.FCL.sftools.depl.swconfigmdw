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

import java.io.IOException;

import org.antlr.runtime.ANTLRFileStream;
import org.antlr.runtime.CommonTokenStream;

import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.resource.RSSLexer;
import com.symbian.sdb.resource.RSSParser;

public class RSSFactory {
    
    public static RSSParserKit getRSSParserKit(String resourceFilename) throws TemplateParsingException {
		try {
			final RSSLexer resourceLexer = new RSSLexer(new ANTLRFileStream(resourceFilename));
			CommonTokenStream tokens = new CommonTokenStream(resourceLexer);
			final RSSParser resourceParser = new RSSParser(tokens);
			
			return new RSSParserKit(){
	            
	            private RSSLexer lexer = resourceLexer;
	            private RSSParser parser = resourceParser;
	            
	            public RSSLexer getLexer() {
	                return lexer;
	            }

	            public RSSParser getParser() {
	                return parser;
	            }
	        };
	        
		} catch(IOException e) {
			throw new TemplateParsingException("Loading resource file failed: " + e.getLocalizedMessage());
		}
		
	} 
	
	public interface RSSParserKit {
	    public RSSLexer getLexer();
	    public RSSParser getParser();
	}

}
