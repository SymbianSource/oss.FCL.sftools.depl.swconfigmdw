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
// PropertyUtils.java
//



package com.symbian.sdb.contacts.importer.vcard;

/**
 * Utility methods for VCard properties
 * 
 * @author krzysztofZielinski
 *
 */
public class PropertyUtil {

	private PropertyUtil() {
		// This class is not meant to be instantiated
	}

	/**
	 * Checks if given string matches photo string. 
	 * It is used to mark places where VCard photo property is treaded specially.
	 * 
	 * @param text
	 * @return
	 */
	public static boolean isPhoto(String text)	{
		return text.matches("[Pp][Hh][Oo][Tt][Oo]");
	}
}
