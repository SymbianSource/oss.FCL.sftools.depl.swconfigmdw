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

package com.symbian.sdb;

import java.util.Properties;

import org.junit.After;
import org.junit.BeforeClass;

/**
 * @author jamesclark
 *
 */
public class PropertyRestorerTestCase  {

	protected static Properties original;

	/**
	 * Before the test class is executed store the system properties
	 */
	@BeforeClass
	public static void storeProperties() {
		original = (Properties)System.getProperties().clone();
	}
	
	public static void setPropertiesForDBPaths()    {
        System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("org.sqlite.lib.path", "lib/");
    }

	/**
	 * After each test is complete copy the original properties back to system
	 */
	@After
	public void restoreProperties() {
		System.setProperties((Properties)original.clone());
	}

}
