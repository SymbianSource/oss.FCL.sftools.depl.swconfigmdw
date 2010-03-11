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
import java.nio.ByteOrder;

import com.symbian.sdb.configuration.policy.type.CapabilityType;
import com.symbian.sdb.configuration.policy.type.IDType;
import com.symbian.sdb.exception.ValidationException;

public class PolicyID extends PolicySet {

	protected IDType fType;
	protected String fId;	
	protected static final int MAX_COUNT = 3;
	
	public PolicyID(String aPolicyType, String aId, String aIdType) throws ValidationException{
		super(aPolicyType);
		try{
			fType = IDType.valueOf(aIdType.toUpperCase());
			fId = Integer.toString(Integer.parseInt(aId, 16));					
		}
		catch(IllegalArgumentException ex){
			throw new ValidationException(aIdType+" is not a valid ID Type. ", ex);
		}		
	}	
	
	public String getID(){
		return fId;
	}
	
	public IDType getIDType(){
		return fType;
	}

	
	public byte[] getBlobData(){		
		
		ByteBuffer lBlobData = ByteBuffer.allocate(8);			
		lBlobData.put(getIDType().toByte());
		
		//Cycle through the capabilities and add to buffer 
		for(CapabilityType lCap : getCapabilities()){
			if(lBlobData.position()<4){
				lBlobData.put(lCap.toByte());
			}
		}
		
		//Fill up the rest with -1		
		while(lBlobData.position()<4){
			lBlobData.put(NO_POLICY);
		}	
		
		//Now the last 4 bytes are the 32 bit VID/SID
		ByteBuffer lIdBuffer = ByteBuffer.allocate(4);			
		lIdBuffer.order(ByteOrder.LITTLE_ENDIAN);
		lIdBuffer.putInt(Integer.valueOf(fId));
		
		lBlobData.put(lIdBuffer.array());
		
		return lBlobData.array();
	}
	
	public void validate() throws ValidationException{
		validate(MAX_COUNT);
	}
	
	/**
	 * Validates the content
	 */
	public void validate(int aCapCount) throws ValidationException{
		
		try{
			super.validate(aCapCount);
		}
		catch(ValidationException ex){
			throw new ValidationException(ex.getMessage()+" when an ID is defined. ");
		}	
		
		//Validate the String ID is a valid integer
		try{
			Integer.valueOf(fId);
		}
		catch(NumberFormatException ex){
			throw new ValidationException(ex.getMessage()+". ", ex);
		}
	}
	
}
