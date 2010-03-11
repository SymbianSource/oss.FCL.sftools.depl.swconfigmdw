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

package com.symbian.sdb.cmd;

import java.io.File;
import java.net.URISyntaxException;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;
import java.util.Locale;
import java.util.ResourceBundle;

import org.apache.commons.cli2.CommandLine;
import org.apache.commons.cli2.Group;
import org.apache.commons.cli2.Option;
import org.apache.commons.cli2.OptionException;
import org.apache.commons.cli2.builder.ArgumentBuilder;
import org.apache.commons.cli2.builder.DefaultOptionBuilder;
import org.apache.commons.cli2.builder.GroupBuilder;
import org.apache.commons.cli2.commandline.Parser;
import org.apache.commons.cli2.util.HelpFormatter;
import org.apache.commons.cli2.validation.FileValidator;
import org.apache.commons.cli2.validation.NumberValidator;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;

import com.symbian.sdb.Application;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.mode.IModeParser;
import com.symbian.sdb.mode.ModeParser;
import com.symbian.sdb.settings.Settings;

/**
 * Instance of the CmdLine interface, wrapping the apache commons cli v2.0 library
 */
public class CmdLinev2 implements CmdLine, CmdLineArgs {
	
	private static final Logger logger = Logger.getLogger(CmdLinev2.class);
	
	private HelpFormatter helpFormatter = new HelpFormatter();
	private CommandLine cmdLine;
	private Group options;
	
	private Option help, version, list, debug;
	private Option mode, input, output, config;
	private Option keepgoing;
	private Option group;
	private Option files;
	private Option template;
	private Option properties;
	private Option speedDialFile;
	private Option deploymnetDbLocation;
	
	private List<File> sqlFiles;
	private List<File> vCardFiles;
	private List<File> cedFiles;
	    
    /** resource bundle */
    private ResourceBundle bundle;
	
    /**
     * initialises options and help for the command line 
     */
	public CmdLinev2() {
		bundle = ResourceBundle.getBundle("arguments", Locale.getDefault(), getClass().getClassLoader());
		helpFormatter.setShellCommand(bundle.getString("shell_command"));
		String line = new MessageFormat(bundle.getString("start_line"))
								.format(new Object[] {Application.SDB_VERSION});
		helpFormatter.setHeader(line);

		createOptions();
		
		GroupBuilder gbuilder = new GroupBuilder();
		
		gbuilder
			.withName("Options:")				
			.withOption(help)
			.withOption(list)
			.withOption(version)
			.withOption(keepgoing)
			.withOption(debug)
			.withOption(mode)
			.withOption(input)
			.withOption(config)
			.withOption(output)
			.withOption(properties)
			.withOption(files);
		
		if(Settings.isContactsEnabled()){
			//contacts specific
			gbuilder
				.withOption(group)
				.withOption(template);
			if (Settings.isContactsSpeedDialEnabled()) {
				gbuilder
					.withOption(speedDialFile)
					.withOption(deploymnetDbLocation);
			}
		}
		
		options = gbuilder.create();
		helpFormatter.setGroup(options);
	}
	
