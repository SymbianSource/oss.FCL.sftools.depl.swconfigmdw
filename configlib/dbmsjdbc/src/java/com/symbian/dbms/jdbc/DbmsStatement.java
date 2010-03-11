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

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.symbian.store.StreamStore;


class DbmsStatement implements java.sql.Statement {

	protected int peerHandle;
	protected DbmsConnection connection;
	protected boolean closed = false;
	protected List<String> batch = new ArrayList<String>();
	protected int fetchSize = 1;
	protected int maxFieldSize = 1024 * 1024;
    protected DbmsResultSet resultSet;
    protected int updateCount;
	
	DbmsStatement(DbmsConnection connection) throws SQLException {
		if ( connection.isClosed() ) {
			throw new SQLException("Cannot create statement - Connection closed.");
		}
		this.connection = connection;
		this.peerHandle = _create(connection.peerHandle);
	}
	
	public void addBatch(String sql) throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		}
		batch.add(sql);
	}

	public void cancel() throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		}
		throw new SQLException("'cancel' not supported");
	}

	public void clearBatch() throws SQLException {
		batch.clear();
	}

	public void clearWarnings() throws SQLException {
		connection.clearWarnings();
	}

	public void close() throws SQLException {
		if ( closed ) {
			return;
		}
		closed = true;
		clearBatch();
		_close(peerHandle);
	}
	
	public boolean execute(String sql) throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		} else if ( connection.isClosed() ) {
			throw new SQLException("Connection closed.");
		}
		String trimmed = sql.trim().toLowerCase();
		if ( trimmed.startsWith("select") ) {
			executeQuery(sql);
			return true;
		} else if ( "begin".equals(trimmed) ) {
			int res = _begin(peerHandle);
			if ( res != 0 ) {
				String error = StreamStore.translateNativeError(res);
				throw new SQLException("Commit failed SOS: " + error);
			}
			return false;
		} else if ( "commit".equals(trimmed) ) {
			int res = _commit(peerHandle);
			if ( res != 0 ) {
				String error = StreamStore.translateNativeError(res);
				throw new SQLException("Commit failed SOS: " + error);
			}
			return false;
		} else if ( "rollback".equals(trimmed) ) {
			_rollback(peerHandle);
			return false;
		}
		executeUpdate(sql);
		return false;
	}

	public int[] executeBatch() throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		} else if ( connection.isClosed() ) {
			throw new SQLException("Connection closed.");
		}
		int [] res = new int[batch.size()];
		int i = 0;
		for ( String sql: batch ) {
			try {
				res[i++] = executeUpdate(sql);
			} catch (SQLException e) {
//				JDK 1.6 only
//				throw new BatchUpdateException(e);
				throw e;
			}			
		}
		return res;
	}

	public ResultSet executeQuery(String sql) throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		} else if ( connection.isClosed() ) {
			throw new SQLException("Connection closed.");
		}
		if ( sql.trim().endsWith(";") ) {
			sql = sql.trim().substring(0,sql.length()-1);
		}
		int resultHandle = _executeQuery(peerHandle, sql);
		if ( resultHandle < 0 ) {
			String error = StreamStore.translateNativeError(resultHandle);
			throw new SQLException("Error executing query SOS: " + error);
		}
		resultSet = new DbmsResultSet(connection, this, resultHandle);
		return resultSet;
	}

	public int executeUpdate(String sql) throws SQLException {
		if (closed ) {
			throw new SQLException("Statement closed.");
		} else if ( connection.isClosed() ) {
			throw new SQLException("Connection closed.");
		}
		if ( sql.trim().endsWith(";") ) {
			sql = sql.trim().substring(0,sql.length()-1);
		}
		int res = _executeUpdate(peerHandle, sql);
		if ( res < 0 ) {
			throw new SQLException("Error executing update SOS: " + 
					StreamStore.translateNativeError(res));
		}
		updateCount = res;
		return updateCount;
	}

	public Connection getConnection() throws SQLException {
		if (closed) {
			throw new SQLException("Statement closed.");
		} else if ( connection.isClosed() ) {
			throw new SQLException("Connection closed.");
		}
		return connection;
	}

	public int getFetchDirection() throws SQLException {
		// Maybe we can support both directions at some point?
		return ResultSet.FETCH_FORWARD;
	}

	public int getFetchSize() throws SQLException {
		return fetchSize;
	}

	public ResultSet getGeneratedKeys() throws SQLException {
		throw new SQLException("Not supported");
	}

	public int getMaxFieldSize() throws SQLException {
		return maxFieldSize;
	}

	public int getMaxRows() throws SQLException {
		// unlimited
		return 0;
	}

	public boolean getMoreResults() throws SQLException {
		if ( resultSet != null) {
			resultSet.close();
			resultSet = null;
		}
		return false;
	}

	public int getQueryTimeout() throws SQLException {
		// unlimited timeout
		return 0;
	}

	public ResultSet getResultSet() throws SQLException {
		return resultSet;
	}

	public int getResultSetConcurrency() throws SQLException {
		// Maybe implement ResultSet.CONCUR_UPDATABLE
		return ResultSet.CONCUR_READ_ONLY;
	}

	public int getResultSetHoldability() throws SQLException {
		return ResultSet.CLOSE_CURSORS_AT_COMMIT;
	}

	public int getResultSetType() throws SQLException {
		// TODO Investigate
		return ResultSet.TYPE_SCROLL_INSENSITIVE;
	}

	public int getUpdateCount() throws SQLException {
		return updateCount;
	}

	public SQLWarning getWarnings() throws SQLException {
		return connection.getWarnings();
	}

	public boolean isClosed() throws SQLException {
		return closed;
	}

	public boolean isPoolable() throws SQLException {
		return false;
	}

	public void setCursorName(String name) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setEscapeProcessing(boolean enable) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setFetchDirection(int direction) throws SQLException {
		// This could be supported
		throw new SQLException("not supported");
	}

	public void setFetchSize(int rows) throws SQLException {
		this.fetchSize = rows;
	}

	public void setMaxFieldSize(int max) throws SQLException {
		this.maxFieldSize = max;
	}

	public void setMaxRows(int max) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setPoolable(boolean poolable) throws SQLException {
		if ( poolable )
			throw new SQLException("Not supported");
	}

	public void setQueryTimeout(int seconds) throws SQLException {
		throw new SQLException("not supported");
	}

	public boolean isWrapperFor(Class<?> iface) throws SQLException {
		return false;
	}

	public <T> T unwrap(Class<T> iface) throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean execute(String sql, int autoGeneratedKeys) throws SQLException {
		if (autoGeneratedKeys != Statement.NO_GENERATED_KEYS) {
		    throw new SQLException("Not supported");
		}
		return execute(sql);
	}

	public boolean execute(String sql, int[] columnIndexes) throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean execute(String sql, String[] columnNames) throws SQLException {
		throw new SQLException("Not supported");
	}
	
	public int executeUpdate(String sql, int autoGeneratedKeys)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public int executeUpdate(String sql, int[] columnIndexes)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public int executeUpdate(String sql, String[] columnNames)
			throws SQLException {
		throw new SQLException("Not supported");
	}
	
	public boolean getMoreResults(int current) throws SQLException {
		throw new SQLException("Not supported");
	}

	// NATIVE METHODS
	private native int _create(int connectionHandle);
	private native int _executeUpdate(int peerHandle, String sql_ucs2);
	private native int _executeQuery(int peerHandle, String sql_ucs2);
	private native int _begin(int peerHandle);
	private native int _commit(int peerHandle);
	private native void _rollback(int peerHandle);
	private native void _close(int peerHandle);
	
}
