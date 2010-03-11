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

package com.symbian.store;

public interface Store {
	public static final int Type_EmbeddedStore = 1;
	public static final int Type_DictinaryStore = 2;
	
	void close();
	void commit() throws StoreException;
	void revert() throws StoreException;
	
	// id meaning is implementation specific: 
	// StreamStore interprets it as streamId
	// DictionaryStore interprets it as uid
	StoreInputStream getInputStream(int id) throws StoreException;
	
	// id meaning is implementation specific: 
	// StreamStore interprets it as streamId
	// DictionaryStore interprets it as uid
	StoreOutputStream getOutputStream(int streamId) throws StoreException;
	
	int getPeerHandle();

}