	private void createOptions() {
		DefaultOptionBuilder obuilder = new DefaultOptionBuilder();
		ArgumentBuilder abuilder = new ArgumentBuilder();

		help = obuilder
		    .withShortName("h")
			.withLongName("help")
			.withDescription("Display this help message and exit.")
			.create();
		
		version = obuilder
			.withShortName("v")
		    .withLongName("version")
		    .withDescription("Display the tool version number and exit.")
			.create();
	
		debug = obuilder
			.withShortName("d")
			.withLongName("debug")
			.withDescription("Increases logging detail level. Sets the logging output mode to debug.")
			.create();
		
		list = obuilder
		    .withShortName("l")
		    .withLongName("list-modes")
			.withDescription("List all available modes of operation and expected input files.")
			.create();

		properties = obuilder
		    .withShortName("p")
		    .withLongName("properties")
			.withDescription("Set the custom SDB properties.")
			.withArgument(
					abuilder.withName("filename")
					.withDefault(getDefaultPropertiesFileName())
					.withMinimum(0)
					.withMaximum(1)
					.withValidator(InputFileValidator.getInstanceForFilesWhichMustExist())
					.create())
			.create();
		
		mode = obuilder
		        .withShortName("m")
		        .withLongName("mode")
				.withDescription("Mode of operation defines output database file type and schema. (see --list-modes).")
				.withArgument(
						abuilder.withName("mode value")
								.withMinimum(1)
								.withMaximum(1)
								.withDefault(new ModeParser("sqlite"))
								.withValidator(new ModeValidator())
								.create())
				.create();
		

		input = obuilder
				.withShortName("i")
				.withLongName("input")
				.withDescription("Input database file name. \nUpdates (a copy of) this database.")
				.withArgument(
						abuilder.withName("filename")
								.withMinimum(1)
								.withMaximum(1)
								.withValidator(InputFileValidator.getInstance())
								.create())
				.create();
		
		config = obuilder
		            .withShortName("c")
		            .withLongName("config")
					.withDescription("Configuration XML file. \nContains settings for the format and content of generated files.")
					.withArgument(
							abuilder.withName("filename")
									.withMinimum(1)
									.withMaximum(1)
									.withValidator(InputFileValidator.getInstanceForFilesWhichMustExist())
									.create())
					.create();
		
		output = obuilder
		        .withShortName("o")
		        .withLongName("output")
		        .withDescription("Output database file name and location.")
				.withArgument(
						abuilder.withName("filename")
								.withMinimum(1)
								.withMaximum(1)
								.withValidator(InputFileValidator.getInstance())
								.create())
				.create();

		String fileDescription = "List of SQL files. May contain wildcards (? and *).";
		if(Boolean.valueOf(Settings.SDBPROPS.contacts_enabled.getValue())){
			fileDescription = "List of SQL or vCards files. May contain wildcards (? and *).";
		}
		files = abuilder
					.withName("file")
					.withValidator(InputFileValidator.getInstanceForPathsWithWildcardSupport())
					.withDescription(fileDescription)
					.create();
		
		group = obuilder
		        .withShortName("g")
		        .withLongName("group")
		        .withDescription("Group for contacts.")
		        .withArgument(
	                   abuilder.withName("group name")
                          .withMinimum(1)
                          .withMaximum(1)
                          .create())
                .create();

		template = obuilder
		        .withShortName("t")
		        .withLongName("template")
		        .withDescription("Resource file containing template mapping applicable to input vCards, for contacts DB.")  //TODO maybe think of a better description
				.withArgument(
						abuilder.withName("filename")
								.withMinimum(1)
								.withMaximum(1)
								.withValidator(InputFileValidator.getInstance())
								.create())
		        .create();
		
		keepgoing = obuilder
				.withShortName("k")
				.withLongName("keep-going")
				.withDescription("SQL or CED execution errors during database creation are ignored")
				.create();
		
		NumberValidator speedDialKeyDigitValidator = NumberValidator.getIntegerInstance();
		speedDialKeyDigitValidator.setMinimum(1);
		speedDialKeyDigitValidator.setMaximum(9);

		speedDialFile = obuilder
        					.withShortName("s")
        					.withLongName("speedDialIniFile")
        					.withDescription("Speed Dial INI file, if this file exists it will be updated otherwise new file will be created i.e. CntModel.ini")
        					.withArgument(
        							abuilder.withName("filename")
        									.withMinimum(1)
        									.withMaximum(1)
        									.withValidator(new FileValidator())
        									.withDefault(new File("speeddial.ini"))
        									.create())
        					.create();
		
		deploymnetDbLocation = obuilder
							.withShortName("a")
							.withLongName("deviceDbLocation")
							.withDescription("Location of Contacts database in deployment environment i.e. c:contacts.cdb.")
							.withArgument(
									abuilder.withName("filename")
											.withDefault("")		
											.withMinimum(1)
											.withMaximum(1)
											.create())
							.create();
	}
	
