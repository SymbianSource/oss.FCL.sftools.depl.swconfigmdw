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

package com.symbian.sdb.contacts.sqlite.model;



/**
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactGroup extends AbstractSQLiteContact {


	//TODO: update equals
	//TODO: anything important in the header?
	/**
	 * Determines whether the two object represent the same group.
	 * This comparison is based on the text field only.
	 * @param the instance to compare against
	 * @return true if the parameter is a group and the text and binary headers and fields are binary identical.
	 */
	public boolean isSameAs(Object arg){
		if (! (arg instanceof SQLiteContactGroup)){
			return false;
		}
		SQLiteContactGroup compareGroup = (SQLiteContactGroup)arg;
		
		return	compareGroup.getTextFields().equals(getTextFields())
				/*&& compareGroup.getTextFieldsHeader().equals(getTextFieldsHeader())
				&& compareGroup.getTextFieldsHeader().equals(getTextFieldsHeader())
				&& compareGroup.getBinaryFieldsHeader().equals(getBinaryFieldsHeader()) 
				&& compareGroup.getBinaryFieldsHeader().equals(getBinaryFieldsHeader())*/;
	}

}
