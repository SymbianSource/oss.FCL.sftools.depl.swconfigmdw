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

import static org.junit.Assert.fail;
import junit.framework.JUnit4TestAdapter;

import org.junit.Assert;
import org.junit.Test;

import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.exception.SDBValidationException;

public class ConfOptionsTest {
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ConfOptionsTest.class); 
    }
    
    @Test
    public void testGetEncoding() throws SDBValidationException {
        try {
            DbOptions.ENCODING.setValue("xxx");
            fail("shouldn't get here - exc should have been thrown");
        } catch(Exception e) {
        }
        String pragma = DbOptions.ENCODING.getValue();
        Assert.assertEquals("PRAGMA encoding = \"UTF-16\"", pragma);
        
        DbOptions.ENCODING.setValue("UTF_16");
        pragma = DbOptions.ENCODING.getValue();
        Assert.assertEquals("PRAGMA encoding = \"UTF-16\"", pragma);
        
        DbOptions.ENCODING.setValue("UTF_8");
        pragma = DbOptions.ENCODING.getValue();
        Assert.assertEquals("PRAGMA encoding = \"UTF-8\"", pragma);
    }
    
    @Test(expected=SDBValidationException.class)
    public void testSetIllegalEncodingValue() throws SDBValidationException {
        DbOptions.ENCODING.setValue("xxx");
    }
    
    @Test(expected=SDBValidationException.class)
    public void testSetIllegalPageSizeValue() throws SDBValidationException {
        DbOptions.PAGE_SIZE.setValue("xxx");
    }
    
    @Test
    public void testGetPageSize() throws SDBValidationException {
        try {
            DbOptions.PAGE_SIZE.setValue("xxx");
            fail("shouldn't get here - exc should have been thrown");
        } catch(Exception e) {
        }
        String pragma = DbOptions.PAGE_SIZE.getValue();
        Assert.assertEquals("PRAGMA page_size = 1024", pragma);
        
        DbOptions.PAGE_SIZE.setValue("512");
        pragma = DbOptions.PAGE_SIZE.getValue();
        Assert.assertEquals("PRAGMA page_size = 512", pragma);
        
        DbOptions.PAGE_SIZE.setValue("2048");
        pragma = DbOptions.PAGE_SIZE.getValue();
        Assert.assertEquals("PRAGMA page_size = 2048", pragma);
        
        DbOptions.PAGE_SIZE.setValue("4096");
        pragma = DbOptions.PAGE_SIZE.getValue();
        Assert.assertEquals("PRAGMA page_size = 4096", pragma);
    }

}
