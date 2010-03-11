// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.util;

import java.util.Arrays;

import junit.framework.TestCase;

public class ByteUtilTest  extends TestCase  {

	private int fIntToTest = 534; 
	private byte[] fIntToTestByteArray = {0, 0, 2, 22};
	
	/**
	 * Tests the int to byte[] (32 bits) conversion is right
	 *
	 */
	public void testToByte(){	
		
		byte[] lRes = ByteUtil.intToByteArray(fIntToTest);
		
		for(int lCnt =0; lCnt< lRes.length; lCnt++){
			assertEquals(lRes[lCnt], fIntToTestByteArray[lCnt]);
		}
		
	}
	
	/**
	 * Tests the byte[] (32 bit) to int conversion is correct
	 *
	 */
	public void testToInt(){		
		assertEquals(fIntToTest, ByteUtil.byteArrayToInt(fIntToTestByteArray));
	}
	
//	public void testHex(){
//		String hex = "4000000E140200000100000001000000140200000300000003000000140200000500000005000000240200001700000017000000240200001800000018000000240200001A0000001A00000034020002B0000002B000000";
//		assertEquals(hex, ByteUtil.toHexString(ByteUtil.fromHexString(hex)).toUpperCase());
//	}
	

	public void testHex2(){
		byte[] b = new byte[] {(byte)100};
		assertEquals("64", ByteUtil.toHexString(b));
	}
	
	public void testHex3() {
		String [] hexstrings = { "ffffffff", "80000000" };
		byte [] [] bytevals = {
				{ (byte)0xff, (byte)0xff, (byte)0xff, (byte)0xff } , 
				{ (byte)0x80, (byte)0x00, (byte)0x00, (byte)0x00 } 
		};
		for ( int i =0; i < hexstrings.length ; i ++ ) {
			assertEquals(hexstrings[i], ByteUtil.toHexString(bytevals[i]));
			assertTrue(Arrays.equals(bytevals[i], ByteUtil.fromHexString(hexstrings[i])));
		}
	}
	
}
