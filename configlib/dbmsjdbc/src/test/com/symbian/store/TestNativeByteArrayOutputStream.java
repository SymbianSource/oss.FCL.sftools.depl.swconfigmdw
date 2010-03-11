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

package com.symbian.store;

import java.io.IOException;
import java.util.Arrays;

import junit.framework.TestCase;

public class TestNativeByteArrayOutputStream extends TestCase {
	public void setUp(){	
	}
	public void tearDown(){	
	}
	
	public void testSmoke() throws IOException{
		NativeByteArrayOutputStream out = null;
		byte [] expectedBlob = { (byte)1, (byte)2, (byte)3, (byte)4 }; 
		byte [] blob = null;
		try{
			out = new NativeByteArrayOutputStream();
			out.writeInt32(0x04030201);
			blob = out.toByteArray();
		} finally {
			if ( out != null ) { try{out.close();out=null;}catch(Exception e){}}
		}
		assertTrue(Arrays.equals(expectedBlob, blob));
	}
}
