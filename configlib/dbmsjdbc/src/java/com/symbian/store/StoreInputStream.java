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

import java.io.IOException;
import java.io.InputStream;

public abstract class StoreInputStream extends InputStream {
	int peerHandle;
	Store store;
	int streamId;
	boolean closed = false;
	
	StoreInputStream(Store store, int streamId)
			throws StoreException {
		this.store = store;
		this.streamId = streamId;
		int result = createNative(store.getPeerHandle(), streamId);
		if (result <= 0) {
			throw new StoreException(result);
		}
		peerHandle = result;
	}

	protected abstract int createNative(int storePeerHandle, int aUid);
	
	public int available() throws IOException {
		checkClosed();
		return 0;
	}

	public void close() throws IOException {
		if (closed) {
			return;
		}
		_close(peerHandle);
		peerHandle = 0;
		closed = true;
	}

	public int read(byte b[]) throws IOException {
		return read(b, 0, b.length);
	}

	public int read() throws IOException {
		checkClosed();
		return _readByte(peerHandle);
	}

	public int read(byte b[], int off, int len) throws IOException {
		if ( b == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readBytes(peerHandle, b, off, len);
	}

	public short readInt16() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readInt16(peerHandle);
	}

	public int readInt32() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readInt32(peerHandle);
	}

	public int readCardinality() throws IOException {
		checkClosed();
		return _readCardinality(peerHandle);
	}

	public byte readInt8() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readInt8(peerHandle);
	}

	public float readReal32() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readReal32(peerHandle);
	}

	public double readReal64() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readReal64(peerHandle);
	}

	public long readUInt32() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readUInt32(peerHandle);
	}

	public int readUInt16() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readUInt16(peerHandle);
	}

	public short readUInt8() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readUInt8(peerHandle);
	}

	public String readDes16(int length) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes16(peerHandle, length);
	}

	public long readInt64() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readInt64(peerHandle);
	}

	public long readUInt64() throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readUInt64(peerHandle);
	}

	/**
	 * 
	 * @param data
	 * @param length
	 * @return The number of characters actually read
	 * @throws IOException
	 */
	public int readDes16(short[] data, int length) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes16(peerHandle, data, length);
	}

	public String readDes16(char delimiter) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes16(peerHandle, delimiter);
	}

	public String readBuf16(int maxSize) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readBuf16(peerHandle, maxSize);
	}


	public String readBuf8(int maxSize) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readBuf8(peerHandle, maxSize);
	}

	public byte[] readBuf8Raw(int maxSize) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readBuf8Raw(peerHandle, maxSize);
	}

	public int readDes16(short[] data, char delimiter) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes16(peerHandle, data, delimiter);
	}
	
	public int readDes8(byte[] data, char delimiter) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes8(peerHandle, data, delimiter);
	}
	
	public String readDes8String(char delimiter) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes8String(peerHandle, delimiter);
	}

	public String readDes8String(int length) throws IOException {
		checkClosed();
		// native will throw an exception if anything goes wrong
		return _readDes8String(peerHandle, length);
	}

	private void checkClosed() throws IOException {
		if (closed) {
			throw new IOException("Store stream has been closed");
		} else if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
	}

	public boolean isClosed() {
		return closed;
	}

	public Store getStore() {
		return store;
	}

	public void setStore(StreamStore store) {
		this.store = store;
	}

	public int getStreamId() {
		return streamId;
	}

	public void setStreamId(int streamId) {
		this.streamId = streamId;
	}

	private native void _close(int peerHandle);
	private native int _readByte(int peerHandle2) throws IOException;
	private native int _readBytes(int peerHandle2, byte[] b, int off, int len) throws IOException;
	private native short _readInt16(int peerHandle2) throws IOException;
	private native int _readInt32(int peerHandle2) throws IOException;
	private native byte _readInt8(int peerHandle2) throws IOException;
	private native long _readInt64(int peerHandle2) throws IOException;
	private native long _readUInt64(int peerHandle2) throws IOException;
	private native float _readReal32(int peerHandle2) throws IOException;
	private native double _readReal64(int peerHandle2) throws IOException;
	private native long _readUInt32(int peerHandle2) throws IOException;
	private native int _readUInt16(int peerHandle2) throws IOException;
	private native short _readUInt8(int peerHandle2) throws IOException;
	private native String _readDes16(int peerHandle2, int length) throws IOException;
	private native int _readDes16(int peerHandle2, short[] data, int length) throws IOException;
	private native String _readDes16(int peerHandle2, char delimiter) throws IOException;
	private native int _readDes16(int peerHandle2, short[] data, char delimiter) throws IOException;
	private native int _readDes8(int peerHandle2, byte[] data, char delimiter) throws IOException;
	private native String _readDes8String(int peerHandle2, char delimiter) throws IOException;
	private native String _readDes8String(int peerHandle2, int length) throws IOException;
	private native int _readCardinality(int peerHandle2) throws IOException;
	private native String _readBuf8(int peerHandle2, int aMaxSize);
	private native String _readBuf16(int peerHandle2, int aMaxSize);
	private native byte[] _readBuf8Raw(int peerHandle2, int aMaxSize);
}
