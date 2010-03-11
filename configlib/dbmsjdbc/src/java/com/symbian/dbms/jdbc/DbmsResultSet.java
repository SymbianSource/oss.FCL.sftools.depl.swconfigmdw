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

import java.io.InputStream;
import java.io.Reader;
import java.math.BigDecimal;
import java.net.URL;
import java.sql.Array;
import java.sql.Blob;
import java.sql.Clob;
import java.sql.Date;
//JDK 1.6 only
//import java.sql.NClob;
import java.sql.Ref;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
//JDK 1.6 only
//import java.sql.RowId;
import java.sql.SQLException;
import java.sql.SQLWarning;
//JDK 1.6 only
//import java.sql.SQLXML;
import java.sql.Statement;
import java.sql.Time;
import java.sql.Timestamp;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.Map;

import com.symbian.store.StreamStore;

class DbmsResultSet implements java.sql.ResultSet {

	int peerHandle;
	DbmsConnection connection;
	DbmsStatement statement;
	int rowcount = 0;
	int colcount = 0;
	HashMap<String, Integer> columnsByName = null;
	String [] columnsByOrder = null;
	DbmsResultSetMetaData rsmd = null;
//	DbmsRowData rowData = null;
	int [] colTypes;
	boolean closed;
	
	public DbmsResultSet(DbmsConnection connection, DbmsStatement statement, int peerHandle) throws SQLException {
		this.peerHandle = peerHandle;
		this.connection = connection;
		this.statement = statement;
		rowcount = _rowcount(peerHandle);
		colcount = _colcount(peerHandle);
		if ( rowcount < 0 || colcount < 0 ) {
			throw new SQLException("SOS error retrieving colcount=" + colcount + ", rowcount " + rowcount);
		}
		colTypes = new int[colcount];
		int res = _columnTypes(peerHandle, colTypes);
		if ( res < 0 ) {
			String error = StreamStore.translateNativeError(res);
			throw new SQLException("SOS error retrieving coltypes " + error);
		}
		columnsByOrder = new String[colcount];
		res = _columnNames(peerHandle, columnsByOrder);
		if ( res < 0 ) {
			String error = StreamStore.translateNativeError(res);
			throw new SQLException("SOS error retrieving colnames " + error);
		}
		columnsByName = new HashMap<String, Integer>();
		for ( int i = 0 ; i < colcount ; i++ ) {
			// populate quick col name lookup table
			columnsByName.put(columnsByOrder[i], i+1);
			// translate type from DBMS to jdbc
			colTypes[i] = DbmsDriver.translateDbmsColTypeToSqlType(colTypes[i]);
		}
		rsmd = new DbmsResultSetMetaData(this);
//		rowData = new DbmsRowData(this);
	}
	
	public boolean absolute(int row) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		//		rowData.reset();
		// this is far from optimal, but works
		if ( row < 0 ) {
			if ( !_last(peerHandle)) {
				throw new SQLException("Error absolute moving to row " + row);
			}
			if ( !_prev(peerHandle, -row-1)) {
				throw new SQLException("Error absolute moving to row " + row);
			}
		} else {
			if ( !_first(peerHandle)) {
				throw new SQLException("Error absolute moving to row " + row);
			}
			if ( !_next(peerHandle, row-1 ) ){
				throw new SQLException("Error absolute moving to row " + row);
			}
		}
		return row == 0 || rowcount == 0;
	}

	public void afterLast() throws SQLException {
//		rowData.reset();
		throw new SQLException("Not supported");
//		if ( ! _afterLast(peerHandle) ) {
//			throw new SQLException();
//		}
	}

	public void beforeFirst() throws SQLException {
//		rowData.reset();
		throw new SQLException("Not supported");
//		if ( ! _beforeFirst(peerHandle) ) {
//			throw new SQLException();
//		}
	}

	public void cancelRowUpdates() throws SQLException {
		throw new SQLException("Not supported");
	}

	public void clearWarnings() throws SQLException {
	}

	public void close() throws SQLException {
//		rowData = null;
		if ( !closed ) {
			closed = true;
			_close(peerHandle);
			peerHandle = 0;
		}
	}


	public void deleteRow() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
