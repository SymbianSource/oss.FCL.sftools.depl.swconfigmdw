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



package com.symbian.sdb.contacts.model;

/**
 * interface to extract specific information from the template field attributes field
 */
public interface FieldAttributes {
	
	/**
	 * @return the storage type of the field (text, store, date or agent)
	 */
	public long getFieldStorageType();
	
	/**
	 * @return category of the field (none, home, work, other)
	 */
	public byte getCategory();

	/**
	 * @return extended attributes of the field (private, speed dial and user defined filters)
	 */
	public long getExtendedAttributes();
	
	/**
	 * @return attributes of the field (Hidden, ReadOnly, Synchronize, 
	 * Disabled, UserMask, TemplateMask, OverRidesLabel, 
	 * UsesTemplateData, UserAddedField, Template, LabelUnspecified and Deleted)
	 */
	public long getAttributes();
	
}
