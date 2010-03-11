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
import java.util.List;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.ced.CEDProcessFactory;
import com.symbian.sdb.mode.flow.ced.CedSchema;
import com.symbian.sdb.mode.flow.ced.FlowCompletionException;
import com.symbian.sdb.mode.flow.ced.ICedProcess;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;
import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.FileUtil;

/**
 * The flow for the creation of the CommsDat databases
 */
public class CedFlow implements IFlow {

	//TODO Should we read it from setting file ?
	private static final String CED_DB_NAME = "cccccc00.cre";
	private static final String CED_LOG_NAME = "ced.log";

	private static final Logger logger = Logger.getLogger(CedFlow.class);
	
	private String getListString(List<File> files) {
	    StringBuilder builder = new StringBuilder();
	    for (File file : files) {
	        builder.append(file.getName());
	        builder.append(" ");
	    }
	    return builder.toString();
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.mode.flow.IFlow#validateOptions(com.symbian.sdb.cmd.CmdLineArgs)
	 */
	public void validateOptions(CmdLineArgs cmd) throws SDBValidationException {
	    List<File> files = cmd.getCedFiles();
	    if (files.size() > 1) {
	        throw new SDBValidationException("Only one input configuration file allowed: " + getListString(files));
	    }
	    
	    if (files.size() == 0) {
	        throw new SDBValidationException("Configuration file is required as the tool input.");
	    }
	    
	    if (cmd.getvCardFiles().size() > 0) {
	        logger.warn("Warning: vCard files are not the correct input for CommsDat creation - ignoring: " + getListString(cmd.getvCardFiles()));
	    }
	    
	    if (cmd.getSQLFiles().size() > 0) {
	        logger.warn("Warning: unrecognized input files - ignoring: " + getListString(cmd.getSQLFiles()));
	    }

	    if (cmd.getTemplateFile() != null) {
	        logger.warn("Warning: tempate files are not valid input for CommsDat creation - ignoring: " + getListString(cmd.getSQLFiles()));
	    }
	}

	/**
	 *  Runs the CED command given the input values.
	 */
	public void start(final CmdLineArgs cmd) throws SdbFlowException{
		
		try {
		    logger.info("CED mode started");
			// Determine the Ced Schema
			//
			CedSchema schema = CedSchema.getSchema(cmd.getMode().getDbSchema());
			
			// Get the specific process
			//
			final ICedProcess process = CEDProcessFactory.getProcess(schema);

			// Always run CED in validating mode so that it doesn't report a success when something goes wrong
			process.addOptions("-v");
			
			//cleanup old CED database
			cleanupLastCedOutput(schema);
			
			
			// Setup the ced command line parameters and environment
			//
			if (isUsingExistingDB(cmd)) {
				process.addOptions("-a");
				
				// Copy the input DB to the location ced looks for the DB to update
				//
				FileUtil.copy(	cmd.getInputDb().getAbsolutePath(),
								FileUtil.concatFilePath(schema.getExeDirectory().getAbsolutePath(),CED_DB_NAME));
			}

			if (isInDebugMode(cmd)){
				process.addOptions("-d");
			}
			
			if (isInKeepGoingMode() || cmd.failFast()){
				process.addOptions("-f");
			}
			
			// The input file is the xml/cfg file containing the comms settings
			//
			process.addOptions("-i", getConfigFile(cmd));
			
			// Execute the process
			//
			try {
				process.start();
			} catch (FlowCompletionException flowException) {
				File cedOutputFile = new File(FileUtil.concatFilePath(schema.getExeDirectory().getAbsolutePath(), CED_DB_NAME));
				if(cedOutputFile.exists()) {
					String outputDBTarget = getErroredOutputDbFileName(cmd);
					FileUtil.copy(cedOutputFile.toString(), outputDBTarget);
					logger.info("Generated DB with errors: "+outputDBTarget);
				}
				throw flowException;
			}

			// If the output DB is specified then we need to copy the DB created by CED to the output location
			//
			FileUtil.copy( FileUtil.concatFilePath(schema.getExeDirectory().getAbsolutePath(), CED_DB_NAME),
								getOutputDbFile(cmd).getAbsolutePath());

			logger.info("Generated DB: "+getOutputDbFile(cmd).getAbsolutePath());
		} catch (IOException e) {
			throw new SdbFlowException(
					"Problem while executing Ced Flow: "+e.getLocalizedMessage(),
					e);
		}
	}
	
	private String getErroredOutputDbFileName(CmdLineArgs cmd) {
	  String outputDbPath = getOutputDbFile(cmd).getAbsolutePath();
	  int fileNamePosition = outputDbPath.lastIndexOf('.');
	  String fileExtention = "";
	  if(fileNamePosition > -1) {
		 fileExtention = outputDbPath.substring(fileNamePosition);
		 outputDbPath = outputDbPath.substring(0, fileNamePosition);
	  }
	  return outputDbPath + "_err" + fileExtention;
	}
	
	private void cleanupLastCedOutput(CedSchema schema) throws IOException {
		 
		deleteCedOutputDbFile(schema);
		deleteCedLogFile(schema);
	}

	private void deleteCedLogFile(CedSchema schema)
									throws IOException {
		deleteCedFile(schema, CED_LOG_NAME);
	}

	private void deleteCedOutputDbFile(CedSchema schema) 
									throws IOException {
		deleteCedFile(schema, CED_DB_NAME);
	}
	
	private void deleteCedFile(CedSchema schema, String fileName)
									throws IOException {
		File cedFile = new File(FileUtil.concatFilePath(schema.getExeDirectory().getAbsolutePath(), fileName));
		if(cedFile.exists()) {
			if(!cedFile.delete()) {
				throw new IOException("Can't delete file: " + cedFile.getName());
			}
		}
	}	
	/**
	 * 
	 * @param cmd
	 * @return
	 */
	public File getOutputDbFile(CmdLineArgs cmd) {
		if(cmd.getOutputDb() == null){
			return new File(Settings.SDBPROPS.ced_default_output.getValue());
		}
		return cmd.getOutputDb();
	}

	/**
	 * 
	 * @param cmd the command input
	 * @return the single file to be used as input to the CED tool 
	 */
	private String getConfigFile(final CmdLineArgs cmd) {
		return cmd.getCedFiles().get(0).getAbsolutePath();
	}
	
	/**
	 * @return true if the CED process should keep going on error
	 */
	private boolean isInKeepGoingMode() {
		return Boolean.getBoolean("sdb.ced.keepgoing");
	}

	/**
	 * @return true if the output should be debug
	 */
	private boolean isInDebugMode(final CmdLineArgs cmd) {
		return Logger.getRootLogger().getLevel().isGreaterOrEqual(Level.DEBUG);
	}

	/**
	 * @return true if an existing DB should be updated
	 */
	private boolean isUsingExistingDB(final CmdLineArgs cmd) {
		return cmd.getInputDb() != null;
	}
}