//		rowData = null;
		if ( ! _delete(peerHandle) ) {
			throw new SQLException("Error deleting current row.");
		}
	}


	public int findColumn(String columnLabel) throws SQLException {
		Integer i = columnsByName.get(columnLabel);
		if ( i == null ) {
			throw new SQLException("Column " + columnLabel + " not found");
		}
		return i;
	}

	public boolean first() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
//		rowData.reset();
		return _first(peerHandle);
	}

	public Array getArray(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Array getArray(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getAsciiStream(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getAsciiStream(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public BigDecimal getBigDecimal(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public BigDecimal getBigDecimal(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public BigDecimal getBigDecimal(int columnIndex, int scale)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public BigDecimal getBigDecimal(String columnLabel, int scale)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getBinaryStream(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getBinaryStream(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Blob getBlob(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Blob getBlob(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean getBoolean(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getBoolean(peerHandle, columnIndex);
	}


	public boolean getBoolean(String columnLabel) throws SQLException {
		return getBoolean(findColumn(columnLabel));
	}

	public byte getByte(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getByte(peerHandle, columnIndex);
	}

	public byte getByte(String columnLabel) throws SQLException {
		return getByte(findColumn(columnLabel));
	}

	public byte[] getBytes(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getBytes(peerHandle, columnIndex);
	}

	public byte[] getBytes(String columnLabel) throws SQLException {
		return getBytes(findColumn(columnLabel));
	}

	public Reader getCharacterStream(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Reader getCharacterStream(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Clob getClob(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Clob getClob(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public int getConcurrency() throws SQLException {
		return ResultSet.CONCUR_READ_ONLY;
	}

	public String getCursorName() throws SQLException {
		return "default";
	}

	public Date getDate(int columnIndex) throws SQLException {
		return getDate(columnIndex, null);
	}

	public Date getDate(String columnLabel) throws SQLException {
		return getDate(findColumn(columnLabel), null);
	}

	public Date getDate(int columnIndex, Calendar cal) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		if (cal == null) {
			cal = new GregorianCalendar();
		}
		long dbLongVal = _getTime(peerHandle, columnIndex);
		cal.setTimeInMillis(dbLongVal);
		return new java.sql.Date(cal.getTimeInMillis());
	}

	public Date getDate(String columnLabel, Calendar cal) throws SQLException {
		return getDate(findColumn(columnLabel), cal);
	}

	public double getDouble(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getDouble(peerHandle, columnIndex);
	}

	public double getDouble(String columnLabel) throws SQLException {
		return getDouble(findColumn(columnLabel));
	}

	public int getFetchDirection() throws SQLException {
		return ResultSet.FETCH_FORWARD;
	}

	public int getFetchSize() throws SQLException {
		return 1;
	}

	public float getFloat(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getFloat(peerHandle, columnIndex);
	}

	public float getFloat(String columnLabel) throws SQLException {
		return getFloat(findColumn(columnLabel));
	}

	public int getHoldability() throws SQLException {
		return ResultSet.CLOSE_CURSORS_AT_COMMIT;
	}

	public int getInt(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getInteger(peerHandle, columnIndex);
	}

	public int getInt(String columnLabel) throws SQLException {
		return getInt(findColumn(columnLabel));
	}

	public long getLong(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getLong(peerHandle, columnIndex);
	}

	public long getLong(String columnLabel) throws SQLException {
		return getLong(findColumn(columnLabel));
	}

	public ResultSetMetaData getMetaData() throws SQLException {
		return rsmd;
	}

	public Reader getNCharacterStream(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Reader getNCharacterStream(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

//  JDK 1.6 only
//	public NClob getNClob(int columnIndex) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public NClob getNClob(String columnLabel) throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public String getNString(int columnIndex) throws SQLException {
		return getString(columnIndex);
	}

	public String getNString(String columnLabel) throws SQLException {
		return getString(columnLabel);
	}

	public Object getObject(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Object getObject(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Object getObject(int columnIndex, Map<String, Class<?>> map)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public Object getObject(String columnLabel, Map<String, Class<?>> map)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public Ref getRef(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public Ref getRef(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public int getRow() throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public RowId getRowId(int columnIndex) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public RowId getRowId(String columnLabel) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public SQLXML getSQLXML(int columnIndex) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public SQLXML getSQLXML(String columnLabel) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
	public short getShort(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getShort(peerHandle, columnIndex);
	}

	public short getShort(String columnLabel) throws SQLException {
		return getShort(findColumn(columnLabel));
	}

	public Statement getStatement() throws SQLException {
		return statement;
	}

	public String getString(int columnIndex) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		return _getText(peerHandle, columnIndex);
	}

	public String getString(String columnLabel) throws SQLException {
		return getString(findColumn(columnLabel));
	}

	public Time getTime(int columnIndex) throws SQLException {
		return getTime(columnIndex, null);
	}

	public Time getTime(String columnLabel) throws SQLException {
		return getTime(findColumn(columnLabel), null);
	}

	public Time getTime(int columnIndex, Calendar cal) throws SQLException {
		if (cal == null) {
			cal = new GregorianCalendar();
		}
		long dbLongVal = _getTime(peerHandle, columnIndex);
		cal.setTimeInMillis(dbLongVal);
		return new java.sql.Time(cal.getTimeInMillis());
	}

	public Time getTime(String columnLabel, Calendar cal) throws SQLException {
		return getTime(findColumn(columnLabel), cal);
	}

	public Timestamp getTimestamp(int columnIndex) throws SQLException {
		return getTimestamp(columnIndex, null);
	}

	public Timestamp getTimestamp(String columnLabel) throws SQLException {
		return getTimestamp(findColumn(columnLabel), null);
	}

	public Timestamp getTimestamp(int columnIndex, Calendar cal)
			throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		if (cal == null) {
			cal = new GregorianCalendar();
		}
		long dbLongVal = _getTime(peerHandle, columnIndex);
		cal.setTimeInMillis(dbLongVal);
		return new java.sql.Timestamp(cal.getTimeInMillis());
	}

	public Timestamp getTimestamp(String columnLabel, Calendar cal)
			throws SQLException {
		return getTimestamp(findColumn(columnLabel), cal);
	}

	public int getType() throws SQLException {
		return ResultSet.TYPE_FORWARD_ONLY;
	}

	public URL getURL(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public URL getURL(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getUnicodeStream(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public InputStream getUnicodeStream(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public SQLWarning getWarnings() throws SQLException {
		return null;
	}

	public void insertRow() throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean isAfterLast() throws SQLException {
		// TODO Auto-generated method stub
		return false;
	}

	public boolean isBeforeFirst() throws SQLException {
		// No possible with DBMS
		return false;
	}

	public boolean isClosed() throws SQLException {
		return closed;
	}

	public boolean isFirst() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		int f = _isFirst(peerHandle);
		if ( f < 0 ) {
			String error = StreamStore.translateNativeError(f);
			throw new SQLException("isFirst SOS error " + error);
		} else if ( f == 0 ) {
			return false;
		} else {
			return true;
		}
	}

	public boolean isLast() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		int f = _isLast(peerHandle);
		if ( f < 0 ) {
			String error = StreamStore.translateNativeError(f);
			throw new SQLException("isLast SOS error " + error);
		} else if ( f == 0 ) {
			return false;
		} else {
			return true;
		}
	}

	public boolean last() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
//		rowData.reset();
		return _last(peerHandle);
	}

	public void moveToCurrentRow() throws SQLException {
//		rowData.reset();
		throw new SQLException("Not supported");
	}

	public void moveToInsertRow() throws SQLException {
//		rowData.reset();
		throw new SQLException("Not supported");
	}

	public boolean next() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
//		rowData.reset();
		return _next(peerHandle, 1);
	}

	public boolean previous() throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
//		rowData.reset();
		return _prev(peerHandle, 1);
	}

	public void refreshRow() throws SQLException {
//		rowData.reset();
	}

	public boolean relative(int rows) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		if ( rows > 0 ) {
			return _next(peerHandle, rows);
		} else if ( rows < 0 ) {
			return _prev(peerHandle, -rows);
		}
		return false;
	}

	public boolean rowDeleted() throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean rowInserted() throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean rowUpdated() throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setFetchDirection(int direction) throws SQLException {
		if ( direction != ResultSet.FETCH_FORWARD ) {
			throw new SQLException("Attempt to set fetch direction to unsupported value.");
		}
	}

	public void setFetchSize(int rows) throws SQLException {
	}

	public void updateArray(int columnIndex, Array x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateArray(String columnLabel, Array x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(int columnIndex, InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(String columnLabel, InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(int columnIndex, InputStream x, int length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(String columnLabel, InputStream x, int length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(int columnIndex, InputStream x, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateAsciiStream(String columnLabel, InputStream x, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBigDecimal(int columnIndex, BigDecimal x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBigDecimal(String columnLabel, BigDecimal x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(int columnIndex, InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(String columnLabel, InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(int columnIndex, InputStream x, int length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(String columnLabel, InputStream x, int length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(int columnIndex, InputStream x, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBinaryStream(String columnLabel, InputStream x,
			long length) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(int columnIndex, Blob x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(String columnLabel, Blob x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(int columnIndex, InputStream inputStream)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(String columnLabel, InputStream inputStream)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(int columnIndex, InputStream inputStream, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBlob(String columnLabel, InputStream inputStream,
			long length) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBoolean(int columnIndex, boolean x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBoolean(String columnLabel, boolean x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateByte(int columnIndex, byte x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateByte(String columnLabel, byte x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBytes(int columnIndex, byte[] x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateBytes(String columnLabel, byte[] x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(int columnIndex, Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(String columnLabel, Reader reader)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(int columnIndex, Reader x, int length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(String columnLabel, Reader reader,
			int length) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(int columnIndex, Reader x, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateCharacterStream(String columnLabel, Reader reader,
			long length) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(int columnIndex, Clob x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(String columnLabel, Clob x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(int columnIndex, Reader reader) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(String columnLabel, Reader reader)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(int columnIndex, Reader reader, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateClob(String columnLabel, Reader reader, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateDate(int columnIndex, Date x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateDate(String columnLabel, Date x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateDouble(int columnIndex, double x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateDouble(String columnLabel, double x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateFloat(int columnIndex, float x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateFloat(String columnLabel, float x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateInt(int columnIndex, int x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateInt(String columnLabel, int x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateLong(int columnIndex, long x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateLong(String columnLabel, long x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNCharacterStream(int columnIndex, Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNCharacterStream(String columnLabel, Reader reader)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNCharacterStream(int columnIndex, Reader x, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNCharacterStream(String columnLabel, Reader reader,
			long length) throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public void updateNClob(int columnIndex, NClob clob) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void updateNClob(String columnLabel, NClob clob) throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public void updateNClob(int columnIndex, Reader reader) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNClob(String columnLabel, Reader reader)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNClob(int columnIndex, Reader reader, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNClob(String columnLabel, Reader reader, long length)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNString(int columnIndex, String string)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNString(String columnLabel, String string)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNull(int columnIndex) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateNull(String columnLabel) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateObject(int columnIndex, Object x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateObject(String columnLabel, Object x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateObject(int columnIndex, Object x, int scaleOrLength)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateObject(String columnLabel, Object x, int scaleOrLength)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateRef(int columnIndex, Ref x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateRef(String columnLabel, Ref x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateRow() throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public void updateRowId(int columnIndex, RowId x) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void updateRowId(String columnLabel, RowId x) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void updateSQLXML(int columnIndex, SQLXML xmlObject)
//			throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void updateSQLXML(String columnLabel, SQLXML xmlObject)
//			throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public void updateShort(int columnIndex, short x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateShort(String columnLabel, short x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateString(int columnIndex, String x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateString(String columnLabel, String x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateTime(int columnIndex, Time x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateTime(String columnLabel, Time x) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateTimestamp(int columnIndex, Timestamp x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void updateTimestamp(String columnLabel, Timestamp x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean wasNull() throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean isWrapperFor(Class<?> iface) throws SQLException {
		throw new SQLException("Not supported");
	}

	public <T> T unwrap(Class<T> iface) throws SQLException {
		throw new SQLException("Not supported");
	}

	public int getColumnCount()throws SQLException  {
		return colcount;
	}

	public String findColumn(int column)throws SQLException  {
		return columnsByOrder[column-1];
	}

	public int getColumnType(int column) throws SQLException {
		return colTypes[column-1];
	}

	public String getTableName() throws SQLException {
		// TODO implement this?
		return null;
	}

	public boolean isAutoIncrement(int column) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		int res = _isAutoIncrement(peerHandle, column);
		if ( res < 0 ) {
			String error = StreamStore.translateNativeError(res);
			throw new SQLException("Error testing isAutoIncrement SOS: " + error);
		} else if ( res >  0 ) {
			return true;
		} else {
			return false;
		}
	}

	public boolean isCaseSensitive() throws SQLException {
		// TODO review this
		return false;
	}

	public int isNullable(int column) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		int res = _isNullable(peerHandle, column);
		if ( res < 0 ) {
			String error = StreamStore.translateNativeError(res);
			throw new SQLException("Error testing isNullable SOS: " + error);
		} else if ( res == 0 ) {
			return ResultSetMetaData.columnNullable;
		} else {
			return ResultSetMetaData.columnNoNulls;
		}
	}
	
	public boolean isSigned(int column) throws SQLException {
		if (closed || connection.isClosed() || peerHandle <= 0 ) {
			throw new SQLException("Closed");
		}
		int res = _isSigned(peerHandle, column);
		if ( res < 0 ) {
			String error = StreamStore.translateNativeError(res);
			throw new SQLException("Error testing isSigned SOS: " + error);
		} else if ( res >  0 ) {
			return true;
		} else {
			return false;
		}
	}

//	private void ensureRowData() throws SQLException {
//		if ( !rowData.isValid() ) {
//			fetchRowData();
//		}
//	}
//	
//	private void fetchRowData() throws SQLException {
//		int error = _fetchRowData(peerHandle, rowData); 
//		if( error < 0 ) {
//			throw new SQLException("Error fetching row data SOS: " + error);
//		}
//		rowData.setValid();
//	}
	
	private native int _rowcount(int peerHandle);
	private native int _colcount(int peerHandle);
//	private native int _fetchRowData(int peerHandle, DbmsRowData rowData);
	private native boolean _next(int peerHandle, int count);
	private native boolean _first(int peerHandle);
	private native boolean _last(int peerHandle);
	private native boolean _prev(int peerHandle, int count);
	private native void _close(int peerHandle);
	private native boolean _delete(int peerHandle);
	private native int _isSigned(int peerHandle, int column);
	private native int _columnTypes(int peerHandle, int[] colTypes2);
	private native int _isFirst(int peerHandle);
	private native int _isLast(int peerHandle);
	private native int _columnNames(int peerHandle, String[] columnsByOrder);
	private native int _isAutoIncrement(int peerHandle, int column);
	private native int _isNullable(int peerHandle, int column);

	private native boolean _getBoolean(int peerHandle, int columnIndex);
	private native byte _getByte(int peerHandle, int columnIndex);
	private native short _getShort(int peerHandle, int columnIndex);
	private native int _getInteger(int peerHandle, int columnIndex);
	private native long _getLong(int peerHandle, int columnIndex);
	private native float _getFloat(int peerHandle, int columnIndex);
	private native long _getTime(int peerHandle, int columnIndex);
	private native String _getText(int peerHandle, int columnIndex);
	private native byte[] _getBytes(int peerHandle, int columnIndex);
	private native double _getDouble(int peerHandle, int columnIndex);

}
