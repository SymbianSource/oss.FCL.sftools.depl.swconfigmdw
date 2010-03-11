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

package com.symbian.sdb;

import org.apache.commons.cli2.OptionException;
import org.apache.log4j.Appender;
import org.apache.log4j.FileAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.xml.XmlBeanFactory;
import org.springframework.core.io.ClassPathResource;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.cmd.InvalidCmdArgumentException;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.mode.flow.WorkflowFactory;
import com.symbian.sdb.mode.flow.ced.FlowCompletionException;
import com.symbian.sdb.settings.Settings;

/**
 * main application class
 *
 */
public class Application {

    private WorkflowFactory workflowFactory;
    
    static private final Logger logger = Logger.getLogger(Application.class);
	public static final String SDB_VERSION = "2.2.2";
	private static boolean overwriteExistingLogFile = true;

    public void setWorkflowFactory(WorkflowFactory workflowFactory) {
        this.workflowFactory = workflowFactory;
    }

	public static void main(String[] args) {
	    Application sdbApplication = createSdbApplication();
	    sdbApplication.run(args);
	}

    private static Application createSdbApplication() {
        ClassPathResource resource = new ClassPathResource("applicationContext.xml");
        BeanFactory factory = new XmlBeanFactory(resource);
        Application sdbApplication = (Application) factory.getBean("sdbApplication"); 

        return sdbApplication;
    }

    private void run(String[] args) {
        int exitCode = 0;
        
        CmdLinev2 cmd = new CmdLinev2();
        try {
            if (cmd.parseArguments(args)) {
                new Settings().configure(cmd);  
                
                setupLogging(cmd);
                
                IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
                
                flow.validateOptions(cmd);
                
                flow.start(cmd);
                
            }
		} catch (InvalidCmdArgumentException ex) {
		    logger.error(ex.getMessage());
			logger.debug("Stack Trace:",ex);
			exitCode = 1;
			printLogFileLocationIfNecessary();
			cmd.printHelp();
		} catch (OptionException ex) {
		    logger.error(ex.getMessage());
			logger.debug("Stack Trace:",ex);
			exitCode = 1;
			printLogFileLocationIfNecessary();
			cmd.printHelp();
		} catch (SDBExecutionException ex) {
		    logger.error(ex.getMessage());
		    logger.debug("Stack Trace:",ex);
		    exitCode = 1;
		    printLogFileLocationIfNecessary();
		} catch (FlowCompletionException ex){
			exitCode = ex.getReturnCode();
			printLogFileLocationIfNecessary();
		} catch (Exception ex ) {
			logger.error(ex.getLocalizedMessage());
			logger.debug("Stack Trace:",ex);
			exitCode = 1;
			printLogFileLocationIfNecessary();
		} finally {
			cmd.printFinish();
		}
        System.exit(exitCode);
    }

    private static void printLogFileLocationIfNecessary() {
        if (logFileEnabled())  {
            logger.info("Log file created in " + Settings.SDBPROPS.log_file_path.getValue());    
        }
    }

    private static boolean logFileEnabled() {
        String logFileEnabled = Settings.SDBPROPS.log_file_enabled.getValue();
        return Boolean.valueOf(logFileEnabled);
    }
    
    private void setupLogging(CmdLineArgs cmd) throws SDBExecutionException {
        enableDebugModeIfNecessary(cmd);
        setupLogfileAppendMode();
    }

    private void setupLogfileAppendMode() throws SDBExecutionException {
        Appender appender = Logger.getRootLogger().getAppender("logfile");
        if (appender instanceof FileAppender) {
            FileAppender logfileAppender = (FileAppender) appender; 
            logfileAppender.setAppend(!overwriteExistingLogFile);
        }
        else    {
           throw new SDBExecutionException("log4j Appender 'logfile' is not of expected type - FileAppender, but "); 
        }
    }

    private void enableDebugModeIfNecessary(CmdLineArgs cmd) {
        if(cmd.isDebugEnabled()){
            Logger sdbLogger = Logger.getLogger("com.symbian.sdb");
            sdbLogger.setLevel(Level.DEBUG);
        }
    }
}


