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

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

import org.apache.log4j.Logger;

/**
 * Executes the sql statements against database connection
 */
public class SqlExecuter {

	/** Static logger */
	private static final Logger logger = Logger.getLogger(SqlExecuter.class);

	/**
	 * Executes SQL statements from the input reader stream Reader stream can be
	 * created based on the String or File class
	 * 
	 * @param input
	 *            the stream containing sql statements separated by ";"
	 * @throws SQLException
	 */
	public boolean executeSql(Reader input, Connection connection, boolean failFast) throws SQLException {
		boolean result = true;
		try {
			BufferedReader reader = new BufferedReader(input);
			String line = null;
			String sql = "", temp = "";
			while ((line = reader.readLine()) != null || sql.length() > 0) {

                if (line != null) {
                    sql += line.trim();
                } else if (!sql.endsWith(";")) {
                    sql += ";";
                }
                if (sql.contains(";") && sql.trim().length() > 1) {
                    int index = sql.indexOf(";");
                    if (index != sql.length() - 1) {
                        temp = sql.substring(index + 1);
                        sql = sql.substring(0, index + 1);
                    }
                    result &= execute(sql, connection, failFast);
                    sql = temp;
                    temp = "";
                }
            }
		} catch (IOException e) {
			logger.error(e);
		}
		return result;
	}

    private boolean execute(String sql, Connection connection, boolean failFast)
    throws SQLException {
    	boolean result = true;
    	Statement statement = connection.createStatement();
        try {
        	statement.execute(sql.replace(";", ""));
        } catch (SQLException exception) {
        	result = false;
            logger.error(exception);
            if (failFast) {
            	throw exception;
            }
        }
        finally	{
        	if (null != statement)	{
        		statement.close();
        	}
        }
        return result;
    }

    public boolean applySqlFileToDb(File sqlFileToExecute, Connection connection, boolean failFast) 
    throws SQLException, IOException {
    	  logger.info("Applying " + sqlFileToExecute.getName());
          return executeSql(new FileReader(sqlFileToExecute), connection, failFast);
    }
	
	public boolean applySqlFilesToDb(List<File> SqlFiles, Connection connection, boolean failFast) 
	throws SQLException, IOException {
		boolean result = true;
		for(File lFileToExecute: SqlFiles) {
        	logger.info("Applying " + lFileToExecute.getName());
			result &= executeSql(new FileReader(lFileToExecute), connection, failFast);
		}
		return result;
	}
	
	public boolean executeSql(List<String> statementsList, Connection connection, boolean failFast) 
	throws SQLException {
	    boolean result = true;
	    for (String sql : statementsList) {
	    	logger.debug("Applying SQL statement: " + sql);
	    	result &= execute(sql, connection, failFast);
	    }
	    return result;
	}
}
