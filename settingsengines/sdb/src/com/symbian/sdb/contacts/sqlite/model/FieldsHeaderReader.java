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
// BinaryFieldsHeaderReader.java
//



package com.symbian.sdb.contacts.sqlite.model;

import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreInputStream;

public class FieldsHeaderReader {
	
	public static FieldHeader[] read(byte[] blob) throws Exception{
		
		//Read root stream from store
		EmbeddedStore store = null;
		try {
			  store = new EmbeddedStore(blob);
			  StoreInputStream istream = store.getInputStream(store.rootStream());
			
			  //populate field header count
			  int fieldCount = istream.readCardinality();
			  FieldHeader[] headers = new FieldHeader[fieldCount];
			  for(int i = 0; i < fieldCount; i++ ) {
				 
				//Allocate header object 
				headers[i] = new FieldHeader();
				
				//Set attributes
				long attributes = istream.readUInt32();		

				headers[i].setAttributes((int)attributes);
				
				if (headers[i].getAttributesContainer().getFieldStorageType() != 0) {
					//Set streamId
					headers[i].setStreamId(istream.readInt32());
				}
				
				//Set templateId / field id
				headers[i].setFieldId(istream.readUInt32());

				//Set contact field guid
				headers[i].setContactFieldGuid(istream.readUInt32());

				//read contact field type
				//hint field
				if (!headers[i].getAttributesContainer().usesTemplateData()) {
					long hint = istream.readUInt32();

					headers[i].setHint((int)hint);
					if (headers[i].hasVCardMapping()) {
						headers[i].setFieldVcardMapping(istream.readInt32());
					}
	
					int additionalFieldCount = headers[i].getAdditionalFieldCount();
					if (additionalFieldCount > 0) {
						int[] additionalFields = new int[additionalFieldCount];
						for (int j = 0; j < additionalFieldCount;  j++) {
							additionalFields[j] = istream.readInt32();
						}	
						headers[i].setFieldAdditionalUIDValues(additionalFields);
					}
				}
				
				//read label
				if(headers[i].getAttributesContainer().hasOverridenLabel()) {
					int labelLength = istream.readInt32();
					headers[i].getFieldLabel().setLength(labelLength);
					if (labelLength > 0) {
						headers[i].getFieldLabel().setLabel(istream.readBuf8(labelLength)); 
					} else {
						headers[i].getFieldLabel().setLabel("");
					}
				}
			  }
			  istream.close();
			  return headers;
			} finally {
				store.close();
			}
	}

}
