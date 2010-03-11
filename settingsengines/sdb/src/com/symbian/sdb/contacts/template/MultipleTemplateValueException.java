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

package com.symbian.sdb.contacts.template;

public class MultipleTemplateValueException extends Exception {

    /** SerialVersionUID */
    static final long serialVersionUID = -4544769666886838814L;
    
    /** 
     * Constructor.
     * 
     * @param message the detail message. The detail message is saved for later retrieval by the Throwable.getMessage() method.
     */
    public MultipleTemplateValueException(String message) {
        super(message); 
    }
    
    /** 
     * Constructor.
     * 
     * @param message the detail message. The detail message is saved for later retrieval by the Throwable.getMessage() method.
     * @param cause - the cause (which is saved for later retrieval by the Throwable.getCause() method). (A null value is permitted, and indicates that the cause is nonexistent or unknown.)
     *   
     */
    public MultipleTemplateValueException(String message, Throwable cause) {
        super(message, cause); 
    }
    
    /** 
     * Constructor.
     * 
     * @param cause - the cause (which is saved for later retrieval by the Throwable.getCause() method). (A null value is permitted, and indicates that the cause is nonexistent or unknown.)
     */
    public MultipleTemplateValueException(Throwable throwable) {
        super(throwable); 
    }
}
