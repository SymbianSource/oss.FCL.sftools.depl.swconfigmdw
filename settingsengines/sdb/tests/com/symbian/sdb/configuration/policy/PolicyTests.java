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


import junit.framework.Test;
import junit.framework.TestSuite;
import junit.textui.TestRunner;

import com.symbian.sdb.configuration.security.SymbianSecuritySettingsTest;
import com.symbian.sdb.util.ValidationExceptionTest;

public class PolicyTests extends TestSuite {

	public static void main(String[] args) {
		TestRunner.run(suite());
	}
	
	/**
	 * Test suite which groups together and runs all our settings tests
	 */
	
	public static Test suite() {
		TestSuite suite = new PolicyTests("Utils Tests");
		suite.addTestSuite(PolicyAlwaysTest.class);
		suite.addTestSuite(PolicyIDTest.class);
		suite.addTestSuite(PolicySetTest.class);
		suite.addTestSuite(ValidationExceptionTest.class);
		suite.addTestSuite(ParserTest.class);
		suite.addTestSuite(SymbianSecuritySettingsTest.class);
		return suite;
	}
	
	/*
	 * Constructor
	 */
	public PolicyTests(String name) {
		super(name);
	}
	
}