	/**
	 * @return true if arguments indicate a command flow is required. False if the tool can exit successfully.
	 */
	public boolean parseArguments(String[] args) throws OptionException {
		Parser parser = new Parser();
		parser.setHelpFormatter(helpFormatter);
		parser.setGroup(options);
		cmdLine = parser.parse(args);
		
		boolean result = true;
		
		if (isDebugEnabled()) {
			Logger.getRootLogger().setLevel(Level.DEBUG);
		}
		if (cmdLine.hasOption(version)) {
			printVersion();
			return false;
		}
		
		helpFormatter.printHeader();
		if (cmdLine.hasOption(help) || !hasImplicitMode(cmdLine)) {
			helpFormatter.printUsage();
			helpFormatter.printWrapped(" ");
			helpFormatter.printHelp();
			helpFormatter.getPrintWriter().flush();
			result = false;
		} 
			
		if (cmdLine.hasOption(list)) {
			printModes();
			result = false;
		}
		
		return result;
	}
	
	/**
	 * Determines whether the command line parser can determine the required mode
	 * even when no mode is specified.
	 * @param cmdLine the parsed command line
	 * @return true if the specified options are enough to determine the mode.
	 * Returns false elsewhere and if options specified override any other options, for example help and list.
	 */
	private boolean hasImplicitMode(CommandLine cmdLine) {
		// TODO: this list may need refining - at the moment everything is there, but can we really create a DB
		// 		 with just an input DB etc?
		//
		return 	cmdLine.hasOption(help) ||
				cmdLine.hasOption(list) ||
				cmdLine.hasOption(mode) ||
				cmdLine.hasOption(group) ||
				cmdLine.hasOption(output) ||
				cmdLine.hasOption(config) ||
				cmdLine.hasOption(input) ||
				cmdLine.hasOption(template) ||
				getvCardFiles().size()>0 ||
				getSQLFiles().size()>0; 
	}

	public File getConfigurationFile() {
		return (File)cmdLine.getValue(config);
	}
	
	public File getOutputDb() {
		return (File)cmdLine.getValue(output);
	}
	
	public File getInputDb() {
		return (File)cmdLine.getValue(input);
	}
	
	@SuppressWarnings("unchecked")
	private List<File> getInputFiles() {
		return (List<File>)cmdLine.getValues(files);
	}

    public List<File> getSQLFiles() {
        if (sqlFiles == null) {
            List<File> inputFiles = getInputFiles();
            sqlFiles = new ArrayList<File>();
            for (final ListIterator<File> i = inputFiles.listIterator(); i.hasNext();) {
                File file = i.next();
                String filename = file.getName();
                if (!filename.endsWith(".xml") 
                        && !filename.endsWith(".vcf") 
                        && !filename.endsWith(".vcard")
                        && !filename.endsWith(".cfg")) {
                    sqlFiles.add(file);
                }
            }
        }
        return sqlFiles;
    }
    
    public List<File> getvCardFiles() {
        if (vCardFiles == null) {
            List<File> inputFiles = getInputFiles();
            vCardFiles = new ArrayList<File>();
            for (final ListIterator<File> i = inputFiles.listIterator(); i.hasNext();) {
                File file = i.next();
                
                if (file.exists() && file.isFile() ) {
                    String filename = file.getName();
                    if (filename.endsWith(".vcf") || filename.endsWith(".vcard")) {
                        vCardFiles.add(file);
                    }
                }               
            }
        }
        return vCardFiles;
    }
    
    public List<File> getCedFiles() {
        if (cedFiles == null) {
            List<File> inputFiles = getInputFiles();
            cedFiles = new ArrayList<File>();
            for (final ListIterator<File> i = inputFiles.listIterator(); i.hasNext();) {
                File file = i.next();
                if (file.exists() && file.isFile() ) {
                    String filename = file.getName();
                    if (filename.endsWith(".cfg") || filename.endsWith(".xml")) {
                        cedFiles.add(file);
                    }
                }
            }
        }
        return cedFiles;
    }

