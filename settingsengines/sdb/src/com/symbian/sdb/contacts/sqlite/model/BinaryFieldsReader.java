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

package com.symbian.sdb.contacts.sqlite.model;

import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreInputStream;

public class BinaryFieldsReader {
	
	public static BinaryField[] read(byte[] fieldsData, FieldHeader[] fieldHeader) throws Exception{
		
		//Create binary field array
		BinaryField[] fields = new BinaryField[fieldHeader.length];
		EmbeddedStore store = null;
		try {
			
			//unwrap data stored in store
			store  = new EmbeddedStore(fieldsData);
			
			//Iterate through fields and dump into array
			for(int i = 0; i < fieldHeader.length; i++) {
				StoreInputStream is = store.getInputStream(fieldHeader[i].getStreamId());
				fields[i] = new BinaryField();
				//Set header
				fields[i].setHeader(fieldHeader[i]);
				
				//Read length and set it to object
				int length = is.readInt32();
				fields[i].setLength(length);
				
				//Read data and set it object
				fields[i].setData(is.readBuf8Raw(length));
			}
			return fields;
		}
		finally {
			store.close();
		}
	}

}
