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

import com.symbian.sdb.mode.DBMode;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.IModeParser;

/**
 * returns the correct work flow based on the mode parser results
 */
public class WorkflowFactory {

    private IFlow genericFlow;
    private IFlow cedFlow;
    private IFlow contactsFlow;
    
    public void setGenericFlow(GenericFlow genericFlow) {
        this.genericFlow = genericFlow;
    }

    public void setCedFlow(CedFlow cedFlow) {
        this.cedFlow = cedFlow;
    }

    public void setContactsFlow(ContactsFlow contactsFlow) {
        this.contactsFlow = contactsFlow;
    }

    /**
	 * @param mode ModeParser instance
	 * @return correct flow for the current mode values
	 */
	public IFlow getWorkflow(IModeParser mode) {
		IFlow flow = null;
		
		if (mode.getDbType()== DBType.CED) {
			flow = cedFlow;
		} else {
			if (mode.getDbMode().equals(DBMode.CONTACTS)) {
			    flow = contactsFlow;
			} else {
			    flow = genericFlow;
			}
		}
		
		return flow;
	}

}
