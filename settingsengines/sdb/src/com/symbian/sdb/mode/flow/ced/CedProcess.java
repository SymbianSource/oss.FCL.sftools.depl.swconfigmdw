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

package com.symbian.sdb.mode.flow.ced;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;

import com.symbian.sdb.util.FileUtil;
import com.symbian.sdb.util.ProcessBuilderFactory;

class CedProcess implements ICedProcess {

	private static final Logger logger = Logger.getLogger(CedProcess.class);
	
	/**
	 * The list of command options/values to provide input to the process 
	 */
	private final List<String> command;
	
	/**
	 * The schema instance representing the desired output
	 */
	private CedSchema _schema;
	
	/**
	 * 
	 * @param schema instance representing the desired output
	 */
	public CedProcess(CedSchema schema) {
		_schema = schema;

		command = new ArrayList<String>();
		command.add(_schema.getExeDirectory().getAbsolutePath() + File.separator + _schema.getExeName());
		// Currently required to set the -b property for the target os but this seems pointless
		// The tool will not work without it.
		//
		command.add("-b");
		command.add(schema.getShortFormOSVersion());
	}
	
	/**
	 *	Executes the relevant CED command and pipes output to the logger
	 *  @throws SdbFlowException if an error occurs creating or executing the process
	 */
	public void start() throws SdbFlowException{
		IProcessBuilder pb = ProcessBuilderFactory.getProcessBuilder(command);
		
		pb.directory(_schema.getExeDirectory());
		
		try {

			logger.debug("Executing Process:"+pb.directory().getAbsolutePath()+" "+getDisplayableCommand(command));
			Process process = pb.start();

			CedOutputProcessor outputProcessor = new CedOutputProcessorImpl();
			redirectProcessOuput(process, outputProcessor);
			
			int retCode = process.waitFor(); 

			if(retCode!=0){
				logger.error("CED process completed with an error (" + retCode + ").");
				logger.info("Check debug log for full CED output details.");
			}
			
			if(outputProcessor.hasErrorSummary()){
				logger.info("Error summary:");
				outputProcessor.printErrorSummary(Level.ERROR);
			}
					
			if(outputProcessor.hasWarningSummary()){
				logger.info("Warning summary:");
				outputProcessor.printWarningSummary(Level.WARN);
			}
			
			logger.info("CED process completed");
			
			if(retCode!=0){
				throw new CedFlowCompletionException(retCode);
			}
			
		} catch (IOException e) {
			throw new SdbFlowException("Problem encountered when executing the CED command: "
											+getDisplayableCommand(command)
										+  " from "+pb.directory().getAbsolutePath()
										+". Due to: "+e.getLocalizedMessage(), e);
		} catch (InterruptedException e) {
			throw new SdbFlowException("CED process interrupted: "+e.getLocalizedMessage(), e);
		}
	}
	
	/**
	 * Add option/values to the command to be executed
	 * @param String... options and/or values to add to command execution
	 */
	public void addOptions(String... strings) {
		for(String s: strings){
			command.add(s);
		}
	}
	
	/**
	 * @param process the running process which output to be redirect
	 * @param outputProcessor used to process the CED output into SDB output and to catch errors
	 * @throws IOException if problem reading and writing streams
	 */
	private void redirectProcessOuput(Process process, CedOutputProcessor outputProcessor) throws IOException {
		redirect(process.getInputStream(), outputProcessor, Level.DEBUG);
	}

	/**
	 * @param inputStream to be redirected to the logger
	 * @param outputProcessor used to process the CED output into SDB output and to catch errors
	 * @param logLevel the log level at which the output should be tagged
	 */
	private void redirect(InputStream inputStream, CedOutputProcessor outputProcessor, Level logLevel) throws IOException{
		if(inputStream != null){
			String line;
			BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
			int logLineNumber = 0;
			while ((line = reader.readLine()) != null) {
				logLineNumber++;
				logger.log(logLevel, logLineNumber+": "+outputProcessor.process(line, logLineNumber));
			}
			FileUtil.closeSilently(reader);
		}
	}

	/**
	 * Util method to generate readable command from command list
	 * @param commandList containing each option/value
	 * @return the readable command
	 */
	private String getDisplayableCommand(List<String> commandList){
		StringBuilder retStr = new StringBuilder();
		for(String commandParam: commandList){
			retStr.append(commandParam).append(" ");
		}
		return retStr.toString();
	}
}
