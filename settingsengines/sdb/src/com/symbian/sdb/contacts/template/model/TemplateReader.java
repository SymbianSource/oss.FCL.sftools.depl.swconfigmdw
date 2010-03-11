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

package com.symbian.sdb.contacts.template.model;

import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.exception.TemplateParsingException;


public interface TemplateReader {
	/**
	 * reads the system template model in from the existing database 
	 * @param templateId 
	 * @return template model
	 * @throws TemplateParsingException 
	 */	
    public ITemplateModel readTemplate(long templateId) throws TemplateParsingException;

}
