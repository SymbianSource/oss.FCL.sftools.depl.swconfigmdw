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

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class ContactsUidMap {
	
	private Map<String,String> mapper = Collections.emptyMap();
	
	public ContactsUidMap(HashMap<String, String> map) {
		mapper = map;
	}
	
	/**
	 * This provides a mapping between strings as defined in the mapping configuration file.
	 * @param fromID The ID to map from
	 * @return the resulting ID obtained from the mapping file.
	 */
	public String map(String fromID){
		if(mapper.containsKey(fromID)){
			return mapper.get(fromID);
		}
		return fromID;
	}
}
