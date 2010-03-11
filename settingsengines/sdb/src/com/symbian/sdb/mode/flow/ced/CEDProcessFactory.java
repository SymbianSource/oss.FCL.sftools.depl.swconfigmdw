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

package com.symbian.sdb.mode.flow.ced;

/**
 * Generates the relevant ICedProcess dependent on the the schema specified 
 * TODO: Candidate for IOC
 */
public class CEDProcessFactory {

	/**
	 * 
	 * @param schema representing the specific output type required
	 * @return An implementation of ICedProcess that will produce the require output given the schema
	 */
	public static ICedProcess getProcess(CedSchema schema){
		return new CedProcess(schema);
	}
}
