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

import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class ModeParser implements IModeParser {
	private static final Pattern dbpattern = Pattern.compile("^(sqlite|dbms|ced)(?:\\.(.*))?$");
	
/**
sqlite
dbms

sqlite.contacts
dbms.contacts

ced

databaseManager type=sqlite|dbms|ced
databaseManager mode=generic|contacts
databaseManager schema=null|.....
 */
	
	//private static final String DATABASE_TYPE = "sdb.dbtype";
	//private static final String DATABASE_MODE = "sdb.dbmode";
	//private static final String DATABASE_SCHEMA = "sdb.dbschema";
	
	private String dbtype;
	private String dbmode = "generic";
	private String schema;
	
	public ModeParser(String mode) {
		parse(mode);
	}
	
	private void parse(String mode) {
		Matcher matcher = dbpattern.matcher(mode);
		if (matcher.matches()) {
			dbtype = matcher.group(1);
			
			if (!dbtype.equals("ced") && matcher.group(2) != null) {
				boolean contacts  = matcher.group(2).startsWith("contacts");
				if (contacts) {
					dbmode = "contacts";
				}
			} else if (dbtype.equals("ced") && matcher.group(2) != null) {
				schema = matcher.group(2).trim();
			}

		} 
		matcher.reset();
	}
	
	public DBType getDbType() {
		return DBType.valueOf(dbtype.toUpperCase());
	}
	
	public DBMode getDbMode() {
		return DBMode.valueOf(dbmode.toUpperCase());
	}
	
	public String getDbSchema() {
		return schema;
	}
}
