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

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.mode.DBMode;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.IModeParser;

public class WorkflowFactoryTest extends BaseIntegrationTestCase {
	
    private WorkflowFactory workflowFactory; 
    Mockery context = new Mockery();
	IModeParser modeparser;
	
	public static junit.framework.Test suite() { 
	    return new JUnit4TestAdapter(WorkflowFactoryTest.class); 
	}
	
	@Before
	public void onSetUp() throws Exception {
		modeparser = context.mock(IModeParser.class);
	}

	@Test
	public void testStartCedWorkflow() {
		context.checking(new Expectations() {{
			allowing (modeparser).getDbType(); will(returnValue(DBType.CED));
		    allowing (modeparser).getDbMode(); will(returnValue("generic"));
		}}); 
		IFlow flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof CedFlow);
	
        // verify
        context.assertIsSatisfied();
	}
	
	@Test
	public void testStartContactsWorkflow() {
		context.checking(new Expectations() {{
			allowing (modeparser).getDbType(); will(onConsecutiveCalls(
		    	       returnValue(DBType.SQLITE),
		    	       returnValue(DBType.DBMS)));
			allowing (modeparser).getDbMode(); will(returnValue(DBMode.CONTACTS));
		}});
		IFlow flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof ContactsFlow);
		flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof ContactsFlow);
		
        // verify
        context.assertIsSatisfied();
	}
	
	@Test
	public void testStartGenericWorkflow() {
		context.checking(new Expectations() {{
			allowing (modeparser).getDbType(); will(onConsecutiveCalls(
		    	       returnValue(DBType.SQLITE),
		    	       returnValue(DBType.CED),
		    	       returnValue(DBType.DBMS)));
			allowing (modeparser).getDbMode(); will(returnValue(DBMode.GENERIC));
		}});
		
		IFlow flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof GenericFlow);
		flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof CedFlow);
		flow = workflowFactory.getWorkflow(modeparser);
		Assert.assertTrue(flow instanceof GenericFlow);
		
        // verify
        context.assertIsSatisfied();
	}

    public void setWorkflowFactory(WorkflowFactory workflowFactory) {
        this.workflowFactory = workflowFactory;
    }
}
