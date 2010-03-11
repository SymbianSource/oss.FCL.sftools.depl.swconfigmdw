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

package com.symbian.sdb.mode.flow;


import java.io.File;
import java.io.Reader;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.hamcrest.Description;
import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.api.Action;
import org.jmock.api.Invocation;
import org.jmock.lib.legacy.ClassImposteriser;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.configuration.ConfigurationValidator;
import com.symbian.sdb.configuration.PlatsecConfigurator;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.ModeParser;

public class GenericFlowDbmsIntegrationTest {
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(GenericFlowDbmsIntegrationTest.class); 
    }
    
    Mockery connectionContext = new Mockery();
    Mockery statementContext = new Mockery();
    Mockery preparedStmContext = new Mockery();
    Mockery managerContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    Mockery commandContext = new Mockery();
    
    Mockery executerContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }};
    
    Mockery configurationContext = new Mockery() {{
        setImposteriser(ClassImposteriser.INSTANCE);
    }}; 
    
    Statement stm;
    PreparedStatement pStm;
    Connection conn;
    DBManager manager;
    CmdLineArgs cmd;
    SqlExecuter executer;
    Configuration configuration;
    
    File temp, temp2;
    
    public class OpenConnectionAction implements Action {
        File file;
        
        public OpenConnectionAction(File file) {
            this.file = file;
        }
        
        public void describeTo(Description description) {
            description.appendText("opens a connection");
        }
        
        public Object invoke(Invocation invocation) throws Throwable {
           // return DriverManager.getConnection("jdbc:sqlite:" + file.getName() + ".tmp");
            file.createNewFile();
            return null;
        }
    }
    
    @BeforeClass
    public static void setUpBeforeClass() throws Exception {
        System.setProperty("com.symbian.dbms.lib.path", "lib/");
    }

    @AfterClass
    public static void tearDownAfterClass() throws Exception {
    }

    @Before
    public void setUp() throws Exception {
        stm = statementContext.mock(Statement.class);
        conn = connectionContext.mock(Connection.class);
        manager = managerContext.mock(DBManager.class);
        cmd = commandContext.mock(CmdLineArgs.class);
        executer = executerContext.mock(SqlExecuter.class);
        pStm = preparedStmContext.mock(PreparedStatement.class);
        configuration = configurationContext.mock(Configuration.class);
        
        temp = new File("dbtest.db");
        temp2 = new File(temp.getName()+".tmp");
   
        executerContext.checking(new Expectations() {{
            one (executer).applySqlFilesToDb(with(any(List.class)), with(any(Connection.class)),with(true)); will(returnValue(true)); 
            never (executer).executeSql(with(any(Reader.class)), with(any(Connection.class)),with(true)); will(returnValue(true));
            one (executer).executeSql(with(any(List.class)), with(any(Connection.class)),with(true)); will(returnValue(true));
        }});
        
        statementContext.checking(new Expectations() {{
          //  atLeast(1).of (stm).execute(with(any(String.class))); 
        }});
        
        preparedStmContext.checking(new Expectations() {{
              allowing (pStm).execute(); 
              allowing (pStm).close(); 
          }});
        
        connectionContext.checking(new Expectations() {{
             allowing (conn).createStatement(); will(returnValue(stm));
             allowing (conn).prepareStatement(with(any(String.class))); will(returnValue(pStm));
             allowing (conn).isClosed(); will(returnValue(false));
        }});
        
        managerContext.checking(new Expectations() {{
            one (manager).openConnection(DBType.DBMS, temp2.getName(), null);  will(new OpenConnectionAction(temp2));
            allowing (manager).isConnectionOpen(); will(returnValue(true));
            allowing (manager).closeConnection(); 
            atLeast(1).of (manager).getConnection(); will(returnValue(conn));
        }});
    }

    @After
    public void tearDown() throws Exception {
    }

    
    @Test
    public void testGenerateDbmsDB() throws Exception {
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(null));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(null));
             atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("dbms")));
             //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             one (cmd).failFast(); will(returnValue(true));
             one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             never (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
        }});
        
       configurationContext.checking(new Expectations() {{
           never (configuration).initialize(with(any(File.class)), with(DBType.DBMS), with(any(ConfigurationValidator.class)));
           one (configuration).applySecurity(with(DBType.DBMS), with(any(PlatsecConfigurator.class)));
           one (configuration).getPragmaStm(with(DBType.DBMS)); will(returnValue(new ArrayList<String>()));
           one (configuration).getConnectionString(with(DBType.DBMS)); will(returnValue(null));
       }});
       
       GenericFlow gFlow = new GenericFlow(executer, configuration);
       gFlow.setDatabaseManager(manager);
       
       gFlow.validateOptions(cmd);
       gFlow.start(cmd);
       
       Assert.assertTrue(temp.exists());
    }
    
}
