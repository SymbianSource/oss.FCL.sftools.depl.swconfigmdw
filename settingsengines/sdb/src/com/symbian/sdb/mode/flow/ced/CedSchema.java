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

import java.io.File;
import java.util.NoSuchElementException;

import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.FileUtil;

/**
 * @author jamesclark
 *
 */
public enum CedSchema {
	ced91("91","9_3","93"),
	ced92("92","9_3","93"),
	ced93("93","9_3","93"),  
	ced94("94","9_4","94"),
	ced95("95","9_5","95");
	
	private String exeSuffix;
	private String shortFormTargetOS;
	private String shortFormOSVersion;
	
	private static final String exePrefix = "cedv";
	
	private static final String exeExtension = ".exe";
	
	private CedSchema(String shortFormTargetOS, String exeSuffix, String shortFormExe) {
		this.shortFormTargetOS = shortFormTargetOS;
		this.exeSuffix = exeSuffix;
		this.shortFormOSVersion = shortFormExe;
	}
	
	/**
	 * 
	 * @return the name of the executable to invoke for the given schema
	 */
	public String getExeName(){
		StringBuilder exeName = new StringBuilder(exePrefix).append(exeSuffix);
		if(isOnWindows()){
			exeName.append(exeExtension);
		}
		return exeName.toString();
	}

	/**
	 * @return the directory containing the executable to invoke for the given schema
	 */
	public File getExeDirectory() {
		return new File(Settings.SDBPROPS.ced_location.getValue());
	}
	
	/**
	 * 
	 * @return the short form of the target OS identifier. For example Symbian OS 9.5 is represented as "95"
	 */
	public String getShortFormOSVersion(){
		return shortFormOSVersion;
	}

	/**
	 * @param schemaLabel the name of the schema required
	 * @return the schema matching the input value
	 */
	public static CedSchema getSchema(String schemaLabel) {
		for(CedSchema schema : CedSchema.values()){
			if(schema.isMatch(schemaLabel)){
				return schema;
			}
		}
		throw new NoSuchElementException("Cannot determine schema for value: "+schemaLabel);
	}
	


	/**
	 * @param schemaLabel a name of a schema
	 * @return true if the parameter matches the this schema instance 
	 */
	private boolean isMatch(String schemaLabel) {
		return (schemaLabel!=null && schemaLabel.endsWith(shortFormTargetOS));
	}
	
	/**
	 * 
	 * @return true if the current OS (as denoted by the system property os.name is windows 
	 */
	private boolean isOnWindows(){
		return System.getProperty("os.name").startsWith("Windows");
	}
	
}
