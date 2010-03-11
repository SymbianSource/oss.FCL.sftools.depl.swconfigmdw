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

import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.sqlite.model.ContactType;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactCard;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.util.SymbianSpecificUtils;

/**
 * Class responsible for SQLite specific contacts creation
 * 
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactBuilder {

    private SQLiteContactCard sqLiteContact;
    
    public void createNewContact(Contact genericContact)    {
        sqLiteContact = new SQLiteContactCard(genericContact);
        
        // TODO: Set real template ID (may not be system template)
        setSystemTemplate(sqLiteContact); 
        setTypeFlags(genericContact);
        setDateBasedFields();

        sqLiteContact.setAccessCount(0);

        createTextFieldsWithHeaderBlob(genericContact);

        createBinaryFieldsBlobWithHeaderBlob();
    }

    private void createBinaryFieldsBlobWithHeaderBlob() {
        // TODO: temporarily hardcoded values
        String binaryFieldsHeader = "0400000000";
        sqLiteContact.setBinaryFieldsHeader(binaryFieldsHeader);
        byte[] binaryFields = {0x00, 0x00, 0x00, 0x00};
        sqLiteContact.setBinaryFields(binaryFields);
    }

    private void createTextFieldsWithHeaderBlob(Contact genericContact) {
        TextFieldsBuilder textFieldsBuilder = new TextFieldsBuilder(genericContact.getFields());

        byte[] textFieldsHeader = textFieldsBuilder.createTextFieldsHeader();
        sqLiteContact.setTextFieldsHeader(textFieldsHeader);
        
        String textFields = textFieldsBuilder.createTextFields(genericContact.getFields());
        sqLiteContact.setTextFields(textFields);
    }
    

    private void setDateBasedFields() {
        long currentSymbianTimestamp = SymbianSpecificUtils.createCurrentSymbianTimestamp();
        
        sqLiteContact.setCreationDate(currentSymbianTimestamp);
        sqLiteContact.setLastModification(currentSymbianTimestamp);
        sqLiteContact.setGuidString(Long.toHexString(currentSymbianTimestamp));
    }


    private void setSystemTemplate(SQLiteContactCard sqLiteContact) {
        sqLiteContact.setTemplateId((int)ITemplateModel.SYSTEM_TEMPLATE_ID);
    }

    private void setTypeFlags(Contact genericContact) {
        TypeFlagsBuilder typeFlagsBuilder = new TypeFlagsBuilder();
        typeFlagsBuilder.createNewTypeFlags(ContactType.CARD);
        
        typeFlagsBuilder.createContactHintFields(genericContact);
        typeFlagsBuilder.createAttributes();

        sqLiteContact.setTypeFlags(typeFlagsBuilder.getTypeFlags());
    }

    public SQLiteContactCard getSqLiteContact() {
        return this.sqLiteContact;
    }
}
