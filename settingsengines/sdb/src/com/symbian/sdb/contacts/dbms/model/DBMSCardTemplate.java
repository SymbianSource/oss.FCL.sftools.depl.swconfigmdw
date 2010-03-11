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

/**
 * Represents additional template. Exists if there is more then one template (system template).
 * 
 * @author krzysztofzielinski
 *
 */
public class DBMSCardTemplate extends DBMSTemplate  {

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.dbms.model.DBMSTemplate#initializeFields()
     */
    @Override
    protected void initializeFields() {
        this.setType(ContactType.CARD_TEMPLATE);
        this.identityTable = new IdentityTable(ContactType.CARD_TEMPLATE);
    }
}
