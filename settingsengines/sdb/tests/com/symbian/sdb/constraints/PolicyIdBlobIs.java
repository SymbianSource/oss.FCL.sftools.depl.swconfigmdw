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

package com.symbian.sdb.constraints;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.List;

import org.jmock.core.Constraint;

import com.symbian.sdb.configuration.policy.type.IDType;

public class PolicyIdBlobIs implements Constraint {
    
	private String fErrorDescription;
	private List<Byte> fAllowedCapabilities;
	private IDType fIdType;
	private int fId;
	
    public PolicyIdBlobIs(List<Byte> aAllowedCapabilities, int aId, IDType aIdType) {
    	fAllowedCapabilities = aAllowedCapabilities;
    	fIdType = aIdType;
    	fId = aId;
    }

    /**
     * This ensures the contents of the blob are as we expect
     */    
    public boolean eval(Object o) {
    	
    	byte[] lBlob = (byte[])o;
    	ByteBuffer lByteIdBuffer = ByteBuffer.allocate(4);
    	lByteIdBuffer.order(ByteOrder.LITTLE_ENDIAN);
    	byte[] lByteId = lByteIdBuffer.putInt(fId).array();
    	
    	//Check the non capabilities
    	if((lBlob[0] != fIdType.toByte()) || (lBlob[4] != lByteId[0]) ||  (lBlob[5] != lByteId[1]) || (lBlob[6] != lByteId[2]) || (lBlob[7] != lByteId[3])){
    		fErrorDescription = "Incorrect ID Sepcified or PolicyType (pass/fail)";
    		return false;
    	}
    	
    	//Ensure the right capabilities are present
    	if((fAllowedCapabilities.indexOf(lBlob[1]) == -1) || (fAllowedCapabilities.indexOf(lBlob[2]) == -1) ||
    			(fAllowedCapabilities.indexOf(lBlob[3]) == -1)){
    		fErrorDescription = "Incorrect capabilities present in PolicyID BLOB";
    		return false;
    	}
    		
    	return true;    	
    }
    
    /**
     * Describes Error
     */    
    public StringBuffer describeTo(StringBuffer buffer) {
    	return buffer.append("Error in capability Blob Validation: "+fErrorDescription);
    }



}
