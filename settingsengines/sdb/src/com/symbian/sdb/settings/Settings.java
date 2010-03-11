// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.settings;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import org.apache.log4j.Logger;

import com.symbian.sdb.cmd.CmdLineArgs;
import com.symbian.sdb.util.FileUtil;

public class Settings extends Properties {

	public enum SDBPROPS {
	    log_file_enabled("sdb.log.file.enabled", "FALSE"),
		log_file_format("sdb.log.file.format","%-5p [%-20.20C{1}] %-8r %4L - %m%n"),
		log_file_path("sdb.log.file.path","logs\\sdb.log"),
		log_file_level("sdb.log.file.level","INFO"),

		log_console_format("sdb.log.console.format", "%m%n"),
		log_console_level("sdb.log.console.level", "INFO"),

		dbname("sdb.dbname", "sdb.db"),

		sqlite_lib_path("org.sqlite.lib.path", "lib/"),
		dbms_lib_path("com.symbian.dbms.lib.path", "lib/"),
		
		contacts_configuration("sdb.contacts.configuration", "config/contacts.xml"),
		contacts_configuration_locale("sdb.contacts.configuration.locale", "config/contacts_locale_en_gb.xml"),
		
		contacts_schema_sqlite("sdb.contacts.schema.sqlite", "schema_data.sql"),
		contacts_schema_dbms("sdb.contacts.schema.dbms", "schema_data_dbms.sql"),
		
		old_schema_location("sdb.schema.location.1.0", "sdb.xsd"),
		schema_location("sdb.schema.location.2.0", "sdb2.0.xsd"),

		contacts_enabled("sdb.contacts.enabled", "true"), 
		speeddial_enabled("sdb.contacts.speeddial.enabled", "true"), 
		
		ced_default_output("sdb.ced.dbname", "cccccc00.cre"),
		ced_location("sdb.ced.location", "comms database creator"),
		sdb_home("sdb.home", null);

		private String _propertyKey;
		private String _defaultValue;
		
		private SDBPROPS(String propertyKey, String defaultValue) {
			_propertyKey = propertyKey;
			_defaultValue = defaultValue;
		}
		
		public String toString(){
			return _propertyKey;
		}
		
		public void updatePropertiesWithDefault(Properties propertiesToUpdate){
			if (_defaultValue != null) {
			updateProperty(_defaultValue, propertiesToUpdate);
			}
		}
		
		/**
		 * @return the system value if specified otherwise returns the default value.
		 */
		public String getValue() {
			return System.getProperty(_propertyKey, _defaultValue);
		}

		/**
		 * Updates the properties argument with the input value for this setting
		 * @param newValue the value to assign to this setting
		 * @param props the properties to be updated
		 */
		public void updateProperty(String newValue, Properties props) {
			props.setProperty(_propertyKey, newValue);
		}
		
		public void resolvePathIfRelative(
				String installationDirectory,
				Properties props) {
			File file = new File(
					props.getProperty(_propertyKey));
			if (!file.isAbsolute()) {
				props.setProperty(_propertyKey, FileUtil.concatFilePath(installationDirectory, file.getPath()));
			}
		}
	}
	
	/** serialVersionUID */
	static final long serialVersionUID = -4544769666886838818L;
	
	/** Class Logger */
	static private final Logger logger = Logger.getLogger(Settings.class);	

	
	/**
	 * Constructor
	 */
	public Settings() {
		super(getDefaults());		
	}
	
	/** 
	 * This function has all the defaults paths, locations etc. change at your peril. 
	 * 
	 * @return Properties
	 */
	private static Properties getDefaults(){
	
		Properties defaults = new Properties(System.getProperties());							
		
		for (SDBPROPS prop: SDBPROPS.values()){
			prop.updatePropertiesWithDefault(defaults);
		}
		
		Boolean isWindows = System.getProperty("os.name").toLowerCase().startsWith("windows");
		String newCedLocation = defaults.getProperty(SDBPROPS.ced_location.toString()) + File.separator;

		if (isWindows) {
			newCedLocation = FileUtil.concatFilePath(newCedLocation, "win");
		} else {
			newCedLocation = FileUtil.concatFilePath(newCedLocation, "linux");
		}
		SDBPROPS.ced_location.updateProperty(newCedLocation, defaults);

		
		return defaults; 
	}
	
