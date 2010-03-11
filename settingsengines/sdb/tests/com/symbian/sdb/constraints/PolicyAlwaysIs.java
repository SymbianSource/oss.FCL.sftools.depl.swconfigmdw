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

import org.jmock.core.Constraint;

/**
 * Our constraint for setting bytes on the prepared statement
 */
public class PolicyAlwaysIs implements Constraint {
    
	private String fErrorDescription;
	private int fAlwaysType;
	private int fNoPolicyValue;
	
    public PolicyAlwaysIs(int aAlwaysType, int aNoPolicy) {  
    	fAlwaysType = aAlwaysType;
    	fNoPolicyValue = aNoPolicy;
    }
    
    /**
     * This ensures the contents of the blob are as we expect
     */
    public boolean eval(Object o) {
    	
    	byte[] lBlob = (byte[])o;
    	
    	if(lBlob[0] != fAlwaysType){
    		fErrorDescription = "Incorrect Always type (fail/pass) specified";
    		return false;
    	}
    	
    	if(  (lBlob[1] != fNoPolicyValue) || (lBlob[2] != fNoPolicyValue) || (lBlob[3] != fNoPolicyValue)|| (lBlob[4] != fNoPolicyValue) ||
    			(lBlob[5] != fNoPolicyValue)|| (lBlob[6] != fNoPolicyValue)|| (lBlob[7] != fNoPolicyValue) ){
    		fErrorDescription = "Incorrect values specified where there should be no policy";
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
