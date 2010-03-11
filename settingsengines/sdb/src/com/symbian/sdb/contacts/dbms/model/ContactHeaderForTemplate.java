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

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.store.StoreInputStream;
import com.symbian.store.StoreOutputStream;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactHeaderForTemplate extends AbstractContactHeader {

    public ContactHeaderForTemplate(byte[] blob) throws Exception {
        super(blob);
    }

    public ContactHeaderForTemplate(List<ContactFieldHeader> contactFieldHeaders) throws Exception {
        super(contactFieldHeaders);
    }
    
    @Override
	public void readAdditionalMappingsFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
    	// read hint value, additional fields and vCard mapping
        int additionalFieldCount = fieldHeader.getAttributesContainer().getAdditionalFieldCount();
        if (additionalFieldCount > 0) {
            setAdditionalMappings(stream, fieldHeader, additionalFieldCount);
        }
	}

	@Override
	public void readFieldHintValueFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		fieldHeader.setFieldHint(stream.readUInt32());
		
	}

	@Override
	public void readFieldLabelFromBlob(StoreInputStream stream,
							ContactFieldHeader fieldHeader) throws IOException {
		// read and set label
        ContactFieldLabel label = new ContactFieldLabel();
        if (fieldHeader.hasOverridenLabel()) {
            int length = stream.readInt32();
            label.setLength(length);
            if (length == 0) {
                label.setLabel("");
            } else {
                label.setLabel(stream.readBuf16(length));
            }
            fieldHeader.setFieldLabel(label);
        }
		
	}

	@Override
	public void readVcardMappingFromBlob(StoreInputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		fieldHeader.setFieldVcardMapping(stream.readInt32());
	}

	@Override
	public void persistFieldLabelToBlob(StoreOutputStream stream,
							ContactFieldHeader fieldHeader) throws IOException {
		//write field label
        if (fieldHeader.hasOverridenLabel()) {
            stream.writeInt32(fieldHeader.getFieldLabel().getLength());
            if (fieldHeader.getFieldLabel().getLength() > 0)	{
            	stream.writeBuf16(fieldHeader.getFieldLabel().getLabel());
            }
        }
	}

	
//~ Private methods ----------------------------------------------------
	private void setAdditionalMappings(StoreInputStream stream,
						ContactFieldHeader fieldHeader, int additionalFieldCount)
			throws IOException {
		int[] additionalFields = new int[additionalFieldCount];
		readMappingFromStream(stream, additionalFields);
		fieldHeader.setFieldAdditionalUIDValues(additionalFields);
	}

	private void readMappingFromStream(StoreInputStream stream, 
			int[] additionalFields)
	throws IOException {
		for (int j = 0; j < additionalFields.length; j++) {
			additionalFields[j] = stream.readInt32();
		}
	}
	
	@Override
	public void persistFieldHintValueToBlob(StoreOutputStream stream, ContactFieldHeader fieldHeader) throws IOException {
		stream.writeUInt32(fieldHeader.getFieldHint()); // write field hint
	}
}
