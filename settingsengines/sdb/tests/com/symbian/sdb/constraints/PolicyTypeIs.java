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

import com.symbian.sdb.configuration.policy.type.PolicyType;

public class PolicyTypeIs implements Constraint {
    
	String fErrorMessage;
	
    public PolicyTypeIs() {    	
    }
    
    /**
     * This is the Logic behind our constraint
     */
    public boolean eval(Object o) {
    	
    	//PolicyType.values();
    	
    	for(PolicyType t : PolicyType.values()){
    		if(o.equals((Object)t.getPolicyTypeID())){
    			return true;
    		}
    	}    	    	    	
    	
    	return false;
    }
    
    /**
     * This is our error message
     */
    public StringBuffer describeTo(StringBuffer buffer) {
    	return buffer.append("Invalid PolicyType has been specified");
    }



}
