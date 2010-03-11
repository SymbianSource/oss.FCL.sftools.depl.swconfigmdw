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

package com.symbian.sdb.exception;

/***
 *  This is the exception class to handle option validation exceptions
 */ 

public class SDBValidationException extends Exception {

    /** SerialVersionUID */
    static final long serialVersionUID = -4544769666886838817L;
    
    public SDBValidationException(String message) {
        super(message); 
    }
    
    public SDBValidationException(String message, Throwable e) {
        super(message, e); 
    } 
} //end of class
