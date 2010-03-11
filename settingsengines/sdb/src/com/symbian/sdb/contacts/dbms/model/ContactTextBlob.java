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

package com.symbian.sdb.contacts.dbms.model;

import java.io.IOException;
import org.apache.commons.io.IOUtils;
import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreOutputStream;

/**
 * Used to store binary field content (DB column is called CM_TextBlob) 
 * 
 * @author krzysztofZielinski
 *
 */
public class ContactTextBlob extends AbstractContactBlobField   {

	/**
	 * @deprecated  Not for public use.
	 *    This class should not take data in the constructor as it needs to be in store format and a stream ID created.
	 *    Use {@link #persistToBlob(byte[] bytesToStore)}}
	 */

	@Deprecated
	public ContactTextBlob(byte[] valueToSet)	{
		this.value = valueToSet;
	}
	
	public ContactTextBlob() { 
        super();
    }

	/**
	 * 
	 * @param bytesToStore
	 * @return
	 * @throws ContactsExeption
	 */
    public int persistToBlob(byte[] bytesToStore) throws ContactsExeption {
    	EmbeddedStore store = null;
        StoreOutputStream stream = null;
        int streamID = 0;
        
        try {
            store = new EmbeddedStore();
            stream = store.getOutputStream();
            
            streamID = stream.getStreamId();

            stream.writeInt32(bytesToStore.length);
            stream.writeBuf8Raw(bytesToStore);

            store.commit();
            value = store.getContent();
        }
        catch (IOException e) {
        	throw new ContactsExeption("Problem occured when writing binary data to store stream.",e);
        }
        finally {
            IOUtils.closeQuietly(stream);    
            store.close();      	
        }
        
        return streamID;
    }
}
