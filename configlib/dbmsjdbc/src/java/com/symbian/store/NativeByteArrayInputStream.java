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

public class NativeByteArrayInputStream extends InputStream {
	EmbeddedStore store = null;
	StoreInputStream in = null;
	
	public NativeByteArrayInputStream(byte [] data) throws IOException {
		int streamId = 0;
		byte [] storebytes = null;
		EmbeddedStore wrstore = null;
		StoreOutputStream sos = null;
		try {
			wrstore = new EmbeddedStore();
			sos = wrstore.getOutputStream();
			streamId = sos.getStreamId();
			sos.write(data);
			sos.close(); sos = null;
			wrstore.commit();
			storebytes = wrstore.getContent();
			wrstore.close(); wrstore = null;
		} finally {
			if ( sos != null ) try{ sos.close();}catch(Exception e){}
			if ( wrstore != null ) try{ wrstore.close();}catch(Exception e){}
		}
		store = new EmbeddedStore(storebytes);
		in = store.getInputStream(streamId);
	}
	
	public void close(){
		if ( in != null ) try{ in.close(); in = null;}catch(Exception e){}
		if ( store != null ) try{ store.close(); store = null;}catch(Exception e){}
	}

	public int read(byte b[]) throws IOException {
		return in.read(b);
	}

	public int read() throws IOException {
		return in.read();
	}

	public int read(byte b[], int off, int len) throws IOException {
		return in.read(b, off, len);
	}

	public short readInt16() throws IOException {
		return in.readInt16();
	}

	public int readInt32() throws IOException {
		return in.readInt32();
	}

	public int readCardinality() throws IOException {
		return in.readCardinality();
	}

	public byte readInt8() throws IOException {
		return in.readInt8();
	}

	public float readReal32() throws IOException {
		return in.readReal32();
	}

	public double readReal64() throws IOException {
		return in.readReal64();
	}

	public long readUInt32() throws IOException {
		return in.readUInt32();
	}

	public int readUInt16() throws IOException {
		return in.readUInt16();
	}

	public short readUInt8() throws IOException {
		return in.readUInt8();
	}

	public String readDes16(int length) throws IOException {
		return in.readDes16(length);
	}

	public int readDes16(short[] data, int length) throws IOException {
		return in.readDes16(data, length);
	}

	public String readDes16(char delimiter) throws IOException {
		return in.readDes16(delimiter);
	}

	public String readBuf16(int maxSize) throws IOException {
		return in.readBuf16(maxSize);
	}


	public String readBuf8(int maxSize) throws IOException {
		return in.readBuf8(maxSize);
	}

	public byte[] readBuf8Raw(int maxSize) throws IOException {
		return in.readBuf8Raw(maxSize);
	}

	public int readDes16(short[] data, char delimiter) throws IOException {
		return in.readDes16(data, delimiter);
	}
	
	public int readDes8(byte[] data, char delimiter) throws IOException {
		return in.readDes8(data, delimiter);
	}
	
	public String readDes8String(char delimiter) throws IOException {
		return in.readDes8String(delimiter);
	}

	public String readDes8String(int length) throws IOException {
		return in.readDes8String(length);
	}

	public boolean isClosed() {
		return in.isClosed();
	}
	public void finalize(){
		close();
	}
}
