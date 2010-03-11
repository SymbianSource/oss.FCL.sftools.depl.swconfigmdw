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

package com.symbian.sdb.cmd;

import junit.framework.Test;
import junit.framework.TestSuite;

public class CmdTests {

	public static Test suite() {
		TestSuite suite = new TestSuite("Test for com.symbian.sdb.cmd");
		//$JUnit-BEGIN$
		suite.addTest(ModeValidatorTest.suite());
		suite.addTest(CommandLinev2Test.suite());
		//$JUnit-END$
		return suite;
	}

}
