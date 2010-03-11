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

import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.contacts.dbms.DBMSPreferences;
import com.symbian.sdb.contacts.sqlite.SQLitePreferences;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;

public class PreferencesManager {
	private Preferences preferences;
	public Preferences getPreferences() throws SDBExecutionException {
		if (preferences == null ) {
			throw new SDBExecutionException("Preferences not initialised");
		}
		return preferences;
	}

	public Preferences initPreferences(DBManager databaseManager, DBType dbType, Configuration configuration, TemplateMapper templateMapper) throws SDBExecutionException {
		preferences = getPreferences(dbType, configuration, templateMapper);
		init(databaseManager);
		return preferences;
	}
	
	private Preferences getPreferences(DBType dbType, Configuration configuration, TemplateMapper templateMapper) throws SDBExecutionException {
		switch (dbType) {
		case DBMS: {
			return new DBMSPreferences(configuration, templateMapper);
		}
		case SQLITE: {
			return new SQLitePreferences(configuration, templateMapper);
		}
		default :
			throw new SDBExecutionException("Unexpected CED db in contacts flow");
		}
	}

	private void init(DBManager databaseManager) throws SDBExecutionException{
		// retrieve preferences
		try{
			// if we already have preferences in the database, retrieve from db
			preferences.readFromDb(databaseManager);
		} catch(SDBExecutionException e) {
			try {
				preferences.readFromConfig();
			} catch (SDBExecutionException ex) {
				throw new SDBExecutionException("Could not read preferences values from config", ex);
			}
		}
	}
}
