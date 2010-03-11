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
// DBTests.java
//

package com.symbian.sdb.database;

import junit.framework.Test;
import junit.framework.TestSuite;
import junit.textui.TestRunner;

/***
 * This is a suite of tests for testing the Commands
 * @author Symbian Ltd. 2006-2007
 * 
 */
public class DBTests extends TestSuite {

	public static void main(String[] args) {
		TestRunner.run(suite());
	}
	
	public static Test suite() {
		TestSuite suite = new DBTests("Database Tests");
		suite.addTestSuite(DBManagerTest.class);	
		return suite;
	}
	
	public DBTests(String name) {
		super(name);
	}
	
}
