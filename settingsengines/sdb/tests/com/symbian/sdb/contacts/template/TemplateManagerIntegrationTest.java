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

import junit.framework.JUnit4TestAdapter;

import com.symbian.sdb.contacts.BaseIntegrationTestCase;

public class TemplateManagerIntegrationTest extends BaseIntegrationTestCase     {

    public static final String templatesPath = "tests/config/template_itests/";
    
    private TemplateManager templateManager;
    
    public void setDbmsTemplateManager(TemplateManager templateManager) {
        this.templateManager = templateManager;
    }

    
    @Override
    protected void onSetUp() throws Exception {
        super.onSetUp();
        System.setProperty("sdb.contacts.configuration","config/contacts.xml");
    }

    public void testTemplateIsSame() throws Exception {
        
        ITemplateModel template1 = templateManager.parse(templatesPath + "94.rss");
        ITemplateModel template2 = templateManager.parse(templatesPath + "94.rss");
        ITemplateModel template3 = templateManager.parse(templatesPath + "91.rss");
        
        assertTrue(template1.isSame(template1));
        assertTrue(template1.isSame(template2));
        assertFalse(template1.isSame(template3));
    }

    public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(TemplateManagerIntegrationTest.class);
	}

}
