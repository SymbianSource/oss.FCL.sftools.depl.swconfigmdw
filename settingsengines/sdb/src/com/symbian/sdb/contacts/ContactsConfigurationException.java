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

package com.symbian.sdb.contacts;

@SuppressWarnings("serial")
public class ContactsConfigurationException extends RuntimeException {

    public ContactsConfigurationException() {
        super();
    }

    public ContactsConfigurationException(String message, Throwable cause) {
        super(message, cause);
    }

    public ContactsConfigurationException(String message) {
        super(message);
    }

    public ContactsConfigurationException(Throwable cause) {
        super(cause);
    }

}