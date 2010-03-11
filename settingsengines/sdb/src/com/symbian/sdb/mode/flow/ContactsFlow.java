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
import java.io.InputStreamReader;
import java.sql.SQLException;
import java.util.List;
import java.util.Set;

import org.apache.log4j.Logger;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.model.Preferences;
import com.symbian.sdb.contacts.model.PreferencesManager;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.template.ITemplateManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateManager;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.flow.ced.FlowCompletionException;
import com.symbian.sdb.mode.flow.ced.SDBExecutionExitCodes;
/**
 * The flow for the creation of the contacts databases
 */
public class ContactsFlow extends GenericFlow implements IFlow {
	
	private static final Logger logger = Logger.getLogger(ContactsFlow.class);
	private List<File> vcardFiles;
	private File contactTemplate;
	private ITemplateManager abstractTemplateManager = null;
	private ITemplateManager dbmsTemplateManager;      //injected bean variable
	private ITemplateManager sqliteTemplateManager;    //injected bean variable
	
	private IContactsManager abstractContactsManager = null;
	private IContactsManager dbmsContactsManager;      //injected bean variable
	private IContactsManager sqliteContactsManager;    //injected bean variable
	
	private PreferencesManager preferencesManager; 
	
	private final String CONTACTS_UID = "100065FF";
	private Preferences preferences;
	private TemplateMapper contactsMapper;
	
	private SpeedDialMode speedDialMode;
	private SpeedDialManager speedDialManager;  
	
    public ContactsFlow() {
        super();
        dbmsTemplateManager = new TemplateManager();
    }
 
    /* (non-Javadoc)
	 * @see com.symbian.sdb.mode.flow.IFlow#validateOptions(com.symbian.sdb.cmd.CmdLineArgs)
	 */    
	public void validateOptions(CmdLineArgs cmd) throws SDBValidationException {
		super.validateOptions(cmd);
		
		vcardFiles = cmd.getvCardFiles();

        contactTemplate = cmd.getTemplateFile();
        
        if (contactTemplate != null){
        	if (!contactTemplate.exists()){
        		throw new SDBValidationException("Template file does not exist: "+contactTemplate.getAbsolutePath());
        	}
        	else if (!contactTemplate.isFile()) {
        		throw new SDBValidationException("Template is not a valid file: "+contactTemplate.getAbsolutePath());
        	}
        }
        
		if (update) {	
	        if (vcardFiles.size() == 0) {
	            throw new SDBValidationException("At least one vCard input file must be specified for the contacts mode if an input database is provided."); 
	        }		
		} else {
			if (contactTemplate == null) {
	            throw new SDBValidationException("A template must be provided when creating a new contacts database."); 
			}		
		}
		
		if (cmd.isSpeedDialGenerationEnabled()) {
			if (cmd.getSpeedDialFile().exists()) {
				this.speedDialMode = new SpeedDialMode(SpeedDialModeType.UPDATE, cmd.getSpeedDialFile());
			} else {
				this.speedDialMode = new SpeedDialMode(SpeedDialModeType.CREATE, cmd.getSpeedDialFile());
			}
			if (null == cmd.getDeploymentDbLocation() || cmd.getDeploymentDbLocation().length() < 1)	{
				throw new SDBValidationException("No deplyment DB location was specified! '-a' option is required in speed dial mode.");
			}
			else	{
				speedDialManager.setDeploymentDbLocation(cmd.getDeploymentDbLocation());
			}
		} else {
			this.speedDialMode = new SpeedDialMode(SpeedDialModeType.NONE, null);
		}
		speedDialManager.setMode(this.speedDialMode.getSpeediDialModeType());
	}
	
	public void start(CmdLineArgs cmd) throws SDBExecutionException {
		logger.info("Contacts started");
		
		// This is the file we will work on
		File tmpDbFile = null;
		try {
			tmpDbFile = tryToExecuteContactsFlow(cmd);
            
		} catch (SDBExecutionException e) {
			cleanTemporaryFile(tmpDbFile);
			throw new SDBExecutionException("Contacts DB generation failed: " + e.getMessage());
		} finally {
			closeConnection();
        }
		
	}

    private File tryToExecuteContactsFlow(CmdLineArgs cmd) throws SDBExecutionException {
        try {
            return executeContactsFlow(cmd);    
        } catch (SystemException e) {
            throw new SDBExecutionException(e);
        }
    }

