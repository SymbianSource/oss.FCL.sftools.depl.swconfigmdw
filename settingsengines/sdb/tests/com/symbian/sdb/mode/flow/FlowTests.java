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

package com.symbian.sdb.mode.flow;

import com.symbian.sdb.mode.flow.ced.CedProcessTest;
import com.symbian.sdb.mode.flow.ced.CedSchemaTest;

import junit.framework.Test;
import junit.framework.TestSuite;

public class FlowTests {

	public static Test suite() {
		TestSuite suite = new TestSuite("Test for com.symbian.sdb.mode.flow");
		//$JUnit-BEGIN$
		suite.addTest(WorkflowFactoryTest.suite());
		suite.addTest(CedFlowTest.suite());
		suite.addTest(CedProcessTest.suite());
		suite.addTest(CedSchemaTest.suite());
		//$JUnit-END$
		return suite;
	}

}
