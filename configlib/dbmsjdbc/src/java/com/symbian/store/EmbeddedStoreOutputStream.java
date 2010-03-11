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

class EmbeddedStoreOutputStream extends StoreOutputStream {
	EmbeddedStoreOutputStream(Store streamStore, int streamId) 
		throws StoreException {
		super(streamStore, streamId);
		int result = _create(store.getPeerHandle(), streamId);
		if (result <= 0) {
			throw new StoreException(result);
		}
		peerHandle = result;
	}
	
	EmbeddedStoreOutputStream(Store streamStore) 
		throws StoreException {
		super(streamStore);
		int result = _create(store.getPeerHandle());
		if (result <= 0) {
			throw new StoreException(result);
		}
		peerHandle = result;
		id = _getStreamId(peerHandle);
	}


	private native int _create(int storePeerHandle, int streamId);
	private native int _create(int storePeerHandle);
	private native int _getStreamId(int peerHandle2);
}
