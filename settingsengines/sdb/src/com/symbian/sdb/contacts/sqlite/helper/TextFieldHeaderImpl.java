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

import com.symbian.sdb.contacts.sqlite.BitsOperationsUtil;


/**
 * @author krzysztofZielinski
 *
 */
public class TextFieldHeaderImpl implements FieldHeader {

    private long contactFieldAttributes;
    private int contactFieldGuid;
    private int templateFieldId;
    
    public void createNewFieldHeader() {
        contactFieldAttributes = 0;
        contactFieldGuid = 0;
        templateFieldId = 0;
    }

    public void setContactFieldAttributes(long contactFieldAttributes) {
        this.contactFieldAttributes = contactFieldAttributes;
    }

    public void setContactFieldGuid(int guid) {
        this.contactFieldGuid = guid;
    }

    public void setTemplateFieldId(int templateFieldId) {
        this.templateFieldId = templateFieldId;
    }

    public byte[] getFieldHeader() {
        
        int[] fieldHeaderAttributes = { (int)contactFieldAttributes, contactFieldGuid, templateFieldId};
        
        byte[] fieldHeaderBytes = transformAttributesToBytes(fieldHeaderAttributes);
        
        return fieldHeaderBytes;
    }

    private byte[] transformAttributesToBytes(int[] fieldHeaderAttributes) {
        int numberOfBytesInInteger = 4;
        int numberOfIntegerFields = 3;

        byte[] fieldHeaderBytes = new byte[numberOfBytesInInteger * numberOfIntegerFields];
        
        byte[] attribute;
        for (int i = 0; i < fieldHeaderAttributes.length; i++) {
            attribute = BitsOperationsUtil.getBytesFromInt(fieldHeaderAttributes[i]);
            System.arraycopy(attribute, 0, fieldHeaderBytes, i * numberOfBytesInInteger, numberOfBytesInInteger);
        }
        return fieldHeaderBytes;
    }

    public int getContactFieldAttributes() {
        return (int)contactFieldAttributes;
    }

    public int getContactFieldGuid() {
        return contactFieldGuid;
    }

    public int getTemplateFieldId() {
        return templateFieldId;
    }
    
}
