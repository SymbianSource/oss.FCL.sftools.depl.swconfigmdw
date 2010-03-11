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

public class EmbeddedStore extends StreamStore {

	public EmbeddedStore() throws StoreException {
		int result = _create();
		if ( result <= 0 ) {
			throw new StoreException(result);
		}
		peerHandle = result;
	}
	
	public EmbeddedStore(byte [] content) throws StoreException {
		if ( content == null ) {
			throw new NullPointerException();
		}
		int result = _create(content);
		if ( result <= 0 ) {
			throw new StoreException(result);
		}
		peerHandle = result;
	}
	
	@Override
	public void close() {
		if( peerHandle > 0 ) {
			_close(peerHandle);
			peerHandle = 0;
		}
	}

	public int rootStream() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _root(peerHandle);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
		return result;
	}

	public void setRoot(int id) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _setRoot(peerHandle, id);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}
	
	@Override
	public byte[] getContent() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _getContentSize(peerHandle);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
		byte [] buffer = new byte[result];
		result = _getContent(peerHandle, buffer);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
		return buffer;
	}
	
	private native int _create();
	private native int _create(byte [] content);
	private native int _root(int peerHandle);
	private native int _setRoot(int peerHandle, int id);
	private native int _close(int peerHandle);
	private native int _getContent(int peerHandle, byte [] buffer);
	private native int _getContentSize(int peerHandle);

	public int getPeerHandle() {
		return peerHandle;
	}
}
