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
import java.io.FileReader;
import java.io.Reader;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import mockit.Mockit;

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
import org.junit.Ignore;
import org.junit.Test;
import org.springframework.test.annotation.ExpectedException;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.configuration.ConfigurationValidator;
import com.symbian.sdb.configuration.PlatsecConfigurator;
import com.symbian.sdb.configuration.SystemSettings;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.ModeParser;
import com.symbian.sdb.mode.flow.GenericFlowTest.OpenConnectionAction;
import com.symbian.sdb.mode.flow.ced.FlowCompletionException;
import com.symbian.sdb.util.FileUtil;

public class GenericFlowIntegrationTest {
    
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(GenericFlowTest.class); 
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
        System.setProperty("sdb.schema.location.1.0", "tests//config//XML//sdb.xsd");
        System.setProperty("org.sqlite.lib.path", "lib\\");
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
            atLeast(1).of (executer).executeSql(with(any(Reader.class)), with(any(Connection.class)),with(true)); will(returnValue(true));
            allowing (executer).executeSql(with(any(List.class)), with(same(conn)),with(true)); will(returnValue(true));
        }});
        
        statementContext.checking(new Expectations() {{
            allowing (stm).execute(with(any(String.class))); 
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
            oneOf (manager).openConnection(DBType.SQLITE, temp2.getName(), null);  will(new OpenConnectionAction(temp2));
            atLeast(1).of (manager).closeConnection(); 
            atLeast(1).of (manager).getConnection(); will(returnValue(conn));
            allowing (manager).isConnectionOpen(); will(returnValue(true));
        }});
        
    }

    @After
    public void tearDown() throws Exception {
        File temp = new File("dbtest.db");
        temp.delete();
        File temp2 = new File(temp.getName()+".tmp");
        temp2.delete();
    }

    @Test
    public void testGenerateSqliteDB() throws Exception {
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(new File("tests//config//XML//sec.xml")));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(null));
             atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
             //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             allowing (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
             atLeast(1).of(cmd).failFast(); will(returnValue(true));
       }});
        
       
       configurationContext.checking(new Expectations() {{
           one (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
           one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
           one (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
           one (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
           one (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
       }});
       
       GenericFlow gFlow = createGenericFlow();
       
       gFlow.validateOptions(cmd);
       gFlow.start(cmd);
       
       Assert.assertTrue(temp.exists());
       commandContext.assertIsSatisfied();
       managerContext.assertIsSatisfied();
       connectionContext.assertIsSatisfied();
       statementContext.assertIsSatisfied();
    }
    

    @Ignore//(expected=SDBValidationException.class)
    public void testGenericWithVCards() throws Exception {
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(new File("tests//config//XML//sec.xml")));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(null));
             atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
             //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             allowing (cmd).getvCardFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.vcf"))));
        }});
       
       configurationContext.checking(new Expectations() {{
           one (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
           one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
           never (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
           never (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
           never (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
       }});
       
       GenericFlow gFlow = createGenericFlow();
       
       gFlow.validateOptions(cmd);
    }
    
    @Ignore//(expected=SDBValidationException.class)
    public void testGenericWithoutSQL() throws Exception {
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(new File("tests//config//XML//sec.xml")));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(null));
             atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
             //never (cmd).getInputFiles(); will(returnValue(new ArrayList<File>()));
             one (cmd).getSQLFiles(); will(returnValue(new ArrayList<File>()));
             allowing (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
        }});
        
       
       configurationContext.checking(new Expectations() {{
           one (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
           one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
           never (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
           never (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
           never (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
       }});
       
       GenericFlow gFlow = createGenericFlow();
       
       gFlow.validateOptions(cmd);
    }

    @Ignore//(expected=SDBValidationException.class)
    public void testGenericUpdateWithNoInput() throws Exception {
        final File existing = new File("tests//config//existingdb.db");
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(null));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(existing));
             allowing (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
             //allowing (cmd).getInputFiles(); will(returnValue(new ArrayList<File>()));
             allowing (cmd).getSQLFiles(); will(returnValue(new ArrayList<File>()));
             allowing (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
        }}); 
       
       configurationContext.checking(new Expectations() {{
           one (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
           one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
           allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
           never (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
           never (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
       }});
       
       GenericFlow gFlow = createGenericFlow();
       
       gFlow.validateOptions(cmd);
    }
    
    @Test
    public void testGenericExistingTempFile() throws Exception {
        //final File existing = new File("tests//config//existingdb.db");
       temp2.createNewFile(); 
       commandContext.checking(new Expectations() {{
             one (cmd).getConfigurationFile(); will(returnValue(null));
             one (cmd).getOutputDb(); will(returnValue(temp));
             one (cmd).getInputDb(); will(returnValue(null));
             allowing (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
             //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
             allowing (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
             atLeast(1).of(cmd).failFast(); will(returnValue(true));
        }});
       
       configurationContext.checking(new Expectations() {{
           never (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
           one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
           allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
           one (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
           one (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
       }});
       
       GenericFlow gFlow = createGenericFlow();
       
       gFlow.validateOptions(cmd);
       gFlow.start(cmd);
       
       Assert.assertTrue(temp.exists());
       commandContext.assertIsSatisfied();
       managerContext.assertIsSatisfied();
       connectionContext.assertIsSatisfied();
       statementContext.assertIsSatisfied();
    }
    
    @Test(expected=SDBExecutionException.class)
    public void testGenericExistingTempFileCannotDelete() throws Exception {
        //final File existing = new File("tests//config//existingdb.db");
       temp2.createNewFile(); 
       FileReader reader = new FileReader(temp2);
       try {
           commandContext.checking(new Expectations() {{
                 one (cmd).getConfigurationFile(); will(returnValue(null));
                 one (cmd).getOutputDb(); will(returnValue(temp));
                 one (cmd).getInputDb(); will(returnValue(null));
                 allowing (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
                 //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
                 one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
                 one (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
                 allowing (cmd).failFast(); will(returnValue(false));
            }});
           configurationContext.checking(new Expectations() {{
               never (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
               one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
               allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
               never (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
               never (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
           }});
           
           GenericFlow gFlow = createGenericFlow();
           
           gFlow.validateOptions(cmd);
           gFlow.start(cmd);
           
           Assert.assertTrue(temp.exists());
           commandContext.assertIsSatisfied();
           managerContext.assertIsSatisfied();
           connectionContext.assertIsSatisfied();
           statementContext.assertIsSatisfied();
       } finally {
           reader.close();
       }
    }
    
    @Test
    public void testUpdateSQLiteDB() throws Exception {
        final File existing = new File("tests//config//existingdb.db");
        commandContext.checking(new Expectations() {{
            one (cmd).getConfigurationFile(); will(returnValue(null));
            //will(returnValue(new File("tests//config//XML//sec.xml")));
            one (cmd).getOutputDb(); will(returnValue(temp));
            one (cmd).getInputDb(); will(returnValue(existing));
            atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
            //allowing (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
            one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
            never (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
            atLeast(1).of(cmd).failFast(); will(returnValue(true));
        }});

        configurationContext.checking(new Expectations() {{
            never (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
            one (configuration).applySettings(with(true), with(any(SystemSettings.class)));
            allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
            one (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
            one (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
        }});

        GenericFlow gFlow = createGenericFlow();

        gFlow.validateOptions(cmd);
        gFlow.start(cmd);

        Assert.assertTrue(temp.exists());
        Assert.assertTrue(temp.length() == existing.length());

        commandContext.assertIsSatisfied();
        managerContext.assertIsSatisfied();
        connectionContext.assertIsSatisfied();
        statementContext.assertIsSatisfied();
    }

	/**
	 * @return
	 */
	private GenericFlow createGenericFlow() {
		GenericFlow gFlow = new GenericFlow(executer, configuration);
        gFlow.setInputDatabaseValidator(new GenericFlowInputDatabaseValidator());
		gFlow.setDatabaseManager(manager);
		return gFlow;
	}

    @Test
    public void testGenerateSQLiteDB_ExistingOutputDB() throws Exception {
        final File existing = new File("tests//config//existingdb.db");
        FileUtil.copy(existing.getAbsolutePath(), temp.getAbsolutePath());
        commandContext.checking(new Expectations() {{
            one (cmd).getConfigurationFile(); will(returnValue(null));
            //will(returnValue(new File("tests//config//XML//sec.xml")));
            one (cmd).getOutputDb(); will(returnValue(temp));
            one (cmd).getInputDb(); will(returnValue(existing));
            atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
            //allowing (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
            one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//data.sql"))));
            never (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
            atLeast(1).of(cmd).failFast(); will(returnValue(true));
        }});

        configurationContext.checking(new Expectations() {{
            never (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
            one (configuration).applySettings(with(true), with(any(SystemSettings.class)));
            allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
            one (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
            one (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
        }});

        GenericFlow gFlow = createGenericFlow();

        gFlow.validateOptions(cmd);
        gFlow.start(cmd);

        Assert.assertTrue(temp.exists());
        Assert.assertTrue(temp.length() == existing.length());

        commandContext.assertIsSatisfied();
        managerContext.assertIsSatisfied();
        connectionContext.assertIsSatisfied();
        statementContext.assertIsSatisfied();
    }
    
    @Test
    public void testGenerateSQLiteDB_BadSQL() throws Exception {
        commandContext.checking(new Expectations() {{
            one (cmd).getConfigurationFile(); will(returnValue(null));
            //will(returnValue(new File("tests//config//XML//sec.xml")));
            one (cmd).getOutputDb(); will(returnValue(temp));
            one (cmd).getInputDb(); will(returnValue(null));
            atLeast(1).of (cmd).getMode(); will(returnValue(new ModeParser("sqlite")));
            //never (cmd).getInputFiles(); will(returnValue(Collections.singletonList(new File("tests//config//badSql.sql"))));
            one (cmd).getSQLFiles(); will(returnValue(Collections.singletonList(new File("tests//config//badSql.sql"))));
            allowing (cmd).getvCardFiles(); will(returnValue(new ArrayList<File>()));
            atLeast(1).of(cmd).failFast(); will(returnValue(true));
        }});

        configurationContext.checking(new Expectations() {{
            never (configuration).initialize(with(any(File.class)), with(same(DBType.SQLITE)), with(any(ConfigurationValidator.class)));
            one (configuration).applySettings(with(false), with(any(SystemSettings.class)));
            allowing (configuration).applySecurity(with(DBType.SQLITE), with(any(PlatsecConfigurator.class)));
            one (configuration).getPragmaStm(with(same(DBType.SQLITE))); will(returnValue(new ArrayList<String>()));
            one (configuration).getConnectionString(with(same(DBType.SQLITE))); will(returnValue(null));
        }});

        GenericFlow gFlow = createGenericFlow();

        gFlow.validateOptions(cmd);
        gFlow.start(cmd);

        Assert.assertTrue(temp.exists());
        Assert.assertTrue(temp.length() == 0);

        commandContext.assertIsSatisfied();
        managerContext.assertIsSatisfied();
        connectionContext.assertIsSatisfied();
        statementContext.assertIsSatisfied();
    }
    
    @Test(expected=SDBValidationException.class)
    public void testValidationForNonExistentInputDb() throws Exception {
	   String noneExistentDB = "noneExistent.db";
	   runGenericFlowsInputDBChecking(noneExistentDB);
    }

    @Test
    public void testValidationForExistentInputDb() throws Exception {
 	   String existentDB = "tests/config/existingdb.db";
	   runGenericFlowsInputDBChecking(existentDB);
    }

	private void runGenericFlowsInputDBChecking(String noneExistentDB)	throws SDBExecutionException {
		GenericFlow flow = createGenericFlow();
		flow.setInputDbFile(new File(noneExistentDB));
		flow.validateInputDB();
	}
	
	
	//DPDEF130191
    @Test(expected=SDBValidationException.class)
	public void testNonExistentDbFromCommandline() throws Exception {
    	CmdLinev2 cmd = new CmdLinev2();
    	cmd.parseArguments(new String[]{"-m", "dbms", "-i", "noneExistent12345.db", "-o", "foo21.db"});

		GenericFlow flow = new GenericFlow(null,null);
		flow.setInputDatabaseValidator(new GenericFlowInputDatabaseValidator());
		flow.validateOptions(cmd);
	}
}
