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

package com.symbian.sdb.contacts;

import org.springframework.test.AbstractDependencyInjectionSpringContextTests;


/**
 * @author krzysztofZielinski
 *
 */
public abstract class BaseIntegrationTestCase extends AbstractDependencyInjectionSpringContextTests  {

    /* (non-Javadoc)
     * @see org.springframework.test.AbstractSingleSpringContextTests#getConfigLocations()
     */
    @Override
    protected String[] getConfigLocations() {
        setAutowireMode(AUTOWIRE_BY_NAME);
        return new String [] {"applicationContext-integration-tests.xml"};
    }
    
    @Override
    protected void onSetUp() throws Exception {
    	super.onSetUp();
    	System.setProperty("sdb.contacts.enabled", "true");
    }

}
