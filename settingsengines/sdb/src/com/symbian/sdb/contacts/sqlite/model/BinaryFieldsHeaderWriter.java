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
import com.symbian.store.StoreOutputStream;

public class BinaryFieldsHeaderWriter {
	
	public static byte[] write(FieldHeader[] headers) throws Exception{
		
		EmbeddedStore store = null;
		try {
			store = new EmbeddedStore();
			StoreOutputStream os = store.getOutputStream();
			store.setRoot(os.getStreamId());
			os.writeCardinality(headers.length);
			for (int i = 0; i < headers.length; i++) {
				
				os.writeInt32((int)headers[i].getAttributesContainer().getValue());;
				os.writeInt32(headers[i].getStreamId());
				os.writeInt32((int)headers[i].getFieldId());
				os.writeInt32((int)headers[i].getContactFieldGuid());
				if(headers[i].getAttributesContainer().hasOverridenLabel()) {
					os.writeInt32(headers[i].getFieldLabel().getLength());
					os.writeBuf8(headers[i].getFieldLabel().getLabel());
				}
			}
			os.close();		
			store.commit();
			//return contents in byte array
			return store.getContent();
		}
		finally {
			store.close();
		}
	}
} // end of class
