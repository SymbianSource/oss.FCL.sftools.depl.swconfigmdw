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

import java.io.ByteArrayOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.OutputStream;

public class NativeByteArrayOutputStream extends OutputStream {
	EmbeddedStore store = null;
	StoreOutputStream out = null;
	int streamId = 0;
	
	public NativeByteArrayOutputStream() throws IOException {
		store = new EmbeddedStore();
		out = store.getOutputStream();
		streamId = out.getStreamId();
	}


	public byte [] toByteArray() throws IOException{
		out.close(); out = null;
		store.commit();
		byte [] storebytes = store.getContent();
		store.close(); store = null;
		EmbeddedStore rdstore = null;
		StoreInputStream sin = null;
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		try{
			rdstore = new EmbeddedStore(storebytes);
			sin = rdstore.getInputStream(streamId);
			int rd = sin.read();
			while(rd >= 0 ) {
				baos.write(rd);
				rd = sin.read();
			}
		} catch(EOFException e) {
		} finally {
			if ( sin != null ) try{ sin.close(); sin = null;}catch(Exception e){}
			if ( rdstore != null ) try{ rdstore.close(); rdstore = null;}catch(Exception e){}
		}
		return baos.toByteArray();
	}

	public void write(int b) throws IOException {
		out.write(b);
	}

	public void write(byte b[]) throws IOException {
		write(b, 0, b.length);
	}

	public void flush() throws IOException {
		out.flush();
	}

	public void close() throws IOException {
		out.close();
	}

	public void write(byte data[], int off, int len) throws IOException {
		out.write(data, off, len);
	}

	public void writeInt16(short data) throws IOException {
		out.writeInt16(data);
	}

	public void writeInt32(int data) throws IOException {
		out.writeInt32(data);
	}

	public void writeCardinality(int data) throws IOException {
		out.writeCardinality(data);
	}

	public void writeInt8(byte data) throws IOException {
		out.writeInt8(data);
	}


	public void writeReal32(float data) throws IOException {
		out.writeReal32(data);
	}

			
	public void writeReal64(double data) throws IOException {
		out.writeReal64(data);
	}

	public void writeUInt32(long data) throws IOException {
		out.writeUInt32(data);
	}

	public void writeUInt16(int data) throws IOException {
		out.writeUInt16(data);
	}

	public void writeUInt8(short data) throws IOException {
		out.writeUInt8(data);
	}


	public void writeDes16(String data) throws IOException {
		out.writeDes16(data);
	}

	public void writeBuf16(String data) throws IOException {
		out.writeBuf16(data);
	}

	public void writeBuf8(String data) throws IOException {
		out.writeBuf8(data);
	}


	public void writeBuf8Raw(byte [] data) throws IOException {
		out.writeBuf8Raw(data);
	}

	public void writeDes16(short[] data, int from, int length) throws IOException {
		out.writeDes16(data, from, length);
	}

	public void writeDes8String(String data) throws IOException {
		out.writeDes8String(data);
	}

	public boolean isClosed() {
		return out.isClosed();
	}
}
