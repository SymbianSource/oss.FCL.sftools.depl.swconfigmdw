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
import java.util.List;

import com.symbian.sdb.exception.ContactHeaderCreationException;
import com.symbian.store.StoreInputStream;
import com.symbian.store.StoreOutputStream;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactHeaderForContact extends AbstractContactHeader  {

    public ContactHeaderForContact(List<ContactFieldHeader> contactFieldHeaders) throws ContactHeaderCreationException {
        super(contactFieldHeaders);
    }

    public ContactHeaderForContact(byte[] blob) throws ContactHeaderCreationException {
        super(blob);
    }

	@Override
	protected void readAdditionalMappingsFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		// No need to implement
		
	}

	@Override
	protected void readFieldHintValueFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		// No need to implement
		
	}

	@Override
	protected void readFieldLabelFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		// No need to implement
		
	}

	@Override
	protected void readVcardMappingFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		// No need to implement
		
	}

//	@Override
//	protected void persistAdditionalMappingsToBlob(StoreOutputStream stream,
//			ContactFieldHeader fieldHeader) throws IOException {
//		// No need to implement
//		
//	}

//	@Override
//	protected void persistFieldHintValueToBlob(StoreOutputStream stream,
//			ContactFieldHeader fieldHeader) throws IOException {
//		// No need to implement
//		
//	}

	public void persistFieldHintValueToBlob(StoreOutputStream stream, ContactFieldHeader fieldHeader) throws IOException {
		if (0 != fieldHeader.getFieldHint())	{	
			stream.writeUInt32(fieldHeader.getFieldHint()); // write field hint
		}
	}

	@Override
	protected void persistFieldLabelToBlob(StoreOutputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		// No need to implement
		
	}
    
    

}
