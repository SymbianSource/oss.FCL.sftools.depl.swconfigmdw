// Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
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
// FieldsHeaderWriter.java
//

package com.symbian.sdb.contacts.sqlite.model;

import java.io.IOException;
import java.util.List;

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreException;
import com.symbian.store.StoreOutputStream;

public class FieldsHeaderWriter {

	public static byte[] write(List<FieldHeader> headers) {
		
		EmbeddedStore store = null;
		try {
			store = new EmbeddedStore();
			StoreOutputStream out = store.getOutputStream();
			store.setRoot(out.getStreamId());
			out.writeCardinality(headers.size());
			
			for (FieldHeader header : headers) {
				long attributes = header.getAttributesContainer().getValue();
				out.writeUInt32(attributes);
				
				if (header.getAttributesContainer().getFieldStorageType() != 0) {
					int stream = header.getStreamId();
					out.writeInt32(stream);
				}
				
				long id = header.getFieldId();
				out.writeUInt32(id);
				
				long guid = header.getContactFieldGuid();
				out.writeUInt32(guid);
				
				long hint = header.getHint();
				out.writeUInt32(hint);
				
				out.writeInt32(header.getFieldVcardMapping());
				
				int[] uids = header.getFieldAdditionalUIDValues();
				for (int i = 0; i < uids.length; i++) {
					out.writeInt32(uids[i]);
				}
				
				ContactFieldLabel label = header.getFieldLabel();
				
				out.writeInt32(label.getLength());
				if (label.getLength() > 0) {
					out.writeBuf8(label.getLabel());
				}
			}
			
			out.close();
			store.commit();
			return store.getContent();
		} catch (StoreException ex) {
			ex.printStackTrace();
		} catch (IOException ex) {
			ex.printStackTrace();
		} finally {
			if (store != null) {
				store.close();
			}
		}
		
		return null;
	}
	
}
