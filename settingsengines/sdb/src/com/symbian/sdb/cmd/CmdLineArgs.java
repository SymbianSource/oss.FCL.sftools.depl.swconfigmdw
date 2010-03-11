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
import java.util.List;

import com.symbian.sdb.mode.IModeParser;

public interface CmdLineArgs {

    /**
     * Returns the settings file, as given with -c option
     * @return settings file
     */
    public File getConfigurationFile();

    /**
     * Returns the output database file, as given with -o option
     * @return the output database file
     */
    public File getOutputDb();

    /**
     * Returns the input database file, as given with -i option
     * @return the input database file
     */
    public File getInputDb();

    /**
     * 
     * @return any files specified on the command line that are not recognised as vCards or CED config. Guaranteed not null.
     */
    public List<File> getSQLFiles();
    
    /**
     * 
     * @return any files identified as vCards. Guaranteed not null.
     */
    public List<File> getvCardFiles();
    
    /**
     * 
     * @return any files identified as CED configuration files. Guaranteed not null.
     */
    public List<File> getCedFiles();

    /**
     * Returns the mode value, as given with -m option
     * @return mode value
     */
    public IModeParser getMode();

    public File getPropertiesFile();
    
    /**
     * returns the group name for contacts creation
     * @return
     */
    public String getGroup();

	/**
	 * @return true is debug output mode was specified on the command line
	 */
	public boolean isDebugEnabled();
    
    /**
     * returns the template file
     * @return
     */   
    public File getTemplateFile();
    
    /**
     * @return false if app should fail fast (on first sql error), true if should continue execution
     */
    public boolean failFast();
    
	/**
	 * @return speed dial INI file should be generated/updated
	 */
	public boolean isSpeedDialGenerationEnabled();

	public File getSpeedDialFile();
	
	public String getDeploymentDbLocation();
	
	public File getInstallationDirectory();
}
