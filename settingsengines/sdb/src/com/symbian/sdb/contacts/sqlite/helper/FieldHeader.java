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

/**
 * @author krzysztofZielinski
 *
 */
public interface FieldHeader {

    public void createNewFieldHeader();

    public byte[] getFieldHeader();

    public void setContactFieldAttributes(long contactFieldAttributes);

    public void setTemplateFieldId(int templateFieldId);

    public void setContactFieldGuid(int guid);
    
    public int getContactFieldAttributes();

    public int getContactFieldGuid();

    public int getTemplateFieldId();

}
