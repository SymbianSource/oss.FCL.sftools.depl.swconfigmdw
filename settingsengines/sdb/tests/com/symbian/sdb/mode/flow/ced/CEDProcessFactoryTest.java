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

import junitx.framework.PrivateTestCase;


/**
 * @author jamesclark
 *
 */
public class CEDProcessFactoryTest extends PrivateTestCase{

	
	/**
	 * @param arg0
	 */
	public CEDProcessFactoryTest(String arg0) {
		super(arg0);
	}

	public void testGetProcessForSchema() throws Exception{
		ICedProcess p = CEDProcessFactory.getProcess(CedSchema.ced95);
		assertEquals("Check that the correct type of IProcess was returned",CedProcess.class,p.getClass());
		assertEquals("Check that the internal schema is correct", CedSchema.ced95, get(p, "_schema"));
	}
}
