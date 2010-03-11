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

import java.math.BigInteger;

import org.apache.commons.codec.DecoderException;
import org.apache.commons.codec.binary.Hex;

public final class ByteUtil {

	/**
	 * Private Constructor
	 *
	 */
	private ByteUtil(){
		
	}
	
	public static byte[] intToByteArray(int aInt) {
        byte[] aByteArray = new byte[4];
        for (int lCount = 0; lCount < 4; lCount++) {
            int lOffset = (aByteArray.length - 1 - lCount) * 8;
            aByteArray[lCount] = (byte) ((aInt >>> lOffset) & 0xFF);
        }        
        
        return aByteArray;
    }
	
	public static int byteArrayToInt(byte[] aBytes){
		
		return((((int)aBytes[0])<<24)
			      + (((int)aBytes[1])<<16) 
			      + (((int)aBytes[2])<<8)  
			      + ((int)aBytes[3]));
	}
	
	
	public static String toHexString(byte[] in){
		return new String(Hex.encodeHex(in));
	}
	
	public static byte[] fromHexString(String in) {
		try {
			return Hex.decodeHex(in.toCharArray());
		} catch (DecoderException e) {
			throw new RuntimeException();
		}
	}
}