    private File executeContactsFlow(CmdLineArgs cmd) throws SDBExecutionException {
         File tmpDbFile = prepareTemporaryFile();
        
        // This applies the default value for the UID if the contacts flow is in use
        // If the value is specified in the DB configuration then the value will have 
        // been set
        //
        if(DbOptions.SECURE_ID.getValue() == null){
        	try {
        		DbOptions.SECURE_ID.setValue(CONTACTS_UID );
        	} catch (SDBValidationException e) {
        		throw new SDBExecutionException("Problem occured while setting the default DB UID.", e);
        	}
        }
        
        boolean executionSuccessful = openAndConfigureDatabase(tmpDbFile);
           
        // here starts contacts mode
        
        wireDatabaseSpecificBeans();
        
        this.validateInputDB();
        
        contactsMapper = TemplateMapper.getInstance();
        
        
            try {
            	if(!update){
            		logger.info("Applying contacts schema...");
            		executionSuccessful &= sqlExecuter.executeSql(new InputStreamReader(dbType.getContactsSchema()),
            				databaseManager.getConnection(), failFast);
            	}            
            } catch (SQLException e) {
            	throw new SDBExecutionException("Problem applying SQL to DB.", e);
            } 
        
        preferences = preferencesManager.initPreferences(databaseManager, dbType, configuration, contactsMapper);
        
        ITemplateModel templateModel = null;
        
        try {
        	templateModel = getTemplateModel();
        } catch (TemplateParsingException ex) {
        	throw new SDBExecutionException("Error while parsing template "+contactTemplate.getAbsolutePath()+": "+ex.getLocalizedMessage(), ex);
        }
        
        Group group = null;

        if (cmd.getGroup() != null){
        	group = new Group(cmd.getGroup());
        }
//    	speedDialManager.getCurrentTempEntry().setSpeedDialNumber(speedDialMode.getSpeedDialNumber());

        importAndSaveContacts(templateModel, group);

        try {
        	preferences.persistToDb(databaseManager);
        } catch (Exception e) {
        	throw new SDBExecutionException("Could not store preferences table values", e);
        }
        // here ends contacts mode
        
        executionSuccessful &= applyUserSql();

        closeDatabase(tmpDbFile, executionSuccessful);
        
		if (!speedDialMode.isNone())	{
        	generateSpeedDialIni();
        }

		if (!executionSuccessful)	{
			throw new FlowCompletionException(SDBExecutionExitCodes.GENERIC_FLOW_EXECUTION_ERROR_WITH_KEEP_GOING);
		}

        return tmpDbFile;
    }

	/**
	 */
	private void generateSpeedDialIni() {
		if (speedDialMode.getSpeediDialModeType().equals(SpeedDialModeType.CREATE))	{
    		speedDialManager.createSpeedDialIniFile(speedDialMode.getSpeedDialIniFile());
        } else if (speedDialMode.getSpeediDialModeType().equals(SpeedDialModeType.UPDATE))	{
        	speedDialManager.updateSpeedDialIniFile(speedDialMode.getSpeedDialIniFile());
        }
	}

	private void importAndSaveContacts(ITemplateModel templateModel, Group group) {
		Set<Contact> contacts = abstractContactsManager.importContacts(vcardFiles, templateModel);
		abstractContactsManager.assignGroupsToContacts(group,contacts);
		abstractContactsManager.persistContacts(contacts, templateModel);
	}
	
    private ITemplateModel getTemplateModel() throws SDBExecutionException, TemplateParsingException {
    	
    	ITemplateModel templateModel = null;
    	if (contactTemplate != null) { //resource file was provided on the command line
        	logger.info("Parsing resource file " + contactTemplate.getName());
            templateModel = abstractTemplateManager.parse(contactTemplate.getAbsolutePath());

            //Persist template in database
    		abstractTemplateManager.persistTemplate(templateModel);
    	} else if (inputDbFile != null) { //resource file not provided, template has to be read from existing database 
    		logger.info("Reading the system template model from the database...");
    		templateModel = abstractTemplateManager.read();
    	}

        return templateModel;
    }
    
    private void wireDatabaseSpecificBeans() {
        if (dbType.equals(DBType.DBMS)) {
            this.abstractTemplateManager = this.dbmsTemplateManager;
            this.abstractContactsManager = this.dbmsContactsManager;
        } else if(dbType.equals(DBType.SQLITE)) {
            this.abstractTemplateManager = this.sqliteTemplateManager;
            this.abstractContactsManager = this.sqliteContactsManager;
        }
        this.inputDatabaseValidator.setContactsDbValidator(this.abstractContactsManager);
    }

    
    // Setters and getters
    
    public void setDbmsTemplateManager(ITemplateManager dbmsTemplateManager) {
        this.dbmsTemplateManager = dbmsTemplateManager;
    }

    public void setSqliteTemplateManager(ITemplateManager sqliteTemplateManager) {
        this.sqliteTemplateManager = sqliteTemplateManager;
    }

    public void setDbmsContactsManager(IContactsManager dbmsContactsManager) {
        this.dbmsContactsManager = dbmsContactsManager;
    }

    public void setSqliteContactsManager(IContactsManager sqliteContactsManager) {
        this.sqliteContactsManager = sqliteContactsManager;
    }

    public void setPreferencesManager(PreferencesManager preferencesManager) {
        this.preferencesManager = preferencesManager;
    }
    
	public void setInputDatabaseValidator(DBValidator inputDatabaseValidator) {
		this.inputDatabaseValidator = inputDatabaseValidator;
	}

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}
}
