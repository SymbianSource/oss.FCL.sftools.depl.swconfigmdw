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

package com.symbian.sdb.configuration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Assert;
import org.junit.Test;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBMode;

public class SystemSettingsTest {
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(SystemSettingsTest.class); 
    }
    
    Mockery connectionContext = new Mockery(); 
    Mockery statementContext = new Mockery();
    Mockery resultContext = new Mockery();
    
    Connection conn;    
    Statement stm;
    ResultSet resultset;

    @Test
    public void testHasSettingsTable() throws SQLException, SDBExecutionException {
        conn = connectionContext.mock(Connection.class);
        stm = statementContext.mock(Statement.class);
        resultset = resultContext.mock(ResultSet.class);
        
        resultContext.checking(new Expectations() {{
            one (resultset).next(); will(returnValue(true));
            one (resultset).close();
        }});
        
        statementContext.checking(new Expectations() {{
            one (stm).executeQuery(with(any(String.class))); will(returnValue(resultset));
            one (stm).close();
         }});
        
        connectionContext.checking(new Expectations() {{
            allowing (conn).createStatement(); will(returnValue(stm));
            allowing (conn).isClosed(); will(returnValue(false));
       }});
        
        SystemSettings settings = new SystemSettings(conn, DBMode.GENERIC);
        boolean result = settings.hasSettingsTable();
        Assert.assertTrue(result);
    }

    
    @Test(expected=SDBExecutionException.class)
    public void testHasSettingsTableException() throws SQLException, SDBExecutionException {
        conn = connectionContext.mock(Connection.class);
        stm = statementContext.mock(Statement.class);
        resultset = resultContext.mock(ResultSet.class);
        
        resultContext.checking(new Expectations() {{
            one (resultset).first(); will(returnValue(true));
            one (resultset).close();
        }});
        
        statementContext.checking(new Expectations() {{
            one (stm).executeQuery(with(any(String.class))); will(throwException(new SQLException()));
            one (stm).close();
         }});
        
        connectionContext.checking(new Expectations() {{
            allowing (conn).createStatement(); will(returnValue(stm));
            allowing (conn).isClosed(); will(returnValue(false));
       }});
        
        SystemSettings settings = new SystemSettings(conn, DBMode.GENERIC);
        boolean result = settings.hasSettingsTable();
        Assert.assertTrue(result);
    }

    
    @Test
    public void testApplySystemSettings() throws SQLException, SDBExecutionException {
        conn = connectionContext.mock(Connection.class);
        stm = statementContext.mock(Statement.class);
        
        statementContext.checking(new Expectations() {{
            exactly(2).of (stm).execute(with(any(String.class))); 
            one (stm).close();
         }});
        
        connectionContext.checking(new Expectations() {{
            allowing (conn).createStatement(); will(returnValue(stm));
            allowing (conn).isClosed(); will(returnValue(false));
       }});
        
        SystemSettings settings = new SystemSettings(conn, DBMode.GENERIC);
        settings.applySystemSettings();

    }

    @Test(expected=SDBExecutionException.class)
    public void testApplySystemSettingsException() throws SQLException, SDBExecutionException {
        conn = connectionContext.mock(Connection.class);
        stm = statementContext.mock(Statement.class);
        
        statementContext.checking(new Expectations() {{
            exactly(2).of (stm).execute(with(any(String.class))); will(throwException(new SQLException())); 
            one (stm).close();
         }});
        
        connectionContext.checking(new Expectations() {{
            allowing (conn).createStatement(); will(returnValue(stm));
            allowing (conn).isClosed(); will(returnValue(false));
       }});
        
        SystemSettings settings = new SystemSettings(conn, DBMode.GENERIC);
        settings.applySystemSettings();

    }
    
}
