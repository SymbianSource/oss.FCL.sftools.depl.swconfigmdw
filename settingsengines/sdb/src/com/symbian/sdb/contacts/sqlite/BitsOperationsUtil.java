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

package com.symbian.sdb.contacts.sqlite;

/**
 * Class for useful bits operations
 * 
 * @author krzysztofZielinski
 *
 */
public class BitsOperationsUtil {

    /**
     * Returns lower byte of short
     * 
     * @param value
     * @return
     */
    public static byte getLowerByte(short value)    {
        return (byte)(value);
    }
    
    /**
     * Returns higher byte of short
     * 
     * @param value
     * @return
     */
    public static byte getHigherByte(short value)    {
        return (byte)(value >> 8);
    }

    /**
     * Create int based on for bytes - int(fistByte,secondByte,thirdByte,fourthByte)
     * 
     * @param firstByte highest byte
     * @param secondByte
     * @param thirdByte
     * @param fourthByte lowest byte
     * @return
     */
    public static int getIntFormBytes(byte firstByte, byte secondByte, byte thirdByte, byte fourthByte) {
 
        return unsignedByteToInt(fourthByte) + (unsignedByteToInt(thirdByte) << 8) + (unsignedByteToInt(secondByte) << 16) + (unsignedByteToInt(firstByte) << 24);
    }
    
    /**
     * Returns in value of unsigned byte
     * 
     * @param value
     * @return
     */
    public static int unsignedByteToInt(byte value) {
        return (int) value & 0xFF;
    }


    /**
     * Returns byte array with 4 bytes from given int (index 0 contain the highest byte)
     * 
     * @param integer
     * @return
     */
    public static byte[] getBytesFromInt(int integer)   {
        
        byte[] bytes = new byte[4];
        
        bytes[0] = (byte) (integer >> 24);
        bytes[1] = (byte) ((integer & 0x00FF0000) >> 16);
        bytes[2] = (byte) ((integer & 0x0000FF00) >> 8);
        bytes[3] = (byte) (integer & 0x000000FF);
        
        return bytes;
    }
}
