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

package com.symbian.sdb.contacts.importer;

import java.util.Set;

import com.symbian.sdb.contacts.vcard.VCardContact;

/**
 * Responsible for reading vCardContacts from vCard file.
 * 
 * @author krzysztofZielinski
 *
 */
public interface VCardReader {

    /**
     * Reads vCard contacts from location matching given path expression
     * 
     * @param vCardFilesPath
     * @return
     */
    public Set<VCardContact> readContacts(String vCardFilesPath);
}
