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

import java.io.File;
import java.sql.Connection;
import java.sql.DriverPropertyInfo;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Types;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.Properties;
import java.util.TimeZone;

public class DbmsDriver implements java.sql.Driver {

	/**
	 * Used to ensure date, time and timestamp data is stored and 
	 * retrieved uniformly. 
	 */
	public static TimeZone timeZone = TimeZone.getTimeZone("UTC");
	
	// driver registration
	static {
		
//		try{  
//            String libpath = System.getProperty("com.symbian.dbms.lib.path");
//            String libname = System.getProperty("com.symbian.dbms.lib.name");
//            if(libpath == null)
//            {
//                System.loadLibrary("dbmsjdbc");
//            } else
//            {
//                if(libname == null)
//                    libname = System.mapLibraryName("dbmsjdbc");
//                System.load((new File(libpath, libname)).getAbsolutePath());
//            }
//		} catch ( Exception e) {
//			e.printStackTrace();
//		}
			try{  
	        String libpath = System.getProperty("com.symbian.dbms.lib.path");
	        
	        // Build system builds dlls with preceding 'lib' on both windows and 
	        // linux. Linux loader expects library name without preceding 'lib'
	        // while Windows loader expects file name without extension.
	        // Using prefix for windows only resolves the problem.
	        
	        String libPrefix = "";
	        if ( System.getProperty("os.name").toLowerCase().indexOf("win") != -1) {
	        	libPrefix = "lib";
	        }
	        String symportLibName = libPrefix+"symport";
	        String driverLibName = libPrefix+"dbmsjdbc";
	        if (libpath == null) {
	            System.loadLibrary(symportLibName);
	            System.loadLibrary(driverLibName);
	        } else {
	            System.load(new File(libpath, System.mapLibraryName(symportLibName)).getAbsolutePath());
	            System.load(new File(libpath, System.mapLibraryName(driverLibName)).getAbsolutePath());
	        }
		} catch ( Exception e) {
			e.printStackTrace();
		}
		try {
			java.sql.DriverManager.registerDriver(new com.symbian.dbms.jdbc.DbmsDriver());
		} catch (SQLException e) {
			e.printStackTrace();
			System.exit(-1);
		}
	}
	
	private DbmsDriver(){}
	
	
	public boolean acceptsURL(String url) throws SQLException {
		return 	url.startsWith("dbms:/") ||
				url.startsWith("jdbc:dbms:/");
	}

	public Connection connect(String url, Properties info) throws SQLException {
		if (!acceptsURL(url)) {
		    return null;
		}
		
		String file = null;
		
		int queryStartIndex = url.indexOf('?');
		int fileStartIndex = url.indexOf('/') + 1;
		
		if ( queryStartIndex != -1 ) {
			String query = url.substring(queryStartIndex + 1);
			if ( query.length() > 0 ) {
				parseQuery(query, info);
			}
			file = url.substring(fileStartIndex, queryStartIndex);
		} else {
			file = url.substring(fileStartIndex);
		}
		
		DbmsConnection connection = DbmsConnectionManager.getConnection(file);
		if ( connection != null ) {
			throw new SQLException("This driver allows only one connection per database file.");
		}
		
		connection = DbmsConnectionManager.createConnection(file, info);
		return connection;
	}

	private void parseQuery(String query, Properties info) throws SQLException {
		String [] parts = query.split("&");
		for ( int i = 0; i < parts.length; i++ ) {
			String [] kv = parts[i].split("=");
			if ( kv.length != 2 ) {
				throw new SQLException("Could not parse parameter '"+parts[i]+"'");
			}
			info.put(kv[0], kv[1]);
		}
	}


	public int getMajorVersion() {
		return 0;
	}

	public int getMinorVersion() {
		return 0;
	}

	DriverPropertyInfo[] DRIVER_PROPS = {
		new DriverPropertyInfo("localeDll", null),
		new DriverPropertyInfo("volumeio.BlockSize", "4096"),
		new DriverPropertyInfo("volumeio.ClusterSize", "4096")
	};
	public DriverPropertyInfo[] getPropertyInfo(String url, Properties info)
			throws SQLException {
		return DRIVER_PROPS;
	}

	public boolean jdbcCompliant() {
		return false;
	}


	/**
	 * Return maximum integer value from a autoincrement column or -1 if there are no 
	 * records.
	 * 
	 * @param conn
	 * @param tableName
	 * @param colName
	 * @return
	 * @throws SQLException
	 */
	public static long getMax(Connection conn, String tableName, String colName) throws SQLException {
		if ( ! ( conn instanceof DbmsConnection ) ){
			throw new SQLException("getMax requires a DBMS database connection object");
		}
		int max = 0;
		DbmsConnection dcon = (DbmsConnection)conn;
		Statement stmt = null;
		try {
			stmt = dcon.createStatement();
			ResultSet rs = stmt.executeQuery("select " + colName + " from " + tableName +" order by " + colName +" DESC");
			boolean hasVal = rs.first();
			if ( hasVal ) {
				max = rs.getInt(1);
			} else {
				return -1;
			}
		} catch( SQLException ex) {
			throw ex;
		} finally {
			if ( stmt != null ) { stmt.close(); }
		}
		return max;
	}
	
	public static int translateDbmsColTypeToSqlType(int dbmsColType) {
		return dbmsToSqlTypeMap[dbmsColType];
	}

	static final int [] dbmsToSqlTypeMap = {
		Types.BIT , 		//	EDbColBit,
		Types.TINYINT , 	//	EDbColInt8,
		Types.TINYINT , 	//	EDbColUint8,
		Types.SMALLINT , 	//	EDbColInt16,
		Types.SMALLINT , 	//	EDbColUint16,
		Types.INTEGER , 	//	EDbColInt32,
		Types.INTEGER , 	//	EDbColUint32,
		Types.BIGINT , 		//	EDbColInt64,
		Types.FLOAT , 		//	EDbColReal32,
		Types.DOUBLE , 		//	EDbColReal64,
		Types.TIMESTAMP , 	//	EDbColDateTime,
		Types.CHAR , 		//	EDbColText8,
//		JDK 1.6 only
//		Types.NCHAR , 		//	EDbColText16,
		Types.CHAR , 		//	EDbColText16,
		Types.VARBINARY , 	//	EDbColBinary,
		Types.LONGVARCHAR ,	//	EDbColLongText8,
//		JDK 1.6 only
//		Types.LONGNVARCHAR ,//	EDbColLongText16,
		Types.LONGVARCHAR ,//	EDbColLongText16,
		Types.LONGVARBINARY //	EDbColLongBinary,
	};
	
	
	public static String symFormatDateTime(long time) {
		return symFormatDateTime(time, null);
	}
	public static String symFormatDateTime(long time, Calendar cal) {
		if ( cal == null ) {
			cal = new GregorianCalendar(timeZone );
		}
		cal.setTime(new java.util.Date(time));
		StringBuilder sb = new StringBuilder();
		sb.append('#');
		sb.append(cal.get(Calendar.DAY_OF_MONTH));
		sb.append('/');
		sb.append(cal.get(Calendar.MONTH) + 1);
		sb.append('/');
		sb.append(cal.get(Calendar.YEAR));
		sb.append(' ');
		sb.append(cal.get(Calendar.HOUR_OF_DAY));
		sb.append(':');
		sb.append(cal.get(Calendar.MINUTE));
		sb.append(':');
		sb.append(cal.get(Calendar.SECOND));
		sb.append('#');
		String ret = sb.toString();
		return ret;
	}
}
