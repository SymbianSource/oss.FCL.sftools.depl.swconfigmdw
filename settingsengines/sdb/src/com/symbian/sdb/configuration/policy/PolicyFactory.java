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

import org.apache.log4j.Logger;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import com.symbian.sdb.configuration.policy.type.IDType;
import com.symbian.sdb.exception.ValidationException;
import com.symbian.sdb.util.NodeWrapper;

public final class PolicyFactory {

	/** Static logger */
	private static final Logger sLogger = Logger.getLogger(PolicyFactory.class);
	
	public static Policy createPolicy(Element aPolicyElement) throws ValidationException{
		
		// Firstly Check that the policy type has been set		
		if(!aPolicyElement.hasAttribute("type")){
			// Should never happen if we validate with schema 
			throw new ValidationException("Policy type not set: "+ aPolicyElement.getNodeName()+". ");
		}
		
		String lPolicyType = aPolicyElement.getAttribute("type");
		
		if(aPolicyElement.hasAttribute("always")){
			PolicyAlways lPolAlways = new PolicyAlways(lPolicyType, aPolicyElement.getAttribute("always"));
			
			if(aPolicyElement.hasChildNodes()){
				sLogger.warn("Policy node has capabilty children and always attribute set. Ignoring capabilities. ");
			}
			
			//Validate policy element then send it back
			lPolAlways.validate();
			return lPolAlways;
		}
		
		PolicySet lPolicyWithCapabilities;
		if(aPolicyElement.hasAttribute(IDType.VID.toString()) && aPolicyElement.hasAttribute(IDType.SID.toString())){
			//This is an error - cant specify both
			throw new ValidationException("\nIn policy element, cannot specify VID and SID. ");
		}
		else if(aPolicyElement.hasAttribute(IDType.VID.toString())){
			//Dealing with a policy with ID Type of VID
			lPolicyWithCapabilities = new PolicyID(lPolicyType, aPolicyElement.getAttribute(IDType.VID.toString()), IDType.VID.toString());
		}
		else if(aPolicyElement.hasAttribute(IDType.SID.toString())){
			//Dealing with a policy with ID Type of SID
			lPolicyWithCapabilities = new PolicyID(lPolicyType, aPolicyElement.getAttribute(IDType.SID.toString()), IDType.SID.toString());
		}
		else{
			lPolicyWithCapabilities = new PolicySet(lPolicyType);
		}
		
		//Now we add the capabilities to this policy
		NodeList lCapabilityList = aPolicyElement.getChildNodes();
		StringBuilder lErrors = new StringBuilder();		
		
		try{
			addCapabilities(lPolicyWithCapabilities, lCapabilityList);
		}
		catch(ValidationException ex){
			lErrors.append(ex.getMessage());
			sLogger.debug(ex);
		}

		//Validate our policy element		
		try{
			lPolicyWithCapabilities.validate();
		}
		catch(ValidationException ex){
			lErrors.append(ex.getMessage());
			sLogger.debug(ex);
		}
		
		//throw the chained errors
		if(lErrors.length() > 0){
			throw new ValidationException(lErrors.toString());
		}

		return lPolicyWithCapabilities;
		
	}
	
	private static void addCapabilities(PolicySet lPolicy, NodeList lCapabilityList) throws ValidationException{

		StringBuilder lErrors = new StringBuilder();
		boolean lFoundCapabilities = false;
		
		for(Node lCapNode : wrap(lCapabilityList)){
			lFoundCapabilities = true;
			if( (lCapNode.getNodeType() == Node.ELEMENT_NODE) && (lCapNode.getNodeName().equalsIgnoreCase("capability"))){
			
				try{
					lPolicy.addCapability(((Element)lCapNode).getAttribute("type"));
				}
				catch(ValidationException ex){
					lErrors.append("\n"+ex.getMessage());					
				}
			}
		}
		
		if(lErrors.length()>0){
			throw new ValidationException(lErrors.toString());
		}
		
		if(!lFoundCapabilities){
			throw new ValidationException("Must Specify at least one Capability");
		}
	}
	
	private static Iterable<Node> wrap(NodeList aNodeList){
		return new NodeWrapper(aNodeList);
	}
}
