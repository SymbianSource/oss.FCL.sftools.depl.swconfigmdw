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

import java.sql.Array;
import java.sql.Blob;
import java.sql.CallableStatement;
import java.sql.Clob;
import java.sql.DatabaseMetaData;
//JDK 1.6 only
//import java.sql.NClob;
import java.sql.PreparedStatement;
//JDK 1.6 only
//import java.sql.SQLClientInfoException;
import java.sql.SQLException;
import java.sql.SQLWarning;
//JDK 1.6 only
//import java.sql.SQLXML;
import java.sql.Savepoint;
import java.sql.Statement;
import java.sql.Struct;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import com.symbian.store.StreamStore;

class DbmsConnection implements java.sql.Connection {

	private static final String SQL_COMMIT = "COMMIT";
	// MAX 5Mb inline blob
	public static final int MAX_BINARY_LITERAL_LENGTH = 10 * 1024 * 1024;
	int peerHandle;
	String file;
	Properties options;
	List<SQLException> warnings = new LinkedList<SQLException>();
	boolean inTransaction;
	boolean autoCommit;
	boolean closed = true;
	
	DbmsConnection(String file, Properties options) throws SQLException {
		this.file = file;
		this.options = options;
		// initialise JNI thread trap, panic handler etc
		_globalInit();
		// set global options
		for ( Object option: options.keySet() ) {
			String opt = (String)option;
			if ( "localeDll".equalsIgnoreCase(opt) ) {
				String dll = options.getProperty(opt);
				int res = _setLocaleDll(dll);
				if ( res != 0 ) {
					throw new SQLException("Error setting locale dll to " + dll + ". SOS error " + res);
				}
			} else if ("volumeio.BlockSize".equalsIgnoreCase(opt)) {
				int blockSize = 0;				
				try{
					blockSize = Integer.parseInt(options.getProperty(opt));
				} catch (NumberFormatException e) {
					throw new NumberFormatException("Invalid Block Size: " + e.getLocalizedMessage());
				}
				if ( blockSize <= 0 ) {
					throw new SQLException("Invalid value '" 
							+ options.getProperty(opt) 
							+ "' for volumeio.BlockSize driver parameter.");
				}
				_setBlockSize(blockSize);
			} else if ("volumeio.ClusterSize".equalsIgnoreCase(opt)) {
				int clusterSize = 0;				
				try{
					clusterSize = Integer.parseInt(options.getProperty(opt));
				} catch (NumberFormatException e) {
					throw new NumberFormatException("Invalid Cluster Size: " + e.getLocalizedMessage());
				}
				if ( clusterSize <= 0 ) {
					throw new SQLException("Invalid value '" 
							+ options.getProperty(opt) 
							+ "' for volumeio.ClusterSize driver parameter.");
				}
				_setClusterSize(clusterSize);
			} else if ("dbms.secureId".equalsIgnoreCase(opt)) {
				try{
					int sid = Integer.parseInt(options.getProperty(opt),16);
					_setSecureId(sid);
				} catch (NumberFormatException e) {
					throw new NumberFormatException("Invalid Secure ID: " + e.getLocalizedMessage());
				}			
			}
		}
		// create / open db
		peerHandle = _init(file);
		if ( peerHandle < 0 ) {
			String error = StreamStore.translateNativeError(peerHandle);
			throw new SQLException(error);
		} else {
			closed = false;
		}
	}

	public void clearWarnings() throws SQLException {
		warnings.clear();
	}

	public void close() throws SQLException {
		if ( closed ) {
			return;
		}
		DbmsConnectionManager.releaseConnection(file);
		dbmd = null;
		_close(peerHandle);
		peerHandle = 0;
		closed = true;
	}
	
	public void commit() throws SQLException {
		execSimpleSql(SQL_COMMIT);
	}

	public Array createArrayOf(String typeName, Object[] elements)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public Blob createBlob() throws SQLException {
		throw new SQLException("Not supported");
	}

	public Clob createClob() throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public NClob createNClob() throws SQLException {
//		throw new SQLException("Not supported");
//	}

//	JDK 1.6 only
//	public SQLXML createSQLXML() throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public Statement createStatement() throws SQLException {
		return new DbmsStatement(this);
	}

	public Statement createStatement(int resultSetType, int resultSetConcurrency)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public Statement createStatement(int resultSetType,
			int resultSetConcurrency, int resultSetHoldability)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public Struct createStruct(String typeName, Object[] attributes)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean getAutoCommit() throws SQLException {
		return inTransaction;
	}

