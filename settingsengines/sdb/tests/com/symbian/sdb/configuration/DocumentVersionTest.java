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

package com.symbian.sdb.configuration;

import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Test;

public class DocumentVersionTest {

    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(DocumentVersionTest.class); 
    }

    @Test
    public void test() {
        Assert.assertEquals("//policy", DocumentVersion.V10.getQuery(new Object[] {"policy", "sqlite"}));
        Assert.assertEquals("//database[@type=\"sqlite\"]/policy | //common/applicable[@type=\"sqlite\"]/following-sibling::database/policy", 
                DocumentVersion.V20.getQuery(new Object[] {"policy", "sqlite"}));
   
        Assert.assertEquals("//configuration", DocumentVersion.V10.getQuery(new Object[] {"configuration", "dbms"}));
        Assert.assertEquals("//database[@type=\"dbms\"]/configuration | //common/applicable[@type=\"dbms\"]/following-sibling::database/configuration", 
                DocumentVersion.V20.getQuery(new Object[] {"configuration", "dbms"}));

    }

}
