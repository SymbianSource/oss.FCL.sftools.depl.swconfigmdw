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

package com.symbian.sdb.configuration.policy;

import java.nio.ByteBuffer;

import com.symbian.sdb.configuration.policy.type.AlwaysType;
import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.exception.ValidationException;

public class PolicyAlways extends Policy {
	
	protected AlwaysType fAlwaysType;
	protected PolicyType fPolicyType;
	
	/**
	 * Constructor which sets the policy type of this policy
	 * @param aPolicyType
	 */
	public PolicyAlways(String aPolicyType, String aAlwaysType) throws ValidationException{
		try{
			fPolicyType = PolicyType.valueOf(aPolicyType.toUpperCase());			
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException("\n"+aPolicyType+" is not a valid Policy Type. ",ex);
		}
		
		try{
			fAlwaysType = AlwaysType.valueOf(aAlwaysType.toUpperCase());
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException("\n"+aAlwaysType+" is not a valid type. ", ex);
		}
	}
	
	public AlwaysType getAlwaysType(){
		return fAlwaysType;
	}
	
	public PolicyType getPolicyType(){
		return fPolicyType;
	}	
	
	/**
	 * Generates the Blob data for this object
	 */
	public byte[] getBlobData(){
		
		ByteBuffer lBlobData = ByteBuffer.allocate(8);
		lBlobData.put(getAlwaysType().toByte());
		
		while(lBlobData.position()<8){
			lBlobData.put(NO_POLICY);
		}
		try {			validate();		}		catch (ValidationException e) {		}
		
		return lBlobData.array();
	}
		
	/**
	 * Validates the Content
	 */
	public void validate() throws ValidationException{
	}

}
