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

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.jmock.Mock;
import org.jmock.cglib.MockObjectTestCase;

public class PlatsecConfiguratorTest extends MockObjectTestCase {

    PlatsecConfigurator configurator;
    
    protected void setUp() throws Exception {
        super.setUp();
    }

    protected void tearDown() throws Exception {
        super.tearDown();
    }

    /**
     * This test ensures the removing of these tables is ok
     */
    public void testRemoveExistingSecurityTables(){
        //When it is open...
        Mock lMockDbConnection = mock(Connection.class);
        Mock lMockPreparedStatement = mock(PreparedStatement.class);
        
       // lMockDbConnection.expects(once()).method("isClosed").will(returnValue(false));
        lMockDbConnection.expects(atLeastOnce()).method("prepareStatement").will(returnValue((PreparedStatement)lMockPreparedStatement.proxy()));       
        lMockPreparedStatement.expects(atLeastOnce()).method("execute").will(returnValue(true));
        lMockPreparedStatement.expects(atLeastOnce()).method("close");
        configurator = new PlatsecConfigurator((Connection)lMockDbConnection.proxy());
        try {
            configurator.removeExistingSecurityTables();
        } catch (SQLException ex) {
            fail("Unexpected Exception Thrown: "+ex.getMessage());
        }
        
    }
    
    
    /**
     * Tests we are correctly checking to see the database
     * has security tables
     */
    public void testDbHasSecurityTables(){
        //When it is open...
        Mock lMockDbConnection = mock(Connection.class);
        Mock lMockPreparedStatement = mock(PreparedStatement.class);
        Mock lResultSet = mock(ResultSet.class);
        
      //  lMockDbConnection.expects(once()).method("isClosed").will(returnValue(false));
        lMockDbConnection.expects(once()).method("prepareStatement").will(returnValue((PreparedStatement)lMockPreparedStatement.proxy()));
        
        lMockPreparedStatement.expects(once()).method("executeQuery").will(returnValue((ResultSet)lResultSet.proxy()));
        lMockPreparedStatement.expects(once()).method("close");
        
        lResultSet.expects(once()).method("next").will(returnValue(true));
        lResultSet.expects(once()).method("close");
        
        //fDbManager.setConnection((Connection)lMockDbConnection.proxy());
        configurator = new PlatsecConfigurator((Connection)lMockDbConnection.proxy());
        try {
            configurator.doesDbHaveSecuritySettings();
        //  fDbManager.setConnection(null);
        } catch (SQLException ex) { 
            fail("Unexpected Exception thrown"+ex.getMessage());
        }
        
    }
    
}
