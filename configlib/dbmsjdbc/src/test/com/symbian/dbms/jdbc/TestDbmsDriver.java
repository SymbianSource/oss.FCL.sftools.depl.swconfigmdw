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
import java.io.FileOutputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.sql.Types;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.TimeZone;

import junit.framework.TestCase;

public class TestDbmsDriver extends TestCase {

	protected void setUp() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
		if ( f.exists() ) {
			throw new Exception("file locked");
		}
	}

	protected void tearDown() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
		if ( f.exists() ) {
			throw new Exception("file locked");
		}
	}
	
	public void testPreparedSelect() throws Exception {
		
	}
	
	public void testOpenClose() throws Exception {
		FileOutputStream fos = null;
		try { 
			fos = new FileOutputStream("test.db");
			fos.write("corrupt data...".getBytes());
		} finally {
			fos.close();
		}
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		Connection conn = null;
		try{
			conn = DriverManager.getConnection(url);
			fail("Opening corrupt file.");
		} catch(Exception e) {
			// pass
		} finally {
			if ( conn != null ) {
				try{conn.close();}catch(Exception e) {}
			}
		}

		// delete the file
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
		if ( f.exists()){
			fail("file locked");
		}

		// this should now succeeed
		try{
			conn = DriverManager.getConnection(url);
		} catch(Exception e) {
			fail("Could not create db file...");
		} finally {
			if ( conn != null ) {
				try{conn.close();}catch(Exception e) {}
			}
		}
		
		// should ignore double close
		try{conn.close();}catch(Exception e) {fail("not ignoring double close");}
		// fine
	}
	
	public void testDriverConnect() throws Exception {
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test-cdb.db?volumeio.BlockSize=8192&dbms.secureId=100065FF";
		Connection conn = null;
		try{
			conn = DriverManager.getConnection(url);
		} finally {
			if( conn != null ) {conn.close();}
		}
	}
	
	public void testClosedConnection() throws Exception{
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		// Database URL with an example of setting params
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		Connection conn = null;
		Statement stmt = null;
		Statement stmt2 = null;
		try {
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			conn.close();
			conn = null;
			stmt.execute("create table test_close_0");
			fail("No exception generated");
		} catch(Exception ew) {
			// expected exception, pass
			assertEquals("Connection closed.", ew.getMessage());
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null;} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null;} catch (SQLException e) {e.printStackTrace();}
			}
		}
		try {
			conn = DriverManager.getConnection(url);
			conn.close();
			stmt = conn.prepareStatement("select * from test_close_0");
			fail("No exception generated");
		} catch(Exception ew) {
			assertEquals("Cannot create statement - Connection closed.", ew.getMessage());
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null; } catch (SQLException e) {e.printStackTrace();}
			}
		}

		// test double close
		try {
			conn = DriverManager.getConnection(url);
			conn.close();
			conn.close();
			conn = null;
		} catch(Exception e){
			fail("Unexpected exception" + e);
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( stmt2 != null ) {
				try {stmt2.close(); stmt2 = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null; } catch (SQLException e) {e.printStackTrace();}
			}
		}
		
		// test double close, prepared statement
		try {
			conn = DriverManager.getConnection(url);
			stmt = conn.prepareStatement("select * from test");
			conn.close();
			stmt.close();
			stmt.close();
		} catch(Exception e){
			fail("Unexpected exception" + e);
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( stmt2 != null ) {
				try {stmt2.close(); stmt2 = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null; } catch (SQLException e) {e.printStackTrace();}
			}
		}
		System.out.println("0");
		
		try {
			conn = DriverManager.getConnection(url);
			stmt2 = conn.createStatement();
			stmt2.execute("create table test_close_1 (t1 integer)");
			conn.close();
			stmt = conn.prepareStatement("insert into test_close_1 values (1)");
			fail("No exception generated");
		} catch(Exception ew) {
			assertEquals("Cannot create statement - Connection closed.", ew.getMessage());
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( stmt2 != null ) {
				try {stmt2.close(); stmt2 = null; } catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null; } catch (SQLException e) {e.printStackTrace();}
			}
		}

		try {
			conn = DriverManager.getConnection(url);
			stmt2 = conn.createStatement();
			stmt2.execute("create table test_close_2 (t1 integer)");
			stmt2.close();
			stmt2 = null;
			stmt2 = conn.prepareStatement("insert into test_close_2 values(?)");
			PreparedStatement pstmt = (PreparedStatement)stmt2;
			pstmt.setInt(1, 1);
			pstmt.execute();
			pstmt.setInt(1, 2);
			pstmt.execute();
			pstmt.setInt(1, 3);
			pstmt.execute();
			
			stmt = conn.prepareStatement("select * from test_close_2 where t1=?");
			pstmt = (PreparedStatement)stmt;
			pstmt.setInt(1, 1);
			ResultSet rs = pstmt.executeQuery();
			conn.close();
			conn = null;
			boolean hasNext = rs.first();
			while ( hasNext ) {
				hasNext = rs.next();
			}
			fail("No exception generated");
		} catch(Exception ew) {
			assertEquals("Closed", ew.getMessage());
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( stmt2 != null ) {
				try {stmt2.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
	
	public void testTableExists() throws Exception {
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		// Database URL with an example of setting params
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		Connection conn = null;
		Statement stmt = null;
		try {
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			stmt.execute("create table test_table_0 ( t1 integer autoincrement)");
			try{
				stmt.execute("create table test_table_0 ( t1 integer autoincrement)");
			} catch ( Exception e) {
//				e.printStackTrace();
			}
			ResultSet rs = stmt.executeQuery("select * from nonexistenttable");
			
		} catch(Exception ew) {
//			ew.printStackTrace();
			// expected exception, pass
			assertEquals("Error executing query SOS: Unable to find the specified object [KErrNotFound]", ew.getMessage());
		} finally {
			if ( stmt != null ) {
				try {stmt.close(); stmt = null;} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close(); conn = null;} catch (SQLException e) {e.printStackTrace();}
			}
		}
		
		
	}
	
	public void testInvalidDriverParams() throws Exception {
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		// array of test cases
		// each entry is an array containing: blockSize, clusterSize, secureId, expectedExcClass, expectedExcMsg
		// A null entry means that the param should be omitted from the url. If exception or message are null, 
		// then we don't expect exception
		String [][] vals = {
				{null,null,null,null,null},	
				{"",null,null,"java.sql.SQLException","Could not parse parameter 'volumeio.BlockSize='"},	
				{"-1",null,null,"java.sql.SQLException","Invalid value '-1' for volumeio.BlockSize driver parameter."},	
				{"0",null,null,"java.sql.SQLException","Invalid value '0' for volumeio.BlockSize driver parameter."},	
				{"lala",null,null,"java.lang.NumberFormatException","Invalid Block Size: For input string: \"lala\""},	
				{null,"",null,"java.sql.SQLException","Could not parse parameter 'volumeio.ClusterSize='"},	
				{null,"-1",null,"java.sql.SQLException","Invalid value '-1' for volumeio.ClusterSize driver parameter."},	
				{null,"0",null,"java.sql.SQLException","Invalid value '0' for volumeio.ClusterSize driver parameter."},
				{"4096","",null,"java.sql.SQLException","Could not parse parameter 'volumeio.ClusterSize='"},
				{"4096","-1",null,"java.sql.SQLException","Invalid value '-1' for volumeio.ClusterSize driver parameter."},
				{null,null,"-1",null,null},	
				{"-1",null,"-1","java.sql.SQLException","Invalid value '-1' for volumeio.BlockSize driver parameter."},
				{null,null,"-1rf","java.lang.NumberFormatException","Invalid Secure ID: For input string: \"-1rf\""}
		};
		
		for ( int i = 0 ; i < vals.length ; i ++ ) {
			StringBuilder sb = new StringBuilder("dbms:/test.db?");
			if ( vals[i][0] != null ) {
				// blockSize
				sb.append("volumeio.BlockSize=");
				sb.append(vals[i][0]);
				if ( vals[i][1] != null || vals[i][2] != null ) {
					sb.append("&");
				}
			}
			if ( vals[i][1] != null ) {
				// clusterSize
				sb.append("volumeio.ClusterSize=");
				sb.append(vals[i][1]);
				if ( vals[i][2] != null ) {
					sb.append("&");
				}
			}
			if ( vals[i][2] != null ) {
				// clusterSize
				sb.append("dbms.secureId=");
				sb.append(vals[i][2]);
			}
			Connection conn = null;
			String url = sb.toString();
//			System.out.println("Url ["+i+"]: " + url);
			try {
				conn = DriverManager.getConnection(url);
			} catch(Exception e) {
//				System.out.println("Exception class ["+i+"]: " + e.getClass().getName());
//				System.out.println("Message ["+i+"]: " + e.getMessage());
				if ( vals[i][3] == null ) {
					// unexpected exception
					fail("Unexpected exception for url=" + url +" "+ e.getMessage());
				}
				assertEquals("Exception class comparison", vals[i][3], e.getClass().getName());
				assertEquals("Exception message comparison", vals[i][4], e.getMessage());
			} finally {
				if ( conn != null ) {
					conn.close();
				}
			}
		}
	}
	
	public void testGetMax() throws Exception {
		Connection conn = null;
		Statement stmt = null;
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			stmt.execute("create table testgetmax ( t1 integer autoincrement)");
			stmt.execute("insert into testgetmax values (1)");
			assertEquals(1, DbmsDriver.getMax(conn, "testgetmax", "t1"));
			stmt.execute("insert into testgetmax values (2)");
			assertEquals(2, DbmsDriver.getMax(conn, "testgetmax", "t1"));
			stmt.execute("insert into testgetmax values (4)");
			assertEquals(4, DbmsDriver.getMax(conn, "testgetmax", "t1"));
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
	
	public void testNullString() throws Exception {
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		ResultSet rs = null;
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			pstmt = conn.prepareStatement("INSERT INTO TEST VALUES(?,?)");
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10))");
			pstmt.setInt(1, 1);
			pstmt.setString(2, null);
			pstmt.execute();
			rs = stmt.executeQuery("select * from test");
			assertTrue(rs.next()); 
			assertEquals(1, rs.getInt(1));
			String s = rs.getString(2);
			assertEquals(null, s);
		} finally {
			if ( rs != null ) {
				try {rs.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( pstmt != null ) {
				try {pstmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
		
	public void testSchemaDump() throws Exception {
		Connection conn = null;
		Statement stmt = null;
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10) NOT NULL, T3 DOUBLE)");
			stmt.execute("CREATE INDEX TEST_INDEX ON TEST(T2)");
			String schema = ((DbmsConnection)conn).getClientInfo("schema");
			System.out.println(schema);
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
	
	public void testPanicHandler() {
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10) NOT NULL, T3 DOUBLE)");
			stmt.execute("CREATE INDEX TEST_INDEX ON TEST(T2)");
			stmt.execute("INSERT INTO TEST (T2, T3) VALUES ('1s', 1.1)");
			ResultSet rs = stmt.executeQuery("select * from test");
			rs.getInt(2);
		} catch (Exception e) {
			// ok exception expected
			System.out.println("Got expected exception: " + e);
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( pstmt != null ) {
				try {pstmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
	
	public void testSimpleResultSet() throws Exception {
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10) NOT NULL, T3 DOUBLE)");
			stmt.execute("CREATE INDEX TEST_INDEX ON TEST(T2)");
			stmt.execute("INSERT INTO TEST (T2, T3) VALUES ('1s', 1.1)");
			stmt.close();
			stmt = null;
			// PreparedStatement example
			pstmt = conn.prepareStatement("INSERT INTO TEST (T2, T3) VALUES (?, ?)");
			pstmt.setString(1, "2s");
			pstmt.setDouble(2, 2.2);
			pstmt.execute();
			pstmt.setString(1, "3s");
			pstmt.setDouble(2, 3.3);
			pstmt.execute();
			try{
				pstmt.setDouble(3, 4.4);
				fail("Attempt to set non-existent col succeded");
			} catch (Exception e) {}
			pstmt.close();
			pstmt = null;

			pstmt = conn.prepareStatement("SELECT * from test");
			ResultSet rs = pstmt.executeQuery();
			ResultSetMetaData rsmd = rs.getMetaData();
			System.out.println("Testing result set meta data");
			assertEquals(3, rsmd.getColumnCount());
			assertEquals("T1", rsmd.getColumnName(1));
			assertEquals("T2", rsmd.getColumnName(2));
			assertEquals("T3", rsmd.getColumnName(3));
			assertEquals(Types.INTEGER, rsmd.getColumnType(1));
//			JDK 1.6 only
//			assertEquals(Types.NCHAR, rsmd.getColumnType(2));
			assertEquals(Types.CHAR, rsmd.getColumnType(2));
			assertEquals(Types.DOUBLE, rsmd.getColumnType(3));
			// TODO
			//rsmd.getPrecision(column)
			//rsmd.getTableName(column)
			assertEquals(true, rsmd.isAutoIncrement(1));
			assertEquals(false, rsmd.isAutoIncrement(2));
			assertEquals(false, rsmd.isAutoIncrement(3));
			assertEquals(ResultSetMetaData.columnNoNulls, rsmd.isNullable(1)); 
			assertEquals(ResultSetMetaData.columnNoNulls, rsmd.isNullable(2));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(3));
			
			System.out.println("Testing result set");
//			rs.
			boolean hasNext = rs.first();
			int i = 1;
			while ( hasNext ) {
				assertEquals(i-1, rs.getInt(1));
				assertEquals(""+i+"s", rs.getString(2));
				assertEquals(Double.parseDouble(""+i+"."+i), rs.getDouble(3));
				i++;
				hasNext = rs.next();
			}
			assertEquals(4, i);
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( pstmt != null ) {
				try {pstmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}

	public void testTypesResultSet() throws Exception {
		System.out.println("Testing result set and meta data with many types");
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		GregorianCalendar gc = new GregorianCalendar(TimeZone.getTimeZone("UTC"));
		gc.set(GregorianCalendar.YEAR, 2008);
		gc.set(GregorianCalendar.MONTH, GregorianCalendar.JUNE);
		gc.set(GregorianCalendar.DATE, 18);
		gc.set(GregorianCalendar.HOUR_OF_DAY, 16);
		gc.set(GregorianCalendar.MINUTE, 25);
		gc.set(GregorianCalendar.SECOND, 25);
		gc.set(GregorianCalendar.MILLISECOND, 0);
		Date testDate = gc.getTime();
		long testDateLong = testDate.getTime();
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10) NOT NULL, T3 DOUBLE, T4 REAL, T5 BIGINT, T6 VARCHAR, T7 TIMESTAMP, T8 VARBINARY, T9 DATE, T10 SMALLINT, T11 TINYINT, T12 CHAR8, T13 LONG VARCHAR8)");
			stmt.execute("INSERT INTO TEST (T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13) VALUES "
					+ "('1a', 1.1, 1.1, 10000000000, '1b', "+DbmsDriver.symFormatDateTime(testDateLong)+", X'CAFEBABE',  "+DbmsDriver.symFormatDateTime(testDateLong)+", 10000, 10, 'char8-1a', 'char8-1b')");
			stmt.close();
			stmt = null;
			// PreparedStatement example
			pstmt = conn.prepareStatement("INSERT INTO TEST (T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
			pstmt.setString(1, "2a");
			pstmt.setDouble(2, 2.2);
			pstmt.setFloat(3, 2.2F);
			pstmt.setLong(4, 20000000000L);
			pstmt.setString(5, "2b");
			pstmt.setTimestamp(6, new Timestamp(testDateLong));
			byte [] bytes = { (byte)0xC, (byte)0xA, (byte)0xF, (byte)0xE, (byte)0xB, (byte)0xA, (byte)0xB, (byte)0xE }; 
			pstmt.setBytes(7, bytes);
			pstmt.setDate(8, new java.sql.Date(testDateLong));
			pstmt.setShort(9, (short)20000);
			pstmt.setByte(10, (byte)20);
			pstmt.setString(11, "char8-2a");
			pstmt.setString(12, "char8-2b");
			pstmt.execute();
			
			pstmt.setString(1, "3a");
			pstmt.setDouble(2, 3.3);
			pstmt.setFloat(3, 3.3F);
			pstmt.setLong(4, 30000000000L);
			pstmt.setString(5, "3b");
			pstmt.setTimestamp(6, new Timestamp(testDateLong));
			pstmt.setBytes(7, bytes);
			pstmt.setDate(8, new java.sql.Date(testDateLong));
			pstmt.setShort(9, (short)30000);
			pstmt.setByte(10, (byte)30);
			pstmt.setString(11, "char8-3a");
			pstmt.setString(12, "char8-3b");
			pstmt.execute();
			pstmt.close();
			pstmt = null;

			pstmt = conn.prepareStatement("SELECT * from test");
			ResultSet rs = pstmt.executeQuery();
			ResultSetMetaData rsmd = rs.getMetaData();
			System.out.println("Testing result set meta data");
			assertEquals(13, rsmd.getColumnCount());
			for ( int i = 0 ; i < rsmd.getColumnCount(); i++ ) {
				assertEquals("T" + (i+1), rsmd.getColumnName(i+1));
			}
			assertEquals(Types.INTEGER, rsmd.getColumnType(1));
//			JDK 1.6 only
//			assertEquals(Types.NCHAR, rsmd.getColumnType(2));
			assertEquals(Types.CHAR, rsmd.getColumnType(2));
			assertEquals(Types.DOUBLE, rsmd.getColumnType(3));
			assertEquals(Types.FLOAT, rsmd.getColumnType(4));
			assertEquals(Types.BIGINT, rsmd.getColumnType(5));
//			JDK 1.6 only
//			assertEquals(Types.NCHAR, rsmd.getColumnType(6));     // as opposed to NVARCHAR
			assertEquals(Types.CHAR, rsmd.getColumnType(6));     // as opposed to NVARCHAR
			assertEquals(Types.TIMESTAMP, rsmd.getColumnType(7)); 
			assertEquals(Types.VARBINARY, rsmd.getColumnType(8));
			assertEquals(Types.TIMESTAMP, rsmd.getColumnType(9)); // as opposed to DATE
			assertEquals(Types.SMALLINT, rsmd.getColumnType(10));
			assertEquals(Types.TINYINT, rsmd.getColumnType(11));
			assertEquals(Types.CHAR, rsmd.getColumnType(12));
			assertEquals(Types.LONGVARCHAR, rsmd.getColumnType(13));

//			assertEquals("INTEGER", rsmd.getColumnTypeName(1));
//			assertEquals("CHAR", rsmd.getColumnTypeName(2));
//			assertEquals("FLOAT", rsmd.getColumnTypeName(3));
			// TODO
			//rsmd.getPrecision(column)
			//rsmd.getTableName(column)
			assertEquals(true, rsmd.isAutoIncrement(1));
			assertEquals(false, rsmd.isAutoIncrement(2));
			assertEquals(false, rsmd.isAutoIncrement(3));
			assertEquals(false, rsmd.isAutoIncrement(4));
			assertEquals(false, rsmd.isAutoIncrement(5));
			assertEquals(false, rsmd.isAutoIncrement(6));
			assertEquals(false, rsmd.isAutoIncrement(7));
			assertEquals(false, rsmd.isAutoIncrement(8));
			assertEquals(false, rsmd.isAutoIncrement(9));
			assertEquals(false, rsmd.isAutoIncrement(10));
			assertEquals(false, rsmd.isAutoIncrement(11));
			assertEquals(false, rsmd.isAutoIncrement(12));
			assertEquals(false, rsmd.isAutoIncrement(13));
			assertEquals(ResultSetMetaData.columnNoNulls, rsmd.isNullable(1)); 
			assertEquals(ResultSetMetaData.columnNoNulls, rsmd.isNullable(2));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(3));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(4));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(5));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(6));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(7));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(8));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(9));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(10));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(11));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(12));
			assertEquals(ResultSetMetaData.columnNullable, rsmd.isNullable(13));
			
			System.out.println("Testing result set");
