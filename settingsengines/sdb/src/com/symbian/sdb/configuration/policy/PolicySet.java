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
import java.util.ArrayList;
import java.util.List;

import com.symbian.sdb.configuration.policy.type.CapabilityType;
import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.exception.ValidationException;

public class PolicySet extends Policy {

	protected static final int UP_TO_3_CAPS_IDENTIFIER = 2;
	protected static final int UP_TO_7_CAPS_IDENTIFIER = 3;	

	protected List<CapabilityType> fCapabilities;
	protected PolicyType fPolicyType;	
	protected static final int MAX_COUNT = 7;

	
	/**
	 * Constructor to set PolicyType
	 * @param aPolicyType
	 */
	public PolicySet(String aPolicyType) throws ValidationException{
		fCapabilities = new ArrayList<CapabilityType>(MAX_COUNT);
		//new HashSet<CapabilityType>(MAX_COUNT);
		
		try{
			fPolicyType = PolicyType.valueOf(aPolicyType.toUpperCase());
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException(aPolicyType+" is not a valid Policy Type. ", ex);
		}
	}	
	
	/**
	 * Adds a capability to this policy object
	 * @param aCapType
	 */
	public void addCapability(String aCapabilityType) throws ValidationException{

		try{
			//add returns false for a set if the element is not unique
			if(!fCapabilities.contains(CapabilityType.valueOf(aCapabilityType.toUpperCase()))){
				fCapabilities.add(CapabilityType.valueOf(aCapabilityType.toUpperCase()));
			}
			else{
				throw new ValidationException("Capability list must contain unique capabilities. ");				
			}
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException(aCapabilityType+" is not a valid Capability Type. ", ex);
		}
	}
	
	/**
	 * Sets the policy Type of this policy
	 * @param aPolicyType
	 */
	public void setPolicyType(String aPolicyType) throws ValidationException{
		try{
			fPolicyType = PolicyType.valueOf(aPolicyType.toUpperCase());
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException(aPolicyType+" is not a valid Policy Type. ", ex);
		}
	}
	
	public PolicyType getPolicyType(){
		return fPolicyType;
	}
	
	public List<CapabilityType> getCapabilities(){
		return fCapabilities;
	}
	
	public void clearCapabilities(){
		fCapabilities.clear();
	}
	
	
	/**
	 * Generates the blob data for this policy
	 */
	public byte[] getBlobData(){

		ByteBuffer lBlobData = ByteBuffer.allocate(8);	

		List<CapabilityType> lCapabilities = getCapabilities();
		if(lCapabilities.size() >3){
			lBlobData.put(Integer.valueOf(UP_TO_7_CAPS_IDENTIFIER).byteValue());
		}
		else{
			lBlobData.put(Integer.valueOf(UP_TO_3_CAPS_IDENTIFIER).byteValue());
		}
		
		//Cycle through the capabilities and add to buffer bytes 1-7
		for(CapabilityType lCap : lCapabilities){
			lBlobData.put(lCap.toByte());
		}
		
		//Fill up the rest with no policy
		while(lBlobData.position()<8){
			lBlobData.put(NO_POLICY);
		}
		
		return lBlobData.array();
	}
	
	
	public void validate() throws ValidationException{		
		validate(MAX_COUNT);
	}
	
	/**
	 * Vaildates this policy cannot have more than aCapCount capabilities
	 * @param aCapCount
	 * @throws ValidationException
	 */
	public void validate(int aCapCount) throws ValidationException{
		
		if(fCapabilities.size()>aCapCount){
			throw new ValidationException("\nCan not have more than "+aCapCount+" Capabilities. ");
		}
	}

}
