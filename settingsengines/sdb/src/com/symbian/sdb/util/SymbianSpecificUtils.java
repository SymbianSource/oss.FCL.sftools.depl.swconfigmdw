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
// 2008
//



package com.symbian.sdb.util;

import java.util.Date;

/**
 * Symbian specific util methods
 * 
 * @author krzysztofZielinski
 *
 */
public class SymbianSpecificUtils {

    /**
     * Converts timesamp as number of milliseconds since 1/1/1970 to 
     * Symbian timestamp i.e. number of microseconds since 0 AD  
     * 
     * @param timestamp
     * @return
     */
    public static long convertToSymbianTimestamp(long timestamp) {
        long timestampInMicroseconds = timestamp * 1000; 
        long symbianTimestampInMicrosecods_1_1_1970 = 62168256000000000L;
        return timestampInMicroseconds + symbianTimestampInMicrosecods_1_1_1970;
    }

    public static long createCurrentSymbianTimestamp() {
        long currentTimestamp = new Date().getTime();
        long currentSymbianTimestamp = convertToSymbianTimestamp(currentTimestamp);
        return currentSymbianTimestamp;
    }
    
}
