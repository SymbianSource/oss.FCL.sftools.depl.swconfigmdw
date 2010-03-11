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

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
/**
 * Template management use cases
 */
public interface ITemplateManager {

	/**
	 * Invokes resource file parser to get a template model from resource file  
	 * @param resourceFilename
	 * @return template model
	 * @throws SDBExecutionException
	 */
	public ITemplateModel parse(String resourceFilename) throws TemplateParsingException;

	
	/**
	 * Persists the template model to the database
	 * @param template TODO
	 */
	public void persistTemplate(ITemplateModel template) throws SDBExecutionException;
	
	/**
	 *  Reads the system template model from existing database connection
	 * @return template model
	 */
	public ITemplateModel read() throws TemplateParsingException;
} 
