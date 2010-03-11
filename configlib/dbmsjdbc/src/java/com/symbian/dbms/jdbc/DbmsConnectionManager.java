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

package com.symbian.dbms.jdbc;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

public class DbmsConnectionManager {
	static Map<String, DbmsConnection> connections = new HashMap<String, DbmsConnection>();

	public static synchronized DbmsConnection getConnection(String file) {
		return connections.get(file);
	}

	public static synchronized DbmsConnection createConnection(String file, Properties info) throws SQLException {
		DbmsConnection connection = new DbmsConnection(file, info);
		connections.put(file, connection);
		return connection;
	}

	public static synchronized DbmsConnection releaseConnection(String file) {
		return connections.remove(file);
	}
}
