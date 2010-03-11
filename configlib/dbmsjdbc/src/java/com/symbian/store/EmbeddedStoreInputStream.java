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

class EmbeddedStoreInputStream extends StoreInputStream {
	public EmbeddedStoreInputStream(Store store, int streamId) throws StoreException {
		super(store, streamId);
	}
	@Override
	protected int createNative(int storePeerHandle, int streamId) {
		return _create(storePeerHandle, streamId);
	}

	private native int _create(int storePeerHandle, int aStreamId);
}