	/** 
	 * Configure the settings of the the tool by reading a properties file etc.
	 *  
	 * When these exceptions are thrown, the default values are first loaded
	 * into the system properties.
	 * 
	 * Once we have right info to load properties file, we can look for it, and then load 
	 * its values into our properties object. We now have overriden hard-coded defaults 
	 * with property file specific values. 
	 * 
	 * With these in place we can continue to process the command line options
	 * and override the defaults and file set options as required. 
	 * 
	 * @param cmd the command line which may indicate location of properties file.
	 * 
	 * @throws OptionSetException if the specified properties file 
	 * can't be found, or if parsing the global args fails. If we fail to open the
	 * default properties file, we carry on with the default hard coded values
	 * set in getDefaults().
	 *  
	 */
	public void configure(CmdLineArgs cmd) {
		File propertiesFile = cmd.getPropertiesFile();

		if (propertiesFile.exists()) {

			// is this required?
			setProperty("sdb.properties.location", cmd.getPropertiesFile().getAbsolutePath());
			
			try {
				FileInputStream propertiesFileInputStr = new FileInputStream(propertiesFile);
				if (propertiesFileInputStr.available() == 0) {
					logger.warn("Supplied Properties file is empty. Proceeding with default values.");
				} else {
					load(propertiesFileInputStr);
				}
			} catch (IOException ex) {
				// Update System properties with defaults
				System.setProperties(this);

				// If the user has specified a properties file and it cant be
				// found/opened we should throw
				// an exception. If it is an issue that we cannot find our
				// default properties file, we
				// should warn the user and use the default hard coded values.
				logger.warn("Unable to process properties file: "+ ex.getLocalizedMessage()+ ". Using default values.");
				logger.debug("Stack Trace:",ex);
			}

		} else {
			logger.warn("Unable to open properties file "+ propertiesFile.getPath());
			// TODO: exit or continue with defaults?
		}

		// This is the point where we should override any properties with those
		// global ones set
		// at the command line. Currently there are no global properties we can
		// set on command
		// line bar properties file location
		updatePropertiesWithCommandLineOptions(cmd, this);
		String sdbHomePath =  this.getProperty(SDBPROPS.sdb_home.toString());
		if (sdbHomePath == null) {
			SDBPROPS.sdb_home.updateProperty(cmd.getInstallationDirectory().getAbsolutePath(), this);
		} else {
			//test if it's an absolute path
			File sdbHome = new File(sdbHomePath);
			if (!sdbHome.isAbsolute()) {
				logger.warn("Incorrect SDB home set in the properties file " + propertiesFile.getAbsolutePath() + ".");
				logger.warn("Proceeding with " + cmd.getInstallationDirectory().getAbsolutePath());
				SDBPROPS.sdb_home.updateProperty(cmd.getInstallationDirectory().getAbsolutePath(), this);
			}
		}
		
		resolveRelativePaths(getProperty(SDBPROPS.sdb_home.toString()));
		// Update System properties
		System.setProperties(this);
	}

	
	private void resolveRelativePaths(String installationPath) {
		SDBPROPS.ced_location.resolvePathIfRelative(installationPath, this);
		SDBPROPS.sqlite_lib_path.resolvePathIfRelative(installationPath, this);
		SDBPROPS.dbms_lib_path.resolvePathIfRelative(installationPath, this);
		SDBPROPS.contacts_configuration.resolvePathIfRelative(installationPath, this);
		SDBPROPS.contacts_configuration_locale.resolvePathIfRelative(installationPath, this);
	}

	/**
	 * @param cmd
	 * @param props
	 */
	private void updatePropertiesWithCommandLineOptions(CmdLineArgs cmd, Properties props) {
		if(cmd.isDebugEnabled()){
			SDBPROPS.log_console_level.updateProperty("debug", props);
		}
		
	}
	
	/**
	 * @return true if the contacts flow is enabled.
	 */
	public static boolean isContactsEnabled() {
		return Boolean.valueOf(SDBPROPS.contacts_enabled.getValue());
	}
	
	/**
	 * @return true if the contacts speed dial option is enabled.
	 */
	public static boolean isContactsSpeedDialEnabled() {
		return Boolean.valueOf(SDBPROPS.speeddial_enabled.getValue());
	}
}
