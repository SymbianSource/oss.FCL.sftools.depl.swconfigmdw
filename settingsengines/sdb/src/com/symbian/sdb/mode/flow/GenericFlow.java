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
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;

import org.apache.log4j.Logger;

import com.symbian.sdb.Application;
import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.configuration.ConfigurationValidator;
import com.symbian.sdb.configuration.PlatsecConfigurator;
import com.symbian.sdb.configuration.SystemSettings;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBMode;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.flow.ced.FlowCompletionException;
import com.symbian.sdb.mode.flow.ced.SDBExecutionExitCodes;
import com.symbian.sdb.util.FileUtil;

/**
 * The flow for the creation of the generic sqlite and dbms databases
 */
public class GenericFlow implements IFlow {

    protected  File outputDbFile;
    protected  File inputDbFile;
    protected  File configFile;
    
   // protected File tmpDbFile;
    
    protected  List<File> sqlFiles;
    
    protected DBType dbType;
    protected DBMode dbMode;
    protected DBManager databaseManager;
    protected SqlExecuter sqlExecuter;
    protected Configuration configuration;
    protected DBValidator inputDatabaseValidator;
    

	protected boolean update = false;
    
    protected boolean failFast = true;
    
    public GenericFlow() {
        this(new SqlExecuter(), new Configuration()); 
    }
    
    public GenericFlow(SqlExecuter executer, Configuration configuration) {
        this.sqlExecuter = executer;
        this.configuration = configuration;
    }
    
	private static final Logger logger = Logger.getLogger(Application.class);

	public void validateOptions(CmdLineArgs cmd) throws SDBValidationException {
	    configFile = cmd.getConfigurationFile();
	    
	    if (configFile != null && configFile.exists() && configFile.isFile()) {
	        configuration.initialize(configFile, cmd.getMode().getDbType(), new ConfigurationValidator());
	    }
	    
	    dbType = cmd.getMode().getDbType();
	    
	    dbMode = cmd.getMode().getDbMode();
	    
	    failFast = cmd.failFast();
	    
        outputDbFile = FileUtil.determineOutputFile(cmd.getOutputDb());
        
        inputDbFile = cmd.getInputDb();
        
        determineUpdateMode();
        
	    //TODO somehow the type of the database has to be resolved here - if it's the same as the mode

	    sqlFiles = cmd.getSQLFiles();
	}

	protected void validateInputDB() throws SDBExecutionException {
		if (isInputDBParameterProvided())	{
			try {
				inputDatabaseValidator.validate(inputDbFile);
			} catch (SDBValidationException e) {
				throw new SDBExecutionException(e.getMessage(),e);
			}	
		}
	}

	private boolean isInputDBParameterProvided() {
		return inputDbFile != null;
	}

	protected void determineUpdateMode() {
		if (isInputDBParameterProvided() && inputDbFile.exists()) {
			update = true;
        } else {
        	update = false;
        }
	}

	protected File prepareTemporaryFile() throws SDBExecutionException {
		File tmpDbFile = new File(outputDbFile.getPath() + ".tmp");
		
        if (tmpDbFile.exists()) {
            if (tmpDbFile.delete()) {
                logger.debug("Deleting existing temp file: " + outputDbFile + ".tmp");
            } else {
                logger.debug("Temporary file " + outputDbFile + ".tmp couldn't be deleted.");
                throw new SDBExecutionException("Temporary file " + outputDbFile + ".tmp couldn't be deleted.");
            }
        }
        
        // if we are supplied with an existing database, first we copy
        // it to the file we are going to work on so we can append to it without
        // overwriting the original
        if (update) {
            try {
                FileUtil.copy(inputDbFile.getPath(), tmpDbFile.getPath());
            } catch (IOException ex) {
                throw new SDBExecutionException("Failed to copy input DB to temporary location: " + tmpDbFile.getPath() + ": " + ex.getMessage(), ex);
            }
        }
        
        return tmpDbFile;
	}
	
	protected boolean openAndConfigureDatabase(File tmpDbFile) throws SDBExecutionException {
        logger.info("Opening database...");
        boolean result = true;
        
		if (update) {
            //TODO recreate db with the new configuration settings if settings provided in the xml file are different
        }
        
        databaseManager.openConnection(dbType, tmpDbFile.getPath(), configuration.getConnectionString(dbType));
        
        try {
        	logger.debug("Applying pragma statements");
        	result &= sqlExecuter.executeSql(configuration.getPragmaStm(dbType), databaseManager.getConnection(), failFast);
        } catch (SQLException e) {
            throw new SDBExecutionException("Problem applying PRAGMA to DB.", e);
        } 

        if (dbType.equals(DBType.SQLITE)) {
            //apply system setting if this is new databaseManager
            configuration.applySettings(update, 
            		new SystemSettings(databaseManager.getConnection(), dbMode)
            );  
        }
        
        //apply the security settings
        configuration.applySecurity(dbType, new PlatsecConfigurator(databaseManager.getConnection()));
        return result;
	}
	
