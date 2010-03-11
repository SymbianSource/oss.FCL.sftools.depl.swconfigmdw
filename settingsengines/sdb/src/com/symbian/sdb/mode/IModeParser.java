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

package com.symbian.sdb.mode;

/**
 * the interface for getting mode values:
 * database type: currently ced, dbms or sqlite
 * database mode: generic or contacts
 * database schema: any number with dots currently
 */
public interface IModeParser {
	
	/**
	 * sqlite, dbms or ced
	 * @return database target type 
	 */
	public DBType getDbType();
	
	/**
	 * generic or contacts
	 * @return database mode
	 */
	public DBMode getDbMode();
	
	/**
	 * 
	 * @return database target schema
	 */
	public String getDbSchema();
	
}
