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

public class BinaryFieldsWriter {
	
	public static byte[] write(BinaryField fields[]) throws Exception {
		
		EmbeddedStore store = null;
		try {	
			store = new EmbeddedStore();
			for (int i = 0;  i < fields.length; i++) {
			
				StoreOutputStream os = store.getOutputStream();
				fields[i].getHeader().setStreamId(os.getStreamId());
				os.writeInt32(fields[i].getLength());
				os.writeBuf8Raw(fields[i].getData());
				os.close();
			}
			store.commit();
			return store.getContent();
		}
		catch (Exception se) {
			throw se;
		}
		finally {
			store.close();
		}
		
	}
}
