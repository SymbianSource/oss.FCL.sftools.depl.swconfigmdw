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

import java.util.Arrays;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.junit.Test;

import com.symbian.sdb.contacts.sqlite.BitsOperationsUtil;


/**
 * @author krzysztofZielinski
 *
 */
public class BitsOperationUtilTest {

    private static short SHORT_65535 = (short) 0xFFFF;
    private static short SHORT_0 = 0x0000;
    private static short SHORT_1056 = 0x0420;
    private static byte BYTE_255 = (byte) 255;
    private static byte BYTE_0 = (byte)0x00;
    private static byte BYTE_4 = (byte)0x04;
    private static byte BYTE_32 = (byte)0x20;
    
    @Test
    public void testGetLowerByteFromShort() throws Exception {
        
        byte lower = BitsOperationsUtil.getLowerByte(SHORT_65535);
        Assert.assertEquals(BYTE_255, lower);

        lower = BitsOperationsUtil.getLowerByte(SHORT_0);
        Assert.assertEquals(BYTE_0, lower);

        lower = BitsOperationsUtil.getLowerByte(SHORT_1056);
        Assert.assertEquals(BYTE_32, lower);
    }
    
    @Test
    public void testGetHigherByteFromShort() throws Exception {
        
        byte higher = BitsOperationsUtil.getHigherByte(SHORT_65535);
        Assert.assertEquals(BYTE_255, higher);

        higher = BitsOperationsUtil.getHigherByte(SHORT_0);
        Assert.assertEquals(BYTE_0, higher);

        higher = BitsOperationsUtil.getHigherByte(SHORT_1056);
        Assert.assertEquals(BYTE_4, higher);
    }

    @Test
    public void testGetIntFormBytes() throws Exception {
        
        int resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_0, BYTE_0, BYTE_0, BYTE_0);
        Assert.assertEquals(0x00000000, resultInt);
        
        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_0, BYTE_0, BYTE_0, BYTE_4);
        Assert.assertEquals(0x00000004, resultInt);

        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_0, BYTE_0, BYTE_0, BYTE_255);
        Assert.assertEquals(0x000000FF, resultInt);

        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_0, BYTE_0, BYTE_4, BYTE_4);
        Assert.assertEquals(0x00000404, resultInt);

        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_4, BYTE_32, BYTE_4, BYTE_32);
        Assert.assertEquals(0x04200420, resultInt);

        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_255, BYTE_4, BYTE_32, BYTE_0);
        Assert.assertEquals(0xFF042000, resultInt);
        
        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_255, BYTE_4, BYTE_32, BYTE_255);
        Assert.assertEquals(0xFF0420FF, resultInt);
        
        resultInt = BitsOperationsUtil.getIntFormBytes(BYTE_255, BYTE_255, BYTE_255, BYTE_255);
        Assert.assertEquals(0xFFFFFFFF, resultInt);
    }

    @Test
    public void testUnsignedByteToInt() throws Exception {
        int resultInt = BitsOperationsUtil.unsignedByteToInt(BYTE_32);
        Assert.assertEquals(0x20, resultInt);
        
        resultInt = BitsOperationsUtil.unsignedByteToInt(BYTE_0);
        Assert.assertEquals(0x00, resultInt);
        
        resultInt = BitsOperationsUtil.unsignedByteToInt(BYTE_255);
        Assert.assertEquals(0xFF, resultInt);
    }
    
    public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(BitsOperationUtilTest.class);
	}
    
	@Test
    public void testGetBytesFromInt() throws Exception {
        byte[] expectedBytes1 = {0x12, 0x34, 0x56, 0x78};
        byte[] bytes = BitsOperationsUtil.getBytesFromInt(0x12345678);
        
        Assert.assertTrue(Arrays.equals(expectedBytes1, bytes));
        
        byte[] expectedBytes2 = {(byte) 0xFF, 0x00, (byte) 0xF0, (byte) 0xA5};
        bytes = BitsOperationsUtil.getBytesFromInt(0xFF00F0A5);
        
        Assert.assertTrue(Arrays.equals(expectedBytes2, bytes));
    }
}
