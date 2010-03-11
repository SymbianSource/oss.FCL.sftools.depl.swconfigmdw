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
import java.net.URISyntaxException;
import java.util.Enumeration;
import java.util.Properties;

import junit.textui.TestRunner;

import org.apache.log4j.Level;
import org.jmock.Mock;
import org.jmock.MockObjectTestCase;
import org.jmock.core.Invocation;
import org.jmock.core.InvocationMatcher;

import com.symbian.sdb.cmd.CmdLineArgs;

public class SettingsTest extends MockObjectTestCase {

	private Settings fSettings;
	private File PropsFile = new File("tests/config/singleModification.properties");
	private File EmptyPropsFile = new File("tests/config/empty.properties");
	private Object PropsFile_InfoLogLevel = new File("tests/config/infoLogLevel.properties");
	private File NotExistingPropsFile = new File("this_file_does_not_exist.file");
	private Properties fDefaultSystemProperties = (Properties)System.getProperties().clone();
	private String fSqliteString = "sdb";
	

	public static void main(String[] args) {
		TestRunner.run(SettingsTest.class);
	}

	public void setUp() throws Exception {
		fSettings = new Settings();
	}
	private File getInstallationDirectory() {
		try {
			File sdbJarFile = new File(getClass().getProtectionDomain().getCodeSource().getLocation().toURI());
			File parentDirectory = sdbJarFile.getParentFile();
			if (parentDirectory.getName().equals("lib")) {
				parentDirectory = parentDirectory.getParentFile();
			}
			return parentDirectory;
		} catch (URISyntaxException ex) {
			return null;
		}
	}
	/**
	 * This is to make sure default values are set when the user specifies an
	 * empty properties file
	 */
	public void testEmptyPropsFile() throws Exception {

		boolean lAppSettingsFound = false;

		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(EmptyPropsFile));
		cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
	                returnValue(getInstallationDirectory()));

		fSettings.configure((CmdLineArgs) cmdLineMock.proxy());

		for (Enumeration<?> lEnum = System.getProperties().propertyNames(); lEnum.hasMoreElements();) {
			String lPropName = (String) lEnum.nextElement();
			if (lPropName.startsWith(fSqliteString)) {
				lAppSettingsFound = true;
			}
		}

		// Reset system settings for next test...
		System.setProperties((Properties)fDefaultSystemProperties.clone());

		// If no application specific settings are set we fail
		assertTrue("No application settings found in system properties", lAppSettingsFound);

	}

	/**
	 * This is to see if the default values get set in the absence of a
	 * properties file
	 */
	public void testDefaultsCorrectlySet() throws Exception {

		boolean lAppSettingsFound = false;

		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(NotExistingPropsFile));
        cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
                returnValue(getInstallationDirectory()));

		fSettings.configure((CmdLineArgs) cmdLineMock.proxy());

		for (Enumeration<?> lEnum = System.getProperties().propertyNames(); lEnum.hasMoreElements();) {
			String lPropName = (String) lEnum.nextElement();
			if (lPropName.startsWith(fSqliteString)) {
				lAppSettingsFound = true;
			}
		}

		// Reset system settings for next test...
		System.setProperties((Properties)fDefaultSystemProperties.clone());

		// If no application specific settings are set we fail
		assertTrue("No application settings found in system properties", lAppSettingsFound);

	}

	/**
	 * This is to see if the default values are set and modified
	 */
	public void testDefaultsCorrectlySetAndModified() throws Exception {
		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(PropsFile));
		cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
				returnValue(getInstallationDirectory()));

		fSettings.configure((CmdLineArgs) cmdLineMock.proxy());

		assertEquals("The default property should have been set", Settings.SDBPROPS.log_file_level
				.getValue(), System.getProperty(Settings.SDBPROPS.log_file_level.toString()));

		assertEquals("The property specified in the input file should have been overritten",
				"modified", System.getProperty(Settings.SDBPROPS.dbname.toString()));

		// Reset system settings for next test...
		System.setProperties((Properties)fDefaultSystemProperties.clone());
	}
	
	/**
	 * This is to see if the default values are set and modified
	 */
	public void testDebugModeSetsDebug() throws Exception {
		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(true));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(PropsFile_InfoLogLevel));
		cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
				returnValue(getInstallationDirectory()));

		// Update the system properties as would happen if Debug is enabled.
		//
		Properties sysProps = System.getProperties();
		Settings.SDBPROPS.log_console_level.updateProperty("debug", sysProps);
		
		fSettings.configure((CmdLineArgs) cmdLineMock.proxy());

		assertEquals("The console log level should be debug", Level.toLevel(Settings.SDBPROPS.log_console_level
				.getValue()), Level.toLevel("debug"));

		// Reset system settings for next test...
		System.setProperties((Properties)fDefaultSystemProperties.clone());
	}
	public void testResolveRelativePaths() {
		File insDir = getInstallationDirectory();
		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(EmptyPropsFile));
		cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
				returnValue(insDir));

		Settings settings = new Settings();
		settings.configure((CmdLineArgs) cmdLineMock.proxy());
		
		String expected = insDir.getAbsolutePath() + File.separator;
		assertEquals(new File(expected + "comms database creator" + File.separator + getCedSystem()).getAbsolutePath(), new File(Settings.SDBPROPS.ced_location.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "lib").getAbsolutePath(), new File(Settings.SDBPROPS.dbms_lib_path.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "lib").getAbsolutePath(), new File(Settings.SDBPROPS.sqlite_lib_path.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "config/contacts.xml").getAbsolutePath(), new File(Settings.SDBPROPS.contacts_configuration.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "config/contacts_locale_en_gb.xml").getAbsolutePath(), new File(Settings.SDBPROPS.contacts_configuration_locale.getValue()).getAbsolutePath());
	}
	
	private String getCedSystem() {
		Boolean isWindows = System.getProperty("os.name").startsWith("Windows");
		if (isWindows) {
			return "win";
		} else {
			return "linux";
		}
	}
	
	public void testSdbHomeAbsolute() {
		Boolean isWindows = System.getProperty("os.name").startsWith("Windows");
		File propsFile;
		String sdbHome;
		if (isWindows) {
			sdbHome = "d:/sdb";
			propsFile = new File("tests/config/sdb.home.win.properties");
		} else {
			sdbHome = "/home/sdb";
			propsFile = new File("tests/config/sdb.home.linux.properties");
		}
		
		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(propsFile));
		cmdLineMock.expects(this.never()).method("getInstallationDirectory");
		
		Settings settings = new Settings();
		settings.configure((CmdLineArgs) cmdLineMock.proxy());
		
		assertEquals(sdbHome, Settings.SDBPROPS.sdb_home.getValue());
		
		System.clearProperty("sdb.home");
	}
	
	public void testResolveAbsolutePaths() {
		Boolean isWindows = System.getProperty("os.name").startsWith("Windows");
		File cedPropsFile;
		String absolutePath;
		if (isWindows) {
			absolutePath = "d:/ced";
			cedPropsFile = new File("tests/config/ced.properties");
		} else {
			absolutePath = "/home";
			cedPropsFile = new File("tests/config/ced_linux.properties");
		}
		
		File insDir = getInstallationDirectory();
		Mock cmdLineMock = mock(CmdLineArgs.class);
		cmdLineMock.expects(anyNumberofTimes()).method("isDebugEnabled").will(
				returnValue(false));
		cmdLineMock.expects(anyNumberofTimes()).method("getPropertiesFile").will(
				returnValue(cedPropsFile));
		cmdLineMock.expects(anyNumberofTimes()).method("getInstallationDirectory").will(
				returnValue(insDir));
		Settings settings = new Settings();
		settings.configure((CmdLineArgs) cmdLineMock.proxy());

		String expected = insDir.getAbsolutePath() + File.separator;			
		assertEquals(new File(absolutePath).getAbsolutePath(), new File(Settings.SDBPROPS.ced_location.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "lib").getAbsolutePath(), new File(Settings.SDBPROPS.dbms_lib_path.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "lib").getAbsolutePath(), new File(Settings.SDBPROPS.sqlite_lib_path.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "config/contacts.xml").getAbsolutePath(), new File(Settings.SDBPROPS.contacts_configuration.getValue()).getAbsolutePath());
		assertEquals(new File(expected + "config/contacts_locale_en_gb.xml").getAbsolutePath(), new File(Settings.SDBPROPS.contacts_configuration_locale.getValue()).getAbsolutePath());
	}
	
	private InvocationMatcher anyNumberofTimes() {
		return new AnyNumberOfTimes();
	}

	private class AnyNumberOfTimes implements InvocationMatcher {

		public boolean hasDescription() {
			return false;
		}

		public void invoked(Invocation arg0) {
		}

		public boolean matches(Invocation arg0) {
			return true;
		}

		public void verify() {
		}

		public StringBuffer describeTo(StringBuffer arg0) {
			return arg0;
		}

	}
}
