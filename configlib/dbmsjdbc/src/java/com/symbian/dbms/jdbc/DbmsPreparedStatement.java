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

// This code is loosely based on the public domain SQLite JDBC driver

import java.math.BigDecimal;
import java.sql.Array;
import java.sql.BatchUpdateException;
import java.sql.Blob;
import java.sql.Clob;
//JDK 1.6 only
//import java.sql.NClob;
import java.sql.ParameterMetaData;
import java.sql.PreparedStatement;
import java.sql.Ref;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
//JDK 1.6 only
//import java.sql.RowId;
import java.sql.SQLException;
//JDK 1.6 only
//import java.sql.SQLXML;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Map;

public class DbmsPreparedStatement extends DbmsStatement implements
		PreparedStatement {

	private String sql;
	private String args[];
	private boolean blobs[];
	private boolean strings[];
	private ArrayList<BatchArg> batch;
	boolean update;

	DbmsPreparedStatement(DbmsConnection connection, String sql) throws SQLException {
		super(connection);
		this.args = null;
		this.blobs = null;
		this.strings = null;
		this.batch = null;
		this.sql = preprocess(sql);
	}

	public boolean execute() throws SQLException {
		if (update) {
			updateCount = super.executeUpdate(replace(sql));
			resultSet = null;
		} else {
			updateCount = 0;
			resultSet = (DbmsResultSet)super.executeQuery(replace(sql));
		}
		return !update;
	}

	public void addBatch() throws SQLException {
		if (batch == null) {
			batch = new ArrayList<BatchArg>(args.length);
		}
		for (int i = 0; i < args.length; i++) {
			batch.add(new BatchArg(args[i], blobs[i], strings[i]));
		}
	}

	public int[] executeBatch() throws SQLException {
		if (batch == null) {
			return new int[0];
		}
		int[] ret = new int[batch.size() / args.length];
		for (int i = 0; i < ret.length; i++) {
			ret[i] = EXECUTE_FAILED;
		}
		int errs = 0;
		int index = 0;
		for (int i = 0; i < ret.length; i++) {
			for (int k = 0; k < args.length; k++) {
				BatchArg b = (BatchArg) batch.get(index++);

				args[k] = b.arg;
				blobs[k] = b.blob;
				strings[k] = b.string;
			}
			try {
				ret[i] = executeUpdate();
			} catch (SQLException e) {
				++errs;
			}
		}
		if (errs > 0) {
			throw new BatchUpdateException("batch failed", ret);
		}
		return ret;
	}

	public void clearBatch() throws SQLException {
		if (batch != null) {
			batch.clear();
			batch = null;
		}
	}

	public void close() throws SQLException {
		clearBatch();
		super.close();
	}

	public void clearParameters() throws SQLException {
		for (int i = 0; i < args.length; i++) {
			args[i] = null;
			blobs[i] = false;
			strings[i] = false;
		}
	}
	public ResultSet executeQuery() throws SQLException {
		execute();
		return resultSet;
	}

	public int executeUpdate() throws SQLException {
		execute();
		return updateCount;
	}

	private String preprocess(String sql) {
		sql = sql.trim();
		String sqllower = sql.toLowerCase();
		if (sqllower.startsWith("update") || sqllower.startsWith("insert")
				|| sqllower.startsWith("delete")) {
			update = true;
		}
		StringBuffer sb = new StringBuffer();
		boolean inq = false;
		int nparm = 0;
		for (int i = 0; i < sql.length(); i++) {
			char c = sql.charAt(i);
			if (c == '\'') {
				if (inq) {
					char nextChar = 0;
					if (i + 1 < sql.length()) {
						nextChar = sql.charAt(i + 1);
					}
					if (nextChar == '\'') {
						sb.append(c);
						sb.append(nextChar);
						i++;
					} else {
						inq = false;
						sb.append(c);
					}
				} else {
					inq = true;
					sb.append(c);
				}
			} else if (c == '?') {
				if (inq) {
					sb.append(c);
				} else {
					++nparm;
					sb.append("%Q");
				}
			} else if (c == ';') {
				if (!inq) {
					break;
				}
				sb.append(c);
			} else if (c == '%') {
				sb.append("%%");
			} else {
				sb.append(c);
			}
		}
		args = new String[nparm];
		blobs = new boolean[nparm];
		strings = new boolean[nparm];
		try {
			clearParameters();
		} catch (SQLException e) {
		}
		return sb.toString();
	}

	private String replace(String sql) {
		StringBuffer sb = new StringBuffer();
		int parm = -1;
		for (int i = 0; i < sql.length(); i++) {
			char c = sql.charAt(i);
			if (c == '%') {
				++i;
				c = sql.charAt(i);
				if (c == 'Q') {
					parm++;
					if (blobs[parm]) {
						sb.append(args[parm]);
					} else if ( strings[parm] ){
						if ( args[parm] != null ) {
							sb.append('\'');
							sb.append(args[parm]);
							sb.append('\'');
						} else {
							sb.append("NULL");
						}
					} else {
						sb.append(args[parm]);
					}
					++i;
					if ( i == sql.length() ) {
						break;
					}
					c = sql.charAt(i);
				} 
			}
			sb.append(c);
		}
		return sb.toString();
	}

	String translateFinal(String sql) {
		StringBuffer sb = new StringBuffer();
		int parm = -1;
		for (int i = 0; i < sql.length(); i++) {
			char c = sql.charAt(i);
			if (c == '%') {
				sb.append(c);
				++i;
				c = sql.charAt(i);
				if (c == 'Q') {
					parm++;
					if (blobs[parm]) {
						c = 's';
					}
				}
			}
			sb.append(c);
		}
		return sb.toString();
	}
	
	static final char[] xdigits = { '0', '1', '2', '3', '4', '5', '6', '7',
			'8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };

	public static String encodeX(byte[] a) {
		// check input
		if (a == null || a.length == 0) {
			return "X''";
		}
		int outLen = a.length + 3;
		StringBuffer out = new StringBuffer(outLen);
		out.append('X');
		out.append('\'');
		for (int i = 0; i < a.length; i++) {
			int tmp = 0xff & a[i];
			out.append(xdigits[tmp >> 4]);
			out.append(xdigits[tmp & 0x0F]);
		}
		out.append('\'');
		return out.toString();
	}


	public ResultSetMetaData getMetaData() throws SQLException {
		return resultSet.getMetaData();
	}

	public ParameterMetaData getParameterMetaData() throws SQLException {
		throw new SQLException("not supported");
	}

	public void registerOutputParameter(String parameterName, int sqlType)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void registerOutputParameter(String parameterName, int sqlType,
			int scale) throws SQLException {
		throw new SQLException("not supported");
	}

	public void registerOutputParameter(String parameterName, int sqlType,
			String typeName) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setNull(int parameterIndex, int sqlType) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = null;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setBoolean(int parameterIndex, boolean x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = x ? "1" : "0";
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setByte(int parameterIndex, byte x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setShort(int parameterIndex, short x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setInt(int parameterIndex, int x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setLong(int parameterIndex, long x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setFloat(int parameterIndex, float x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setDouble(int parameterIndex, double x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		args[parameterIndex - 1] = "" + x;
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setBigDecimal(int parameterIndex, BigDecimal x)
			throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = "" + x;
		}
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setString(int parameterIndex, String x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = x;
		}
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = true;
	}

	public void setBytes(int parameterIndex, byte x[]) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		blobs[parameterIndex - 1] = false;
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = encodeX(x);
			blobs[parameterIndex - 1] = true;
		}
		strings[parameterIndex - 1] = false;
	}

	public void setDate(int parameterIndex, java.sql.Date x)
			throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = DbmsDriver.symFormatDateTime(x.getTime());
		}
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setTime(int parameterIndex, java.sql.Time x)
			throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = DbmsDriver.symFormatDateTime(x.getTime());
		}
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setTimestamp(int parameterIndex, java.sql.Timestamp x)
			throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			args[parameterIndex - 1] = DbmsDriver.symFormatDateTime(x.getTime());
		}
		blobs[parameterIndex - 1] = false;
		strings[parameterIndex - 1] = false;
	}

	public void setAsciiStream(int parameterIndex, java.io.InputStream x,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	@Deprecated
	public void setUnicodeStream(int parameterIndex, java.io.InputStream x,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBinaryStream(int parameterIndex, java.io.InputStream x,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setObject(int parameterIndex, Object x, int targetSqlType,
			int scale) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		strings[parameterIndex - 1] = false;
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			if (x instanceof byte[]) {
				byte[] bx = (byte[]) x;
				args[parameterIndex - 1] = encodeX(bx);
				blobs[parameterIndex - 1] = true;
				return;
			} else {
				args[parameterIndex - 1] = x.toString();
			}
		}
		blobs[parameterIndex - 1] = false;
	}

	public void setObject(int parameterIndex, Object x, int targetSqlType)
			throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		strings[parameterIndex - 1] = false;
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			if (x instanceof byte[]) {
				byte[] bx = (byte[]) x;
				args[parameterIndex - 1] = encodeX(bx);
				blobs[parameterIndex - 1] = true;
				return;
			} else {
				args[parameterIndex - 1] = x.toString();
			}
		}
		blobs[parameterIndex - 1] = false;
	}

	public void setObject(int parameterIndex, Object x) throws SQLException {
		if (parameterIndex < 1 || parameterIndex > args.length) {
			throw new SQLException("bad parameter index");
		}
		strings[parameterIndex - 1] = false;
		if (x == null) {
			args[parameterIndex - 1] = null;
		} else {
			if (x instanceof byte[]) {
				byte[] bx = (byte[]) x;
				args[parameterIndex - 1] = encodeX(bx);
				blobs[parameterIndex - 1] = true;
				return;
			} else {
				args[parameterIndex - 1] = x.toString();
			}
		}
		blobs[parameterIndex - 1] = false;
	}

	public void setCharacterStream(int parameterIndex, java.io.Reader reader,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setRef(int i, Ref x) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBlob(int i, Blob x) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setClob(int i, Clob x) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setArray(int i, Array x) throws SQLException {
		throw new SQLException("not supported");
	}

//	JDK 1.6 only
//	public void setRowId(int parameterIndex, RowId x) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void setRowId(String parameterName, RowId x) throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public void setNString(int parameterIndex, String value)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNString(String parameterName, String value)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNCharacterStream(int parameterIndex, java.io.Reader x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNCharacterStream(String parameterName, java.io.Reader x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public void setNClob(int parameterIndex, NClob value) throws SQLException {
//		throw new SQLException("Not supported");
//	}

//	JDK 1.6 only
//	public void setNClob(String parameterName, NClob value) throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public void setClob(int parameterIndex, java.io.Reader x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setClob(String parameterName, java.io.Reader x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBlob(int parameterIndex, java.io.InputStream x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBlob(String parameterName, java.io.InputStream x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNClob(int parameterIndex, java.io.Reader x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNClob(String parameterName, java.io.Reader x, long len)
			throws SQLException {
		throw new SQLException("Not supported");
	}

//	JDK 1.6 only
//	public void setSQLXML(int parameterIndex, SQLXML xml) throws SQLException {
//		throw new SQLException("Not supported");
//	}
//
//	public void setSQLXML(String parameterName, SQLXML xml) throws SQLException {
//		throw new SQLException("Not supported");
//	}

	public void setAsciiStream(int parameterIndex, java.io.InputStream x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setAsciiStream(String parameterName, java.io.InputStream x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBinaryStream(int parameterIndex, java.io.InputStream x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBinaryStream(String parameterName, java.io.InputStream x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setCharacterStream(int parameterIndex, java.io.Reader x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setCharacterStream(String parameterName, java.io.Reader x,
			long len) throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setAsciiStream(int parameterIndex, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setAsciiStream(String parameterName, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBinaryStream(int parameterIndex, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBinaryStream(String parameterName, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setCharacterStream(int parameterIndex, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setCharacterStream(String parameterName, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNCharacterStream(int parameterIndex, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNCharacterStream(String parameterName, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setClob(int parameterIndex, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setClob(String parameterName, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBlob(int parameterIndex, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setBlob(String parameterName, java.io.InputStream x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNClob(int parameterIndex, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setNClob(String parameterName, java.io.Reader x)
			throws SQLException {
		throw new SQLException("Not supported");
	}

	public void setDate(int parameterIndex, java.sql.Date x, Calendar cal)
			throws SQLException {
		setDate(parameterIndex, x);
	}

	public void setTime(int parameterIndex, java.sql.Time x, Calendar cal)
			throws SQLException {
		setTime(parameterIndex, x);
	}

	public void setTimestamp(int parameterIndex, java.sql.Timestamp x,
			Calendar cal) throws SQLException {
		setTimestamp(parameterIndex, x);
	}

	public void setNull(int parameterIndex, int sqlType, String typeName)
			throws SQLException {
		setNull(parameterIndex, sqlType);
	}

	public java.net.URL getURL(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setURL(int parameterIndex, java.net.URL url)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setNull(String parameterName, int sqlType) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBoolean(String parameterName, boolean val)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setByte(String parameterName, byte val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setShort(String parameterName, short val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setInt(String parameterName, int val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setLong(String parameterName, long val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setFloat(String parameterName, float val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setDouble(String parameterName, double val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBigDecimal(String parameterName, BigDecimal val)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setString(String parameterName, String val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBytes(String parameterName, byte val[]) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setDate(String parameterName, java.sql.Date val)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setTime(String parameterName, java.sql.Time val)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setTimestamp(String parameterName, java.sql.Timestamp val)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setAsciiStream(String parameterName, java.io.InputStream s,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setBinaryStream(String parameterName, java.io.InputStream s,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setObject(String parameterName, Object val, int targetSqlType,
			int scale) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setObject(String parameterName, Object val, int targetSqlType)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setObject(String parameterName, Object val) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setCharacterStream(String parameterName, java.io.Reader r,
			int length) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setDate(String parameterName, java.sql.Date val, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setTime(String parameterName, java.sql.Time val, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public void setTimestamp(String parameterName, java.sql.Timestamp val,
			Calendar cal) throws SQLException {
		throw new SQLException("not supported");
	}

	public void setNull(String parameterName, int sqlType, String typeName)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public String getString(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public boolean getBoolean(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public byte getByte(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public short getShort(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public int getInt(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public long getLong(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public float getFloat(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public double getDouble(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public byte[] getBytes(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Date getDate(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Time getTime(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Timestamp getTimestamp(String parameterName)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public Object getObject(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Object getObject(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public BigDecimal getBigDecimal(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Object getObject(String parameterName, Map<?,?> map) throws SQLException {
		throw new SQLException("not supported");
	}

	public Object getObject(int parameterIndex, Map<?,?> map) throws SQLException {
		throw new SQLException("not supported");
	}

	public Ref getRef(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public Ref getRef(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Blob getBlob(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Blob getBlob(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public Clob getClob(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Clob getClob(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public Array getArray(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

	public Array getArray(int parameterIndex) throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Date getDate(String parameterName, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Date getDate(int parameterIndex, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Time getTime(String parameterName, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Time getTime(int parameterIndex, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Timestamp getTimestamp(String parameterName, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.sql.Timestamp getTimestamp(int parameterIndex, Calendar cal)
			throws SQLException {
		throw new SQLException("not supported");
	}

	public java.net.URL getURL(String parameterName) throws SQLException {
		throw new SQLException("not supported");
	}

}

class BatchArg {
	String arg;
	boolean blob;
	boolean string;

	BatchArg(String arg, boolean blob, boolean string) {
		if (arg == null) {
			this.arg = null;
		} else {
			this.arg = new String(arg);
		}
		this.blob = blob;
		this.string = string;
	}
}
