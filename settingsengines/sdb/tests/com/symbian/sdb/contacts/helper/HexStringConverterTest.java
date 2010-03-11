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

package com.symbian.sdb.contacts.helper;

import java.util.Arrays;

import junit.framework.TestCase;

/**
 * @author krzysztofZielinski
 *
 */
public class HexStringConverterTest extends TestCase {

    public void testConvertHexStringToByteArray() throws Exception {
        String hexString = "00FF010F21F0";
        byte[] expectedByteArray = {0x00,(byte) 0xFF, 0x01, 0x0F, 0x21,(byte) 0xF0};

        byte[] resultByteArray = HexStringConverter.convertHexStringToByteArray(hexString);
        
        assertTrue(Arrays.equals(expectedByteArray, resultByteArray));
    }
    
    public void testConvertHexStringToByteArrayWithEmptyString() throws Exception {
        String hexString = "";
        byte[] expectedByteArray = {};
        
        byte[] resultByteArray = HexStringConverter.convertHexStringToByteArray(hexString);
        
        assertTrue(Arrays.equals(expectedByteArray, resultByteArray));
    }
    
    public void testConvertHexStringToByteArrayWithOddNumberOfCharacters() throws Exception {
        String hexString = "FFFFF";
        
        try {
            HexStringConverter.convertHexStringToByteArray(hexString);
            fail();
        }
        catch (StringIndexOutOfBoundsException e) {
        }
    }

    public void testConvertHexStringToByteArrayWithLongString() throws Exception {
        String hexString = "FFFFFF000101010C1010101D001F01010101A010101010101010101105959340503400";
        byte[] expectedByteArray = {(byte) 0xFF, (byte) 0xFF ,(byte) 0xFF ,0x00 ,0x01 ,0x01 ,0x01 ,0x0C ,0x10 ,0x10 ,0x10 ,0x1D ,0x00 ,0x1F ,0x01 ,0x01 ,0x01 ,0x01 ,(byte) 0xA0 ,0x10 ,0x10 ,0x10 ,0x10 ,0x10 ,0x10 ,0x10 ,0x10 ,0x11 ,0x05 ,(byte) 0x95 ,(byte) 0x93 ,0x40 ,0x50 ,0x34 ,0x00};
        
        byte[] resultByteArray = HexStringConverter.convertHexStringToByteArray(hexString);
        
        assertTrue(Arrays.equals(expectedByteArray, resultByteArray));
    }

    public void testConvertHexStringToByteArrayWithInvalidHexString() throws Exception {
        String hexString = "ABCDEFGHIJK0Z1";

        try {
            HexStringConverter.convertHexStringToByteArray(hexString);    
            fail();
        }
        catch (NumberFormatException e) {
        }
    }

    public void testConvertHexStringToByteArrayWithLowerUpperCase() throws Exception {
        String hexString = "00Ffa10Ff1bC";
        byte[] expectedByteArray = {0x00, (byte) 0xFF, (byte) 0xA1, 0x0F, (byte) 0xF1, (byte) 0xBC};

        byte[] resultByteArray = HexStringConverter.convertHexStringToByteArray(hexString);
        
        assertTrue(Arrays.equals(expectedByteArray, resultByteArray));
    }
    
    public void testConvertByteArrayToHexString() throws Exception {
        String expectedString = "00Ffa10Ff1bC";
        byte[] bytes = {0x00, (byte) 0xFF, (byte) 0xA1, 0x0F, (byte) 0xF1, (byte) 0xBC};

        String resultString = HexStringConverter.convertByteArrayToHexString(bytes);
        
        assertEquals(expectedString.toUpperCase(), resultString.toUpperCase());
    }
    
    public void testConvertByteArrayToHexStringWithOddNumberOfBytes() throws Exception {
        String expectedString = "00FFA10F";
        byte[] bytes = {0x00, (byte) 0xFF, (byte) 0xA1, 0x0F};

        String resultString = HexStringConverter.convertByteArrayToHexString(bytes);
        
        assertEquals(expectedString.toUpperCase(), resultString.toUpperCase());
    }

}
