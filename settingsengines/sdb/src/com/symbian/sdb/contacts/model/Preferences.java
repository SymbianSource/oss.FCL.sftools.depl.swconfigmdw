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

package com.symbian.sdb.contacts.model;

import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.util.LongArray;

/**
 * Interface for reading and writing the contents of the Preferences table.
 * 
 * Implemented for both SQLite and DBMS.
 */
public interface Preferences {
	void readFromConfig() throws SDBExecutionException;
	void readFromDb(DBManager manager) throws SDBExecutionException;
	void persistToDb(DBManager manager) throws SDBExecutionException;
	void addGroupId(int id);
	void addCardTemplateId(int id);
	LongArray getCardTemplateIds();
	LongArray getGroupIds();
}
