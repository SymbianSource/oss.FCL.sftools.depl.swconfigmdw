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

import java.io.EOFException;
import java.io.OutputStream;
import java.util.Arrays;

import junit.framework.TestCase;

public class TestStore extends TestCase {

	protected void setUp() throws Exception {
		super.setUp();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testTransform() {
		byte [] bytes = { 
				0x04, 0x00, 0x00, 0x00,
				0x06, 
				0x78, 0x56, 0x34, 0x12
		};
		String text = "040000000678563412";		
		assertTrue(Arrays.equals(bytes, transformToBytesArray(text)));
	}
	
    private byte[] transformToBytesArray(String hexString) {
        byte[] bytes = new byte[hexString.length()/2];
        for (int index = 0, byteCounter = 0; index < hexString.length(); index+=2) {
            String hex2ByteString = hexString.substring(0+index, 2+index);
            
            byte value = (byte) Short.parseShort(hex2ByteString,16);
            bytes[byteCounter++] = value;
        }
        return bytes;
    }

	
	public void testSmoke2() throws Exception {
		byte [] bytes = { 
				0x04, 0x00, 0x00, 0x00,
				0x06, 
				0x78, 0x56, 0x34, 0x12
		};
		EmbeddedStore readStore = new EmbeddedStore(bytes);
		StoreInputStream in = readStore.getInputStream(readStore.rootStream());
		assertEquals(6, in.readUInt8());
		assertEquals(0x12345678, in.readUInt32());
		in.close();
		readStore.close();
	}
	
	
	public void testCardinality() throws Exception {
		EmbeddedStore store =  new EmbeddedStore();
		StoreOutputStream outstream = store.getOutputStream();
		int streamId = outstream.getStreamId();
		store.setRoot(streamId);
		for ( int i = 0; i < 0x1ffffff; i = 3*i + 1 ){ 
			outstream.writeCardinality(i);
		}
		outstream.flush();
		outstream.close();
		outstream = null;
		store.commit();
		byte[] bytes = store.getContent();
		store.close();
		
		// Note - you can't use the same EmbeddedStore instance for reading and writing 
		EmbeddedStore readStore = new EmbeddedStore(bytes);
		StoreInputStream in = readStore.getInputStream(readStore.rootStream());
		for ( int i = 0; i < 0x1ffffff; i = 3*i + 1 ){ 
			assertEquals(i, in.readCardinality());
		}
		in.close();
		readStore.close();
	}
	
	public void testSmoke() throws Exception {
		// positive lifecycle and data type marshalling test
		
		EmbeddedStore store =  new EmbeddedStore();
		StoreOutputStream outstream = store.getOutputStream();
		int streamId = outstream.getStreamId();
		outstream.writeInt32(0x12345678);
		outstream.writeInt16((short)0x1234);
		outstream.writeInt8((byte)0x12);
		outstream.writeUInt32(0x12345678L);
		outstream.writeUInt16(0x1234);
		outstream.writeUInt8((short)0x12);
		outstream.writeUInt32(0x82345678L);
		outstream.writeUInt16(0x8234);
		outstream.writeUInt8((short)0x82);
		outstream.writeReal32(0.12345F);
		outstream.writeReal64(0.12345678);
		outstream.writeUInt64(0x0123456789ABCDEFL);
		outstream.writeInt64(0x0123456789ABCDEFL);
		byte [] somebytes = "test".getBytes();
		outstream.writeBuf8Raw(somebytes);
		outstream.write(somebytes);
		outstream.writeDes16("lalala");
		outstream.writeDes8String("8lalala8");
		outstream.flush();
		outstream.close();
		outstream = null;
		store.commit();
		byte[] bytes = store.getContent();
		store.close();
		store = null;
		
		// Note - you can't use the same EmbeddedStore instance for reading and writing 
		EmbeddedStore readStore = new EmbeddedStore(bytes);
		StoreInputStream in = readStore.getInputStream(streamId);
		assertEquals(0x12345678, in.readInt32());
		assertEquals(0x1234, in.readInt16());
		assertEquals(0x12, in.readInt8());
		assertEquals(0x12345678, in.readUInt32());
		assertEquals(0x1234, in.readUInt16());
		assertEquals(0x12, in.readUInt8());
		assertEquals(0x82345678L, in.readUInt32());
		assertEquals(0x8234, in.readUInt16());
		assertEquals(0x82, in.readUInt8());
		assertEquals(0.12345F, in.readReal32());
		assertEquals(0.12345678, in.readReal64());
		assertEquals(0x0123456789ABCDEFL, in.readUInt64());
		assertEquals(0x0123456789ABCDEFL, in.readInt64());
		//0x0123456789ABCDEFL
		byte [] buf = new byte[somebytes.length];
		assertTrue(Arrays.equals(somebytes, in.readBuf8Raw(64)));
		assertEquals(somebytes.length, in.read(buf));
		assertTrue("test".equals(new String(buf)));
		assertEquals("lalala", in.readDes16(6));
		assertEquals("8lalala8", in.readDes8String(8));
		in.close();
		readStore.close();
	}
	
	public void testNegative() throws Exception {
		EmbeddedStore store =  new EmbeddedStore();
		StoreOutputStream outstream = store.getOutputStream();
		int streamId = outstream.getStreamId();
		store.setRoot(streamId);
		outstream.writeInt32(0x12345678);
		
		outstream.flush();
		outstream.close();
		store.commit();
		byte[] bytes = store.getContent();
		store.close();
		
		EmbeddedStore readStore = new EmbeddedStore(bytes);
		StoreInputStream in = readStore.getInputStream(readStore.rootStream());
		assertEquals(0x12345678, in.readInt32());
		// test that we throw an exception when readin beyond instream end
		try{
			in.readInt32();
			fail("Expected exception, but didn't get one");
		} catch(EOFException e) {
			// expected
		} finally {
			in.close();
			readStore.close();
		}

		// test that using closed store does not crash
		try {
			store.commit();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.compact();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}

		try {
			store.delete(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.extend();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.getInputStream(0);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.getOutputStream();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.getOutputStream(0);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}

		try {
			store.getContent();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}

		try {
			store.reclaim();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.revert();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
		try {
			store.rootStream();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}		
		
	
		
		// test that using closed streams does not crash VM
		try {
			outstream.write(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.write("lala".getBytes());
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeDes16("lala");
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			short[] data = { 1,2,3};
			outstream.writeDes16(data, 0, data.length);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeDes8String("lala");
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeInt16((short)1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeInt32(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeInt8((byte)1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeUInt16(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeUInt32(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeUInt8((short)1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeInt16((short)1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeInt32(1);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeReal32(.5F);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.writeReal64(.5F);
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		try {
			outstream.flush();
			fail ( "No exception when one was expected " );
		} catch ( Exception e ) {
			// expected
		}
		
	}
	
	public void testMultipleStreams() throws Exception {
		// create store
		EmbeddedStore store =  new EmbeddedStore();
		// create a new stream
		StoreOutputStream outstream = store.getOutputStream();
		// get the stream id
		int streamId = outstream.getStreamId();
		// write some data into the stream
		outstream.writeInt32(0x12345678);
		
		// flush/close the stream - store remains open
		outstream.flush();
		outstream.close();

		// create another stream in this store
		outstream = store.getOutputStream();
		// save the stream id so we can read
		int streamId2 = outstream.getStreamId();
		// write some data
		outstream.writeInt32(0xABCD1234);
		outstream.writeCardinality(0xBCD1234);
		outstream.writeBuf8("some string");
		outstream.writeBuf16("another string");
		
		// close the second stream
		outstream.flush();
		outstream.close();

		// 'commit' store
		store.commit();
		
		// get the store contents as a byte array, then dismantle
		byte[] bytes = store.getContent();
		store.close();
		store = null;
//		System.out.println(hexDump(bytes));
		// check all was ok
		EmbeddedStore readStore = new EmbeddedStore(bytes);
		// open the first stream 
		StoreInputStream in = readStore.getInputStream(streamId);
		// make sure data is correct
		assertEquals(0x12345678, in.readInt32());
		in.close();
		// open the second stream
		in = readStore.getInputStream(streamId2);
		// verify
		assertEquals(0xABCD1234, in.readInt32());
		assertEquals(0xBCD1234, in.readCardinality());
		assertEquals("some string", in.readBuf8(128));
		assertEquals("another string", in.readBuf16(128));
		
		// all fine, close
		in.close();
		readStore.close();
	}
	
	public void testForLeaksAndPerformance() throws Exception {
		int numruns = 100000;
		long memstart = memUsage();
		long starttime = System.currentTimeMillis();
		for ( int i = 0 ; i < numruns; i ++ ) {
			testMultipleStreams();
		}
		long endtime = System.currentTimeMillis();
		long memend = memUsage();
		System.out.println("Mem start : " + memstart + ", mem end : " + memend);
		int seconds = (int)((endtime-starttime)/1000);
		System.out.println(""+numruns+" multi-stream read-write tests took around: " + seconds + " seconds ");
		if ( memend > memstart + 100000) {
			fail("Are we realeasing all memory?");
		}
		if ( seconds > 10 ) {
			fail("Performance seems to be lower than expected.");
		}
	}
	private long memUsage() {
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		System.gc();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		Runtime rt = Runtime.getRuntime();
		return rt.totalMemory() - rt.freeMemory();
	}
	
	public String hexDump(byte [] bytes) {
		char [] chars = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
		StringBuilder sb = new StringBuilder();
		for ( int i = 0 ; i < bytes.length ; i ++ ) {
			int hi = (bytes[i]>>4) & 0xf;
			int lo = bytes[i] & 0xf;
			sb.append(chars[hi]);
			sb.append(chars[lo]);
			if ( i % 4 == 3 ) {
				sb.append(' ');
			}
			if ( i % 16 == 15 ) {
				sb.append('\n');
			}
		}
		return sb.toString();
	}
	
	public void testCreateOutStreamWithId() throws Exception { 
		EmbeddedStore store = new EmbeddedStore();
		try{
		OutputStream os = store.getOutputStream(4);
		} catch(StoreException e) {
			assertEquals(e.getMessage(), "The operation requested is not supported [KErrNotSupported]");
		} finally {
			store.close();
		}
	}
}