//			rs.
			boolean hasNext = rs.first();
			int i = 1;
			while ( hasNext ) {
				assertEquals(i-1, rs.getInt(1));
				assertEquals(i-1, rs.getInt("T1"));
				assertEquals(""+i+"a", rs.getString(2));
				assertEquals(""+i+"a", rs.getString("T2"));
				assertEquals(Double.parseDouble(""+i+"."+i), rs.getDouble(3));
				assertEquals(Float.parseFloat(""+i+"."+i), rs.getFloat(4));
				assertEquals(10000000000L * i , rs.getLong(5));
				assertEquals(""+i+"b", rs.getString(6));
				java.sql.Date date = new java.sql.Date(testDateLong);
				java.sql.Timestamp timestamp = new java.sql.Timestamp(testDateLong);
				java.sql.Timestamp timestampFromDb = rs.getTimestamp(7);
//				System.out.println("RT       : long="+testDateLong+", ts.="+timestamp.getTime() + ", str="+timestamp.toString());
//				System.out.println("DB       : long="+testDateLong+", ts.="+timestampFromDb.getTime() + ", str="+timestampFromDb.toString());
				assertEquals(timestamp.toString(), timestampFromDb.toString());
				// verify bytes
				assertEquals(date.toString(), rs.getDate(9).toString());
				assertEquals((short)(i * 10000), rs.getShort(10));
				assertEquals((byte)(i * 10), rs.getByte(11));
				assertEquals("char8-"+i+"a", rs.getString(12));
				assertEquals("char8-"+i+"b", rs.getString(13));
				i++;
				hasNext = rs.next();
			}
			assertEquals(4, i);
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( pstmt != null ) {
				try {pstmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}
	
	public void testTransaction(){
		
	}
	
	// memory leak test - monitor memory usage over a large transaction
	public void testDriverWithManyLargeRecords() throws Exception {
		int numRecords = 100;
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		try {
			File f = new File("test.db");
			if ( f.exists() ) {
				f.delete();
			}
			if ( f.exists() ) {
				fail ( "file locked");
			}
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=4096";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 VARCHAR, T3 LONG VARCHAR, T4 VARCHAR8, T5 LONG VARCHAR8, T6 VARBINARY, T7 LONG VARBINARY)");
			stmt.close();
			stmt = null;
			// PreparedStatement example
			long prevMemUsage = memUsage();
			pstmt = conn.prepareStatement("INSERT INTO TEST (T2, T3, T4, T5, T6, T7) VALUES (?, ?, ?, ?, ?, ?)");
			// test for memory usage during insertions
			for ( int i = 0; i < numRecords ; i ++ ) {
				pstmt.setString(1, makeString(1,i));
				pstmt.setString(2, makeLongString(2,i));
				pstmt.setString(3, makeString(3,i));
				pstmt.setString(4, makeLongString(4,i));
				pstmt.setBytes(5, makeBlob(5,i));
				pstmt.setBytes(6, makeLongBlob(6,i));
				pstmt.execute();
			}
			pstmt.close();
			pstmt = null;
			long memUsage = memUsage();
			if ( memUsage > 1.3 * prevMemUsage ) {
				fail("Mem usage now:" + memUsage + ", prev:" + prevMemUsage);
			} else { 
				System.out.println("Mem: " + memUsage + ", prev: " + prevMemUsage);
			}

			// test for memory usage during retrieval
			prevMemUsage = memUsage();
			pstmt = conn.prepareStatement("SELECT * from test");
			ResultSet rs = pstmt.executeQuery();

			boolean hasNext = rs.first();
			int i = 0;
			while ( hasNext ) {
				assertEquals(i, rs.getInt(1));
				assertEquals(makeString(1,i), rs.getString(2));
				assertEquals(makeLongString(2,i), rs.getString(3));
				assertEquals(makeString(3,i), rs.getString(4));
				assertEquals(makeLongString(4,i), rs.getString(5));
				compareBlobs(makeBlob(5,i), rs.getBytes(6));
				compareBlobs(makeLongBlob(6,i), rs.getBytes(7));
				i++;
				hasNext = rs.next();
			}
			memUsage = memUsage();
			if ( memUsage > 1.3 * prevMemUsage  ) {
				fail("Mem usage now:" + memUsage + ", prev:" + prevMemUsage);
			} else { 
				System.out.println("Mem: " + memUsage + ", prev: " + prevMemUsage);
			}
			assertEquals(numRecords, i);
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( pstmt != null ) {
				try {pstmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( conn != null ) {
				try {conn.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	}

	private void compareBlobs(byte[] makeBlob, byte[] bytes) {
		assertEquals(makeBlob.length, bytes.length);
		for ( int i = 0 ; i < makeBlob.length ; i++ ) {
			assertEquals(makeBlob[i], bytes[i]);
		}
	}

	private long memUsage() {
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		Runtime rt = Runtime.getRuntime();
		return rt.totalMemory() - rt.freeMemory();
	}

	private byte[] makeLongBlob(int i, int i2) {
		return makeLongString(i, i2).getBytes();
	}

	private byte[] makeBlob(int i, int i2) {
		return makeString(i, i2).getBytes();
	}

	private String makeLongString(int i, int i2) {
		StringBuilder sb = new StringBuilder();
		for ( int a = 0; a < 4096 ; a++) {
			sb.append(a);
			sb.append(i);
			sb.append(i2);
		}
		return sb.toString();
	}

	private String makeString(int i, int i2) {
		StringBuilder sb = new StringBuilder();
		for ( int a = 0; a < 8 ; a++) {
			sb.append(a);
			sb.append(i);
			sb.append(i2);
		}
		return sb.toString();
	}
}