	public File getTemplateFile() {
		return (File)cmdLine.getValue(template);
	}
    
	public File getPropertiesFile() {
		return new File((String) cmdLine.getValue(properties));
	}
	
	public IModeParser getMode() {
		return (IModeParser)cmdLine.getValue(mode);
	}
	
	public String getGroup() {
	    return (String)cmdLine.getValue(group);
	}
	
	public void printModes() {
		StringBuilder modesBuilder = new StringBuilder();
		modesBuilder.append(bundle.getString("generic_modes"));

		if(Settings.isContactsEnabled()){
			modesBuilder.append(bundle.getString("contacts_modes"));
		}
		
		modesBuilder.append(bundle.getString("ced_mode"));
		
		modesBuilder.append(bundle.getString("list_generic_options"));
		if(Settings.isContactsEnabled()){
			modesBuilder.append(bundle.getString("list_contacts_options"));
			if (Settings.isContactsSpeedDialEnabled()) {
				modesBuilder.append(bundle.getString("list_speeddial_options"));
			}
		}
		modesBuilder.append(bundle.getString("list_generic_input_files"));
		
		if(Settings.isContactsEnabled()){
			modesBuilder.append(bundle.getString("list_contacts_input_files"));
		}
		
		modesBuilder.append(bundle.getString("list_ced_input_files"));
		
		helpFormatter.printWrapped(modesBuilder.toString());
	}
	
	public boolean failFast() {
		return !cmdLine.hasOption(keepgoing);
	}
	
	public void printHelp() {
	//	if (ex != null) {
	//		helpFormatter.setException(ex);
	//		helpFormatter.printException();
	//	}
		helpFormatter.printUsage();
	//	helpFormatter.setException(null);
		helpFormatter.printHelp();
		//have to flush as HelpFormatter.printHelp doesn't do it
		helpFormatter.getPrintWriter().flush();
	}
		
	public void printHeader() {
		helpFormatter.printHeader();
	}
	
	public void printFinish() {
		helpFormatter.printFooter();
	}
	
	public void printVersion() {
		helpFormatter.printWrapped("SDB " + Application.SDB_VERSION);
	}
	
	  private File getClassLocation() {
		try {
			File classLocation = new File(
					getClass()
							.getProtectionDomain()
							.getCodeSource()
							.getLocation()
							.toURI());
			return classLocation;
		} catch (URISyntaxException ex) {
			logger.warn("warning: Installation directory not recognized. Default values used.");
			throw new SystemException(ex.getMessage(),ex);
		}
	}
	  
	public File getInstallationDirectory() {
		File sdbJarFile = getClassLocation();
		File parentDirectory = sdbJarFile.getParentFile();
		if (parentDirectory.getName().equals("lib")) {
			// need to go two folders up: sdb-creator/lib
			parentDirectory = parentDirectory.getParentFile().getParentFile();
		} else if (parentDirectory.getName().equals("target")) {
			parentDirectory = parentDirectory.getParentFile();
		}
		return parentDirectory;
	}
	
	public String getDefaultPropertiesFileName() {
		File path = getClassLocation();
		String propertiesFileName = null;
		if (path.getParentFile().getName().equals("lib")) {
			propertiesFileName = path.getParentFile().getAbsolutePath().replace("lib", "config"+File.separator+"sdb.properties");
		}
		if (null == propertiesFileName){
			propertiesFileName = "config"+File.separator+"sdb.properties";	
		}
		return propertiesFileName;
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.cmd.CmdLineArgs#isDebugEnbabled()
	 */
	public boolean isDebugEnabled() {
		return cmdLine.hasOption(debug);
	}

	public boolean isSpeedDialGenerationEnabled() {
		return cmdLine.hasOption(speedDialFile);
	}

	public File getSpeedDialFile() {
		return (File)cmdLine.getValue(speedDialFile);
	}
	
	public String getDeploymentDbLocation() {
		return (String)cmdLine.getValue(deploymnetDbLocation);
	}

}
