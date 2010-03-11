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
import java.io.OutputStream;

public abstract class StoreOutputStream extends OutputStream {
	int peerHandle;
	Store store;
	int id;
	boolean closed = false;

	StoreOutputStream(Store streamStore, int id)
			throws StoreException {
		this.store = streamStore;
		this.id = id;
	}

	StoreOutputStream(Store streamStore) 
			throws StoreException {
		this.store = streamStore;
	}


	public void write(byte b[]) throws IOException {
		write(b, 0, b.length);
	}

	public void flush() throws IOException {
		checkClosed();
		int result = _flush(peerHandle);
		if ( result != 0 ){
			throw new StoreException(result); 
		}
	}

	public void close() throws IOException {
		if (closed) {
			return;
		}
		try{
			flush();
		} finally{
			_close(peerHandle);
			peerHandle = 0;
			closed = true;
		}
	}

	public void write(int data) throws IOException {
		checkClosed();
		writeInt8((byte)(data&0xff));
	}

	public void write(byte data[], int off, int len) throws IOException {
		checkClosed();
		int result = _writeBytes(peerHandle, data, off, len);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeInt16(short data) throws IOException {
		checkClosed();
		int result = _writeInt16(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeInt32(int data) throws IOException {
		checkClosed();
		int result = _writeInt32(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeCardinality(int data) throws IOException {
		checkClosed();
		int result = _writeCardinality(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeInt8(byte data) throws IOException {
		checkClosed();
		int result = _writeInt8(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}


	public void writeReal32(float data) throws IOException {
		checkClosed();
		int result = _writeReal32(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

			
	public void writeReal64(double data) throws IOException {
		checkClosed();
		int result = _writeReal64(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeUInt32(long data) throws IOException {
		checkClosed();
		int result = _writeUInt32(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeUInt16(int data) throws IOException {
		checkClosed();
		int result = _writeUInt16(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeInt64(long data) throws IOException {
		checkClosed();
		int result = _writeInt64(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeUInt64(long data) throws IOException {
		checkClosed();
		int result = _writeUInt64(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeUInt8(short data) throws IOException {
		checkClosed();
		int result = _writeUInt8(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}


	public void writeDes16(String data) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		int result = _writeDes16(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeBuf16(String data) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		int result = _writeBuf16(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeBuf8(String data) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		int result = _writeBuf8(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}


	public void writeBuf8Raw(byte [] data) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		int result = _writeBuf8(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeDes16(short[] data, int from, int length) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		if ( from + length > data.length ) {
			throw new IOException("Buffer overflow");
		}
		checkClosed();
		int result = _writeDes16(peerHandle, data, from, length);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
	}

	public void writeDes8String(String data) throws IOException {
		if ( data == null ) {
			throw new NullPointerException();
		}
		checkClosed();
		int result = _writeDes8String(peerHandle, data);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
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
		return id;
	}

	public void setStreamId(int streamId) {
		this.id = streamId;
	}
	private native int _flush(int peerHandle2);
	private native void _close(int peerHandle);

	
	private native int _writeInt8(int peerHandle2, byte data);
	private native int _writeInt16(int peerHandle2, short data);
	private native int _writeInt32(int peerHandle2, int data);
	private native int _writeInt64(int peerHandle2, long data);
	private native int _writeUInt8(int peerHandle2, short data);
	private native int _writeUInt16(int peerHandle2, int data);
	private native int _writeUInt32(int peerHandle2, long data);
	private native int _writeUInt64(int peerHandle2, long data);
	private native int _writeReal32(int peerHandle2, float data);
	private native int _writeReal64(int peerHandle2, double data);
	private native int _writeBytes(int peerHandle2, byte[] data, int off, int len);
	private native int _writeDes8String(int peerHandle2, String data);
	private native int _writeDes16(int peerHandle2, short[] data, int from, int length);
	private native int _writeDes16(int peerHandle2, String data);
	private native int _writeCardinality(int peerHandle2, int data);
	private native int _writeBuf16(int peerHandle2, String data);
	private native int _writeBuf8(int peerHandle2, String data);
	private native int _writeBuf8(int peerHandle2, byte[] data);

}
