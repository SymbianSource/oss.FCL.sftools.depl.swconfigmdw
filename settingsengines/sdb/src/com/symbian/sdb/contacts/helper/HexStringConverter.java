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

import com.symbian.sdb.contacts.sqlite.BitsOperationsUtil;

/**
 * @author krzysztofZielinski
 *
 */
public class HexStringConverter {

    public static byte[] convertHexStringToByteArray(String hexString)  {
        byte[] bytes = new byte[hexString.length()/2];
        for (int index = 0, byteCounter = 0; index < hexString.length(); index+=2) {
            String singleByteInHexString = hexString.substring(index, index+2);
            
            byte value = (byte) Short.parseShort(singleByteInHexString,16);
            bytes[byteCounter++] = value;
        }
        return bytes;
    }
    
    public static String convertByteArrayToHexString(byte[] bytes)  {
        StringBuffer stringBuffer = new StringBuffer();
        
        for (int i = 0; i < bytes.length; i++) {
            int value = BitsOperationsUtil.getIntFormBytes((byte)0, (byte)0, (byte)0, bytes[i]);
            String byteHexString = createByteHextString(value);
            stringBuffer.append(byteHexString);
        }
        
        return stringBuffer.toString();
    }

    private static String createByteHextString(int value) {
        StringBuffer hexStringBuffer = new StringBuffer(Integer.toHexString(value));
        
        if (hexStringBuffer.length() < 2) {
            hexStringBuffer.insert(0, "0");
        }
        return hexStringBuffer.toString();
    }
}

