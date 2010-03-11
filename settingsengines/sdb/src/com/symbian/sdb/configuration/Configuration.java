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

package com.symbian.sdb.configuration;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;

import com.symbian.sdb.configuration.options.DbOptions;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;

@SuppressWarnings("unchecked")
public class Configuration {

    private static final Logger logger = Logger.getLogger(Configuration.class);
    protected ConfigurationParser confParser;
    protected Document configDocument;
    // holds free-form options for the DbType currently in use
    protected Map<String, String> options = null;
    
    public boolean initialize(File configFile, DBType dbType, ConfigurationValidator validator) throws SDBValidationException {
        logger.debug("initializing configuration file");
        configDocument = validator.loadAndValidate(configFile);
        DocumentVersion documentVersion = validator.getVersion();
        if (documentVersion.equals(DocumentVersion.V10) && dbType.equals(DBType.DBMS)) {
            //ignore the parsing here
            logger.warn("Warning: the configuration file version is not applicable to DBMS database type. Configuration file " + configFile.getAbsolutePath() + " will be ignored.");
            return false;
        } else {
            confParser = new ConfigurationParser(dbType, documentVersion);
            options = confParser.parseConfigurationOptions(configDocument);
            return true;
        }
    }
    
    public void applySettings(boolean update, SystemSettings systemSettings) throws SDBExecutionException {
        if (!update || !systemSettings.hasSettingsTable()) {
        	logger.info("Applying SQLite DB settings...");
            systemSettings.applySystemSettings();
        }
    }
    
    public void applySecurity(DBType dbType, PlatsecConfigurator platsec) throws SDBExecutionException {
        if (confParser != null) {
            SecuritySettings settings = confParser.parseSecurityOptions(configDocument);
            if (settings.getPolicies().size() > 0) {
                if (dbType.equals(DBType.SQLITE)) {
                    platsec.applySecuritySettings(settings);
                } else {
                    logger.warn("Warning: Security settings are not applicable for the DBMS database type. Settings will be ignored.");
                }
            }
        }
    }
    
    public List<String> getPragmaStm(DBType dbType) {
        ArrayList<String> list = new ArrayList<String>();
        for (DbOptions option : DbOptions.values()) {
            if (option.isPragma() && option.isApplicableFor(dbType)) {
                list.add(option.getValue());
            }
        }
        return list;
    }
    
    public String getConnectionString(DBType dbType) {
        String parameters = null;
        for (DbOptions option : DbOptions.values()) {
            if (!option.isPragma() && option.isApplicableFor(dbType)) {
                if (option.getValue() != null) {
                    if (parameters == null) {
                        parameters = "";
                    } else {
                        parameters += "&";
                    }
                    parameters += option.getValue();
                }
            }
        }
        return parameters;
    }

    public String getOption(String optionName) {
    	if ( options != null) {
    		return options.get(optionName);
    	} else {
    		return null;
    	}
    }
}
