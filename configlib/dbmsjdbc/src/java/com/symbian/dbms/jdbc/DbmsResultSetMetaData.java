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

class DbmsResultSetMetaData implements java.sql.ResultSetMetaData {

	DbmsResultSet resultSet;
	
	public DbmsResultSetMetaData(DbmsResultSet dbmsResultSet) {
		this.resultSet = dbmsResultSet;
	}

	public String getCatalogName(int column) throws SQLException {
		return "default";
	}

	public String getColumnClassName(int column) throws SQLException {
		return null;
	}

	public int getColumnCount() throws SQLException {
		return resultSet.getColumnCount();
	}

	public int getColumnDisplaySize(int column) throws SQLException {
		return 20;
	}

	public String getColumnLabel(int column) throws SQLException {
		return resultSet.findColumn(column);
	}

	public String getColumnName(int column) throws SQLException {
		return resultSet.findColumn(column);
	}

	public int getColumnType(int column) throws SQLException {
		return resultSet.getColumnType(column);
	}

	public String getColumnTypeName(int column) throws SQLException {
		// TODO implement this
//		int colType = resultSet.getColumnType(column);
//		return colTypeNames.get(colType);
		return null;
	}

	public int getPrecision(int column) throws SQLException {
		// TODO Auto-generated method stub
		return 0;
	}

	public int getScale(int column) throws SQLException {
		// TODO Auto-generated method stub
		return 0;
	}

	public String getSchemaName(int column) throws SQLException {
		return "default";
	}

	public String getTableName(int column) throws SQLException {
		return resultSet.getTableName();
	}

	public boolean isAutoIncrement(int column) throws SQLException {
		return resultSet.isAutoIncrement(column);
	}

	public boolean isCaseSensitive(int column) throws SQLException {
		return resultSet.isCaseSensitive();
	}

	public boolean isCurrency(int column) throws SQLException {
		throw new SQLException("Not supported");
	}

	public boolean isDefinitelyWritable(int column) throws SQLException {
		return false;
	}

	public int isNullable(int column) throws SQLException {
		return resultSet.isNullable(column);
	}

	public boolean isReadOnly(int column) throws SQLException {
		return true;
	}

	public boolean isSearchable(int column) throws SQLException {
		return true;
	}

	public boolean isSigned(int column) throws SQLException {
		return resultSet.isSigned(column);
	}

	public boolean isWritable(int column) throws SQLException {
		return false;
	}

	public boolean isWrapperFor(Class<?> iface) throws SQLException {
		return false;
	}

	public <T> T unwrap(Class<T> iface) throws SQLException {
		return null;
	}

}
