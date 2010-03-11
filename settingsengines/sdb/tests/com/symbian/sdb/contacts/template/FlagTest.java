// Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.contacts.template;

import junit.framework.Assert;

import org.junit.Test;

public class FlagTest {

	@Test
	public void testSame() {
		Flag flag1 = new Flag("uid1", 1);
		Flag flag2 = new Flag("uid2", 2);
		Flag flag3 = new Flag("uid3", 1);
		Flag flag4 = new Flag("uid1", 4);
		
		Assert.assertTrue(flag1.same(flag3));
		Assert.assertFalse(flag1.same(flag2));
		Assert.assertFalse(flag1.same(flag4));
	}

}
