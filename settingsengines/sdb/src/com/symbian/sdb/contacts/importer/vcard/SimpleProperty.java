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

import java.io.UnsupportedEncodingException;

import net.sf.vcard4j.util.XpathUtil;

import org.w3c.dom.Element;

import com.symbian.sdb.exception.SDBRuntimeException;


/**
 * @author krzysztofZielinski
 *
 */
public class SimpleProperty extends Property {

    /**
     * @param type
     */
    public SimpleProperty(Element type) {
        super(type);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.vcard.Property#getValue()
     */
    @Override
    public byte[] getValue() {
        try {
			return XpathUtil.getValue(getElement(), "value/text/text()").trim().getBytes("ISO-8859-1");
		} catch (UnsupportedEncodingException e) {
			throw new SDBRuntimeException(e.getMessage(), e);
		}
    }


}