	protected boolean applySql(List<File> files) throws SDBExecutionException {
		boolean result = true;
        // Apply user SQL to DB
        try {
        	logger.debug("Executing SQL files: "+files.toString());
        	result &= sqlExecuter.applySqlFilesToDb(files, databaseManager.getConnection(), failFast);
        } catch (SQLException e) {
            throw new SDBExecutionException("Problem applying SQL to DB.", e);
        } catch (IOException e) {
            throw new SDBExecutionException("Problem reading SQL input files.", e);
        }
        return result;
	}
	
	protected boolean applyUserSql() throws SDBExecutionException {
		return applySql(sqlFiles);
	}
	
	public void start(CmdLineArgs cmd) throws SDBExecutionException {
		logger.info("Generic mode started");
		boolean executionSuccessful = true;
		// This is the file we will work on
		File tmpDbFile = null;
		try {
			validateInputDB();
			
			tmpDbFile = prepareTemporaryFile();
			
            executionSuccessful = openAndConfigureDatabase(tmpDbFile);
            
            
            
            executionSuccessful &= applyUserSql();

            closeDatabase(tmpDbFile, executionSuccessful);

		} catch (SDBExecutionException e) {
			cleanTemporaryFile(tmpDbFile);
			throw new SDBExecutionException("Generic DB generation failed: " + e.getMessage(), e);
		} finally {
			closeConnection();
        }
		if (!executionSuccessful)	{
			throw new FlowCompletionException(SDBExecutionExitCodes.GENERIC_FLOW_EXECUTION_ERROR_WITH_KEEP_GOING);
		}
	}
	
	protected void closeDatabase(File tmpDbFile, boolean result) throws SDBExecutionException {
        //close the connection to free the temp file and delete the file
        closeConnection();
    
        if (result) {
            // Our newly created database is fNewDatabase.tmp and now that
            // everything is successful we want to
            // write it to be fNewDatabase, so we get rid of any old files of
            // that name first.
            if (outputDbFile.exists()) {
                outputDbFile.delete();
                logger.debug("The new file created is overwriting - " + outputDbFile.getPath());
            }
            
            // Finally, on success, we delete the tmp file and copy it over to
            // the proper filename
            copyFileToOutput(tmpDbFile);     
        } else {
        	logger.error("Errors encountered during the SDB execution. ");
            if (!outputDbFile.exists()) {
            	copyFileToOutput(tmpDbFile);
            } else {
            	logger.info("File " + outputDbFile.getName() + " already exists. Database file created in " + tmpDbFile.getName());
            }
        }
	}
	
	protected void closeConnection() {
		if (databaseManager.isConnectionOpen()) {
	        logger.info("Closing database...");
	        databaseManager.closeConnection();
		}
	}
	
	protected void cleanTemporaryFile(File tmpDbFile) {
        if (tmpDbFile != null && tmpDbFile.exists()) {
        	tmpDbFile.delete();
        }
	}
	
	private void copyFileToOutput(File tmpDbFile) throws SDBExecutionException {
        try{
            FileUtil.copy(tmpDbFile.getPath(), outputDbFile.getPath());

            if (inputDbFile != null && inputDbFile.getPath().equals(outputDbFile.getPath())) {
            	logger.info("Database " + outputDbFile.getName() + " updated");
            }
            else {
            	logger.info("Database " + outputDbFile.getName() + " created");
            }

            cleanTemporaryFile(tmpDbFile);
        } catch (IOException ex) {
            throw new SDBExecutionException("Failed to create file " + outputDbFile.getPath() + ": " + ex.getMessage(), ex);
        }  
	}

    public void setDatabaseManager(DBManager databaseManager) {
        this.databaseManager = databaseManager;
    }

	void setInputDbFile(File inputDbFile) {
		this.inputDbFile = inputDbFile;
	}
	
	public void setInputDatabaseValidator(DBValidator inputDatabaseValidator) {
		this.inputDatabaseValidator = inputDatabaseValidator;
	}
}
