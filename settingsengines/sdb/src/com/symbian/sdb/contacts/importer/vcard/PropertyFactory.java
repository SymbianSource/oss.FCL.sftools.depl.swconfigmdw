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

import java.util.Collections;

import org.w3c.dom.Element;

/**
 * @author krzysztofZielinski
 *
 */
public class PropertyFactory {

	/**
	 * Creates new simple property
	 * 
	 * @param element
	 * @return
	 */
	public static SimpleProperty newSimpleProperty(Element element) {
		if (isPhoto(element))	{
			return new PhotoProperty(element); 
		}
		Collections.emptySet();
		return new SimpleProperty(element);
	}

	private static boolean isPhoto(Element element) {
		return PropertyUtil.isPhoto(element.getAttribute("name"));
	}

	/**
	 * @param node
	 * @return
	 */
	public static ListProperty newListProperty(Element node) {
		return new ListProperty(node);
	}

	/**
	 * @param node
	 * @param numberOfItems
	 * @return
	 */
	public static StructuredProperty newStructuredProperty(Element node, Integer numberOfItems) {
		return new StructuredProperty(node, numberOfItems);
	}
	

}
