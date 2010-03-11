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

import java.io.File;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Before;
import org.junit.Test;

public class SqlExecuterTest {
    Mockery context = new Mockery();
    Mockery stmContext = new Mockery();
    Connection con;
    SqlExecuter executer = new SqlExecuter();

    public static junit.framework.Test suite() {
        return new JUnit4TestAdapter(SqlExecuterTest.class);
    }

    @Before
    public void setUp() throws Exception {
        con = context.mock(Connection.class);
    }

    @Test
    public void testExecuteSql1() throws SQLException {
        final Statement stm = stmContext.mock(Statement.class);

        context.checking(new Expectations() {
            {
                one(con).createStatement(); will(returnValue(stm));
               
            }
        });

        stmContext.checking(new Expectations() {
            {
                one(stm).execute(with(equal("select * from table")));
                one(stm).close();
            }
        });

        Reader input = new StringReader("select * from table;");

        executer.executeSql(input, con, false);

        context.assertIsSatisfied();
        stmContext.assertIsSatisfied();
    }

    @Test
    public void testExecuteSql2() throws SQLException {
        final Statement stm = stmContext.mock(Statement.class);

        context.checking(new Expectations() {
            {
                atLeast(1).of(con).createStatement(); will(returnValue(stm));
            }
        });

        stmContext.checking(new Expectations() {
            {
                one(stm).execute(with(equal("select * from table")));
                one(stm).close();
                one(stm).execute(with(equal("select column1 from table1")));
                one(stm).close();
            }
        });

        Reader input = new StringReader(
                "select * from table;select column1 from table1;");

        executer.executeSql(input, con, false);

        context.assertIsSatisfied();
        stmContext.assertIsSatisfied();
    }

    @Test
    public void testExecuteSql3() throws SQLException {
        final Statement stm = stmContext.mock(Statement.class);

        context.checking(new Expectations() {
            {
            	atLeast(1).of(con).createStatement();  will(returnValue(stm));
            }
        });

        stmContext.checking(new Expectations() {
            {
                one(stm).execute(with(equal("select * from table")));
                one(stm).close();
                one(stm).execute(with(equal("select column1 from table1")));
                one(stm).close();
            }
        });

        Reader input = new StringReader(
                "select * from table;\nselect column1 from table1;");

        executer.executeSql(input, con, false);

        context.assertIsSatisfied();
        stmContext.assertIsSatisfied();
    }

    @Test
    public void testExecuteList() throws SQLException {
        final Statement stm = stmContext.mock(Statement.class);

        context.checking(new Expectations() {
            {
            	atLeast(1).of(con).createStatement(); will(returnValue(stm));
            }
        });

        stmContext.checking(new Expectations() {
            {
                one(stm).execute(with(equal("select * from table")));
                one(stm).close();
                one(stm).execute(with(equal("select column1 from table1")));
                one(stm).close();
            }
        });

        List<String> list = new ArrayList<String>();
        list.add("select * from table;");
        list.add("select column1 from table1");

        executer.executeSql(list, con, false);

        context.assertIsSatisfied();
        stmContext.assertIsSatisfied();
    }

    @Test
    public void testExecuteFiles() throws SQLException, IOException {
        final Statement stm = stmContext.mock(Statement.class);

        context.checking(new Expectations() {
            {
            	atLeast(1).of(con).createStatement(); will(returnValue(stm));
            }
        });

        stmContext.checking(new Expectations() {
            {
                one(stm).execute(with(equal("select * from table")));
                one(stm).close();
                one(stm).execute(with(equal("select column1 from table1")));
                one(stm).close();
                one(stm).execute(with(equal("create table t1(t1key INTEGER PRIMARY KEY, data TEXT, num double, timeEnter DATE)")));
                one(stm).close();
            }
        });

        List<File> list = new ArrayList<File>();
        list.add(new File("tests/config/example.sql"));
        list.add(new File("tests/config/example1.sql"));

        executer.applySqlFilesToDb(list, con, false);

        context.assertIsSatisfied();
        stmContext.assertIsSatisfied();
    }
}
