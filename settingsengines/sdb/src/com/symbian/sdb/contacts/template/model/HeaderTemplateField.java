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



package com.symbian.sdb.contacts.template.model;

import com.symbian.sdb.contacts.model.ContactFieldLabel;
import com.symbian.sdb.contacts.model.FieldAttributes;

/**
 * Common interface for dbms and sqlite template field headers
 */
public interface HeaderTemplateField {
	
	/** 
	 * @return the attributes persisted in field header
	 */
	public FieldAttributes getAttributesContainer();
	
	/**
	 * @return the field label
	 */
	public ContactFieldLabel getFieldLabel();
	
	/**
	 * @return the vCard mapping
	 */
	public int getFieldVcardMapping();
	
	/**
	 * @return the additional uids for the field - vCard mappings or contact field type
	 */
	public int[] getFieldAdditionalUIDValues();
	
	/**
	 * @return the real field hint value, 
	 * after the mask has been used on the one persisted in field header 
	 */
	public long getFieldHintValue();
	
	/**
	 * @return field index
	 */
	public long getFieldId();
	
}
