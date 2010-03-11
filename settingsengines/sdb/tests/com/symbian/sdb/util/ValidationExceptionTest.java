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

package com.symbian.sdb.util;

import junit.framework.TestCase;

import com.symbian.sdb.exception.ValidationException;

public class ValidationExceptionTest extends TestCase {

	ValidationException fEx1;
	ValidationException fEx2;
	ValidationException fEx3;
	
	public void setUp(){		
		fEx1 = new ValidationException("Test Exception");
		fEx2 = new ValidationException("Test Exception", new Throwable());
		fEx3 = new ValidationException(new Throwable());
	}
	
	public void testMessages(){
		assertNotNull(fEx1.getMessage());
		assertNotNull(fEx2.getMessage());
		assertNotNull(fEx3.getCause());
	}
}
