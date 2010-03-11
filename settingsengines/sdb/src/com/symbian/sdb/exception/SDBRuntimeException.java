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

@SuppressWarnings("serial")
public class SDBRuntimeException extends RuntimeException {

	/**
	 * @param message
	 * @param cause
	 */
	public SDBRuntimeException(String message, Throwable cause) {
		super(message, cause);
	}

	/**
	 * @param message
	 */
	public SDBRuntimeException(String message) {
		super(message);
	}

	/**
	 * @param cause
	 */
	public SDBRuntimeException(Throwable cause) {
		super(cause);
	}
}
