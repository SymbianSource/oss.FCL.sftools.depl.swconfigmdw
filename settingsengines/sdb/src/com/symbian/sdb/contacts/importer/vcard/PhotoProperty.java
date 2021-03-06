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



package com.symbian.sdb.contacts.importer.vcard;

import org.w3c.dom.Element;


/**
 * @author krzysztofzielinski
 *
 */
class PhotoProperty extends SimpleProperty	{

	public PhotoProperty(Element type) {
		super(type);
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.importer.vcard.SimpleProperty#getValue()
	 */
	@Override
	public byte[] getValue() {
		return super.getValue();
	}
}
