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
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Random;

public class SmokeTest {
	public static void main(String [] a ) {
		Connection conn = null;
		Statement stmt = null;
		PreparedStatement pstmt = null;
		Random r = new Random();
		try {
			// Driver registration
			Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
			// Database URL with an example of setting params
			String url = "dbms:/test.db?volumeio.BlockSize=8192";
			// From here on, all is standard JDBC
			conn = DriverManager.getConnection(url);
			stmt = conn.createStatement();
			stmt.execute("CREATE TABLE TEST (T1 INTEGER, T2 CHAR(10), T3 FLOAT, T4 LONG VARBINARY)");
			stmt.execute("INSERT INTO TEST (T1, T2, T3, T4) VALUES (1, '1s', 1.1, X'CAFEBABE' )");
			stmt.close();
			stmt = null;
			// PreparedStatement example
			byte[] bytes = new byte[12];
			r.nextBytes(bytes);
			pstmt = conn.prepareStatement("INSERT INTO TEST (T1, T2, T3, T4) VALUES (?, ?, ?, ?)");
			pstmt.setInt(1, 2);
			pstmt.setString(2, "2s");
			pstmt.setFloat(3, 2.2F);
			pstmt.setBytes(4, bytes);
			pstmt.execute();
			r.nextBytes(bytes);
			pstmt.setInt(1, 3);
			pstmt.setString(2, "3s");
			pstmt.setFloat(3, 3.3F);
			pstmt.setBytes(4, bytes);
			pstmt.execute();
			
		} catch (Exception e) {
			e.printStackTrace();
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

}
