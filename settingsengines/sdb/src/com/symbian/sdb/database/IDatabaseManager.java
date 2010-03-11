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

package com.symbian.sdb.database;

import java.sql.Connection;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;

/**
 *
 */
public interface IDatabaseManager {

    /* (non-Javadoc)
     * @see com.symbian.sdb.database.DatabaseManager#setDbConnection(java.sql.Connection)
     */
    public void setConnection(Connection aConnection);

    /* (non-Javadoc)
     * @see com.symbian.sdb.database.DatabaseManager#openDatabase(java.lang.String)
     */
    public void openConnection(DBType dbType, String aFilename) throws SDBExecutionException;

    /* (non-Javadoc)
     * @see com.symbian.sdb.database.DatabaseManager#closeDatabase()
     */
    public void closeConnection();
}
