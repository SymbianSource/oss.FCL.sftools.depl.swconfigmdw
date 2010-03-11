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

package com.symbian.sdb.contacts.dbms.model;

import junit.framework.Assert;

import org.junit.Test;


/**
 * @author jamesclark
 *
 */
public class ContactFieldHeaderTest {

	
	@Test
	public void testHeader_AdditionalMappingFlagValue() throws Exception{
		Assert.assertEquals("The Attribute flag for additional mappings has changed value",(int)0x200000, ContactFieldHintMask.DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS.getValue());
	}
	
	@Test
	public void testHeader_AdditionalMappingFlagSet() throws Exception{
		ContactFieldHeader header = new ContactFieldHeader();
		// clear the default value
		header.setFieldHint(0);
		
		// Currently the flag hasn't been set so the mask will be 0
		Assert.assertEquals("The additional mapping flag should be 0 if not set.", 0, header.getFieldHint() & ContactFieldHintMask.DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS.getValue());
		
		// Set the flag
		header.setFieldHasAdditionalUIDs();
		
		// The mask is now one
		Assert.assertTrue("The additional mapping flag should be set.", (header.getFieldHint() & ContactFieldHintMask.DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS.getValue()) != 0);
	}
}