	public String getCatalog() throws SQLException {
		return "default";
	}

	public Properties getClientInfo() throws SQLException {
		return new Properties();
	}

	public String getClientInfo(String name) throws SQLException {
		if ( "schema".equals(name.trim().toLowerCase())) {
			return _schema(peerHandle);
		}
		return null;
	}

	public int getHoldability() throws SQLException {
		return 0;
	}

	DatabaseMetaData dbmd = null;
	public DatabaseMetaData getMetaData() throws SQLException {
		if ( dbmd == null ) {
			dbmd = new DbmsDatabaseMetaData(this);
		}
		return dbmd;
	}

	public int getTransactionIsolation() throws SQLException {
		return java.sql.Connection.TRANSACTION_READ_COMMITTED;
	}

	public Map<String, Class<?>> getTypeMap() throws SQLException {
		throw new SQLException("Not supported");
	}

	public SQLWarning getWarnings() throws SQLException {
		return null;
	}

	public boolean isClosed() throws SQLException {
		return peerHandle == 0;
	}

	public boolean isReadOnly() throws SQLException {
		return false;
	}

	public boolean isValid(int timeout) throws SQLException {
		return peerHandle != 0;
	}

	public String nativeSQL(String sql) throws SQLException {
		throw new SQLException("Not supported");
	}

	public CallableStatement prepareCall(String sql) throws SQLException {
		throw new SQLException("Not supported");
	}

	public CallableStatement prepareCall(String sql, int resultSetType,
			int resultSetConcurrency) throws SQLException {
		throw new SQLException("Not supported");
	}

	public CallableStatement prepareCall(String sql, int resultSetType,
			int resultSetConcurrency, int resultSetHoldability)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public PreparedStatement prepareStatement(String sql) throws SQLException {
		return new DbmsPreparedStatement(this, sql);
	}

	public PreparedStatement prepareStatement(String sql, int autoGeneratedKeys)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public PreparedStatement prepareStatement(String sql, int[] columnIndexes)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public PreparedStatement prepareStatement(String sql, String[] columnNames)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public PreparedStatement prepareStatement(String sql, int resultSetType,
			int resultSetConcurrency) throws SQLException {
		throw new SQLException("Not supported");
	}

	public PreparedStatement prepareStatement(String sql, int resultSetType,
			int resultSetConcurrency, int resultSetHoldability)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void releaseSavepoint(Savepoint savepoint) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void rollback() throws SQLException {
		execSimpleSql("ROLLBACK");
	}

	public void rollback(Savepoint savepoint) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setAutoCommit(boolean autoCommit) throws SQLException {
		this.autoCommit = autoCommit; 
	}

	public void setCatalog(String catalog) throws SQLException {
		throw new SQLException("Not supported");
	}

// 	JDK 1.6 only
//	public void setClientInfo(Properties properties)
//			throws SQLClientInfoException {
//	}
//
//	public void setClientInfo(String name, String value)
//			throws SQLClientInfoException {
//	}

	public void setHoldability(int holdability) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setReadOnly(boolean readOnly) throws SQLException {
	}

	public Savepoint setSavepoint() throws SQLException {
		throw new SQLException("Not supported");
	}

	public Savepoint setSavepoint(String name) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setTransactionIsolation(int level) throws SQLException {
		if ( level != java.sql.Connection.TRANSACTION_READ_COMMITTED ){
			throw new SQLException("Not supported");
		}
	}

	public void setTypeMap(Map<String, Class<?>> map) throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean isWrapperFor(Class<?> iface) throws SQLException {
		return false;
	}

	public <T> T unwrap(Class<T> iface) throws SQLException {
		return null;
	}

	private void execSimpleSql(String sql) throws SQLException {
		DbmsStatement stmt = new DbmsStatement(this);
		try{
			stmt.execute(sql);
		} finally {
			stmt.close();
		}		
	}

	
	// NATIVE
	private native void _globalInit();
	private native int _init(String file);
	private native String _schema(int peerHandle);
	private native void _close(int peerHandle);
	// options are global so may not need a peer
	private native void _setSecureId(int parseInt);
	private native int _setLocaleDll(String dll);
	private native void _setBlockSize(int size);
	private native void _setClusterSize(int size);
}
