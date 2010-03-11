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

package com.symbian.sdb.contacts.template;


public enum ContactFlagTypes {
	KIntFieldFlagHidden,
	KIntFieldFlagReadOnly,
	KIntFieldFlagSynchronize, 
	KIntFieldFlagDisabled,
	KIntFieldFlagFilterable,
	KIntFieldFlagFilterable1,
	KIntFieldFlagFilterable2,
	KIntFieldFlagFilterable3, 
	KIntFieldFlagFilterable4; 
	
	public static ContactFlagTypes[] attrValues() {
		return new ContactFlagTypes[]{
				KIntFieldFlagHidden,
				KIntFieldFlagReadOnly,
				KIntFieldFlagSynchronize,
				KIntFieldFlagDisabled
				};
	}
	
	public static ContactFlagTypes[] extAttrValues() {
		return new ContactFlagTypes[]{KIntFieldFlagFilterable,
										KIntFieldFlagFilterable1,
										KIntFieldFlagFilterable2,
										KIntFieldFlagFilterable3,
										KIntFieldFlagFilterable4
			};
	}
}
