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

package com.symbian.sdb.exception;

import org.apache.commons.cli2.Option;

public class OptionMissingException extends Exception {
	static final long serialVersionUID = 0;
	
	public OptionMissingException(Option option) {
		super("The option " + option.getPreferredName()+ " is missing");		
	}
	
}
