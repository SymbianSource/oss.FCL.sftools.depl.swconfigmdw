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

package com.symbian.sdb.contacts.sqlite.model.creator;

import java.util.Set;

import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.sqlite.helper.ContactFieldAttributes;
import com.symbian.sdb.contacts.sqlite.helper.FieldHeader;
import com.symbian.sdb.contacts.sqlite.helper.TextFieldHeaderBlobBuilder;
import com.symbian.sdb.contacts.sqlite.helper.TextFieldHeaderImpl;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactFieldAttributes;
import com.symbian.sdb.contacts.sqlite.model.StorageType;

/**
 * @author krzysztofZielinski
 *
 */
public class TextFieldsBuilder {

    private Set<ContactField> contactFields;
    
    public TextFieldsBuilder(Set<ContactField> fields) {
        this.contactFields = fields;
    }

    public String createTextFields(Set<ContactField> fields) {
        StringBuffer textFieldsBuffer = new StringBuffer();
        
        for (ContactField contactField : fields) {
            textFieldsBuffer.append(contactField.getTextValue());
            textFieldsBuffer.append((char)0);
        }
        return textFieldsBuffer.toString();
    }


    public byte[] createTextFieldsHeader() {
        TextFieldHeaderBlobBuilder blobBuilder = new TextFieldHeaderBlobBuilder();
        for (ContactField contactField : contactFields) {
            FieldHeader fieldHeader = createFieldHeader(contactField);
            blobBuilder.addTextFieldHeader(fieldHeader);    
        }
        blobBuilder.tryToBuildBlob();
        
        return blobBuilder.getBlob();
    }

    private FieldHeader createFieldHeader(ContactField contactField) {
        FieldHeader fieldHeader = new TextFieldHeaderImpl();
        fieldHeader.createNewFieldHeader();
        
        ContactFieldAttributes contactFieldAttributes = createFieldAttributes(contactField);
        fieldHeader.setContactFieldAttributes((int)contactFieldAttributes.getValue());
        int templateIdForCurrentField = getTemplateIdForField(contactField);
        fieldHeader.setTemplateFieldId(templateIdForCurrentField);
        fieldHeader.setContactFieldGuid(getFieldId(contactField));
        return fieldHeader;
    }

    private int getFieldId(ContactField contactField) {
        // TODO KZ: template manager should be queried (hardcoded value !!!)
        return contactField.getTemplateFieldId(); 
    }


    private ContactFieldAttributes createFieldAttributes(ContactField contactField) {
        ContactFieldAttributes contactFieldAttributes = new ContactFieldAttributes();
        contactFieldAttributes.addAttribute(SQLiteContactFieldAttributes.SYNCHRONIZE);
        contactFieldAttributes.addAttribute(SQLiteContactFieldAttributes.UNKNOWN);
        contactFieldAttributes.addAttribute(SQLiteContactFieldAttributes.USE_TEMPLATE_DATA);
        contactFieldAttributes.setStorageType(0);

        return contactFieldAttributes;
    }
    
    private int getTemplateIdForField(ContactField contactField) {
        // TODO KZ: assume system template
        return 0;
    }

    private StorageType getStorageTypeForField(ContactField contactField) {
        // TODO KZ: template manager should be queried 
        return StorageType.TEXT;
    }
    
    

}
