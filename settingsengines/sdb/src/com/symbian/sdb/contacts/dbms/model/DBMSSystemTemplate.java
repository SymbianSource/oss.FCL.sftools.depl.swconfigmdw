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

import com.symbian.sdb.contacts.template.ITemplateModel;

/**
 * Represents system template (default template stored with id=0).
 * 
 * @author krzysztofzielinski
 *
 */
public class DBMSSystemTemplate extends DBMSTemplate {

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.dbms.model.DBMSTemplate#initializeFields()
     */
    @Override
    protected void initializeFields() {
        this.setType(ContactType.TEMPLATE);
        this.identityTable = new IdentityTable(ContactType.TEMPLATE);
        
        this.setId(ITemplateModel.SYSTEM_TEMPLATE_ID);
    }
    
    
}
