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
// ContactTextBlob.java
//



package com.symbian.sdb.contacts.dbms.model;

import java.io.IOException;
import org.apache.commons.io.IOUtils;
import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreException;
import com.symbian.store.StoreOutputStream;

/**
 * Used to write data in Symbian Store format 
 * 
 * @author krzysztofZielinski
 *
 */
public class StoreBlob extends AbstractContactBlobField   {

	private EmbeddedStore store = null;
	private int streamID = 0;

	public StoreBlob() { 
        super();
    }


    public byte[] persistToBlob() throws StoreException {
    	store.commit();
    	store.close();
    	return store.getContent();
    }


	public StoreOutputStream createStream() throws StoreException {
		return store.getOutputStream();
	}


	public void closeStore() throws StoreException {
		store.commit();
		value = store.getContent();
		store.close();      	
	}


	public void createStore() throws StoreException {
		store = new EmbeddedStore();	
	}
}
