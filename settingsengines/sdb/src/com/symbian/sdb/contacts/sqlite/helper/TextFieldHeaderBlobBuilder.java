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

package com.symbian.sdb.contacts.sqlite.helper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreException;
import com.symbian.store.StoreOutputStream;

/**
 * @author krzysztofZielinski
 *
 */
public class TextFieldHeaderBlobBuilder {

    private byte[] blob;
    private List<FieldHeader> fieldHeaders = new ArrayList<FieldHeader>();
    
    public byte[] getBlob() {
        return blob;
    }
    
    public void addTextFieldHeader(FieldHeader textFieldHeader)   {
        fieldHeaders.add(textFieldHeader);
    }
    
    public void tryToBuildBlob() {
    	EmbeddedStore store = null;
    	try {
			store = buildBlob();
		} catch (IOException e) {
			throw new ContactsExeption(e.getMessage());
		} finally {
			closeStore(store);
		}
    }

    private void closeStore(EmbeddedStore store) {
        if (store!=null)	{
        	store.close();
        }
    }

    private EmbeddedStore buildBlob() throws StoreException, IOException {
        EmbeddedStore store;
        store = new EmbeddedStore();
        StoreOutputStream outstream = store.getOutputStream();

        store.setRoot(outstream.getStreamId());

        outstream.writeCardinality(fieldHeaders.size());
        for (FieldHeader fieldHeader : fieldHeaders) {
        	writeHeader(fieldHeader, outstream);
        }
        outstream.flush();
        outstream.close();
        store.commit();
        this.blob = store.getContent();
        
        return store;
    }

    private void writeHeader(FieldHeader fieldHeader, StoreOutputStream outstream) throws IOException {
        outstream.writeInt32(fieldHeader.getContactFieldAttributes());
        // TODO temp repeat field guid twice
//        outstream.writeInt32(fieldHeader.getTemplateFieldId());
        outstream.writeInt32(fieldHeader.getContactFieldGuid());
        outstream.writeInt32(fieldHeader.getContactFieldGuid());
    }
}
