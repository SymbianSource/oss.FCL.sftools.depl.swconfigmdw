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

package com.symbian.sdb.configuration.options;

import java.text.MessageFormat;
import java.util.EnumSet;

import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;

public enum DbOptions {
    //SQLite options
    PAGE_SIZE("PRAGMA page_size = {0}" , "1024", EnumSet.of(DBType.SQLITE), true),
    ENCODING("PRAGMA encoding = \"{0}\"", "UTF-16", EnumSet.of(DBType.SQLITE), true),
    
    //DMBS options
    BLOCK_SIZE("volumeio.BlockSize={0}" , "4096", EnumSet.of(DBType.DBMS), false),
    CLUSTER_SIZE("volumeio.ClusterSize={0}", "4096", EnumSet.of(DBType.DBMS), false),
    LOCALE("localeDll=\"{0}\"", null, EnumSet.of(DBType.DBMS), false),
    SECURE_ID("dbms.secureId={0}", null, EnumSet.of(DBType.DBMS), false);
    
    String pragmast;
    String value;
    boolean isPragma;
    
    EnumSet<DBType> dbSet;
    
    private DbOptions(String keyValue, String defaultValue, EnumSet<DBType> set, boolean isPragma) {
        pragmast = keyValue;
        value = defaultValue;
        dbSet = set;
        this.isPragma = isPragma;
    }

    public void setValue(String val) throws SDBValidationException {
        try {
            switch(this) {
                case PAGE_SIZE:    Pagesize.valueOf("P" + val); break;
                case ENCODING:  val = Encoding.valueOf(val).getValue(); break;
            }
        } catch(IllegalArgumentException ex) {
            throw new SDBValidationException(ex.getMessage());
        }
        value = val;
    }
    
    public boolean isApplicableFor(DBType db) {
        return dbSet.contains(db);
    }
    
    public String getValue() {
        if (value != null) {
            return MessageFormat.format(pragmast, new Object[] {value});
        } else {
            return null;
        }
    }
    
    public boolean isPragma() {
        return isPragma;
    }
}
