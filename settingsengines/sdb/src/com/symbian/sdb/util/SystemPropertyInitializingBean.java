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



package com.symbian.sdb.util;

import java.util.Map;

import org.springframework.beans.factory.InitializingBean;

/**
 * Bean for automatically initialising System properties from within a Spring context. 
 * 
 * @author krzysztofZielinski
 */
public class SystemPropertyInitializingBean implements InitializingBean {

    // ~ Fields ================================================================
    
    // Properties to be set
    private Map<String,String> systemProperties;

    // ~ Business Methods ======================================================
    
    /**
     *  Sets the system properties
     */
    public void afterPropertiesSet() throws Exception {
        
        if (systemProperties == null) {
            // No properties to initialize
            return;
        }

        for (String propertyName : systemProperties.keySet()) {
            String propertyValue = systemProperties.get(propertyName);
            System.setProperty(propertyName, propertyValue);
        }
    }

    // ~ Getters/Setters =======================================================

    public void setSystemProperties(Map<String,String> systemProperties) {
        this.systemProperties = systemProperties;
    }
}