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

import java.util.List;

import org.jmock.core.Constraint;

public class PolicySetBlobIs implements Constraint {
    
	private List<Byte> fAllowedCapabilities;
	private String fErrorDescription;
	private int fPolicyType;
	
    public PolicySetBlobIs(List<Byte> aAllowedCaps, int aPolicyType) {
    	fAllowedCapabilities = aAllowedCaps;
    	fPolicyType = aPolicyType;
    }
    
    /**
     * This ensures the contents of the blob are as we expect
     */     
    public boolean eval(Object o) {
    	
    	byte[] lBlob = (byte[])o;

    	
    	//Check the non capabilities
    	if((lBlob[0] != fPolicyType)){
    		fErrorDescription = "Incorrect PolicyData:PolicyType specified: "+fPolicyType;
    		return false;
    	}
    	
    	//Ensure the right capabilities are present
    	if((fAllowedCapabilities.indexOf(lBlob[1]) == -1) || (fAllowedCapabilities.indexOf(lBlob[2]) == -1) ||
    			(fAllowedCapabilities.indexOf(lBlob[3]) == -1) || (fAllowedCapabilities.indexOf(lBlob[4]) == -1) ||
    			(fAllowedCapabilities.indexOf(lBlob[5]) == -1) || (fAllowedCapabilities.indexOf(lBlob[6]) == -1) ||
    			(fAllowedCapabilities.indexOf(lBlob[7]) == -1)
    	){
    		fErrorDescription = "Incorrect capabilities in BLOB";
    		return false;
    	}
    		
    	return true;    	
    }
    
    /**
     * Describes Error
     */     
    public StringBuffer describeTo(StringBuffer buffer) {
    	return buffer.append("Error in capability BLOB verification: "+fErrorDescription);
    }



}
