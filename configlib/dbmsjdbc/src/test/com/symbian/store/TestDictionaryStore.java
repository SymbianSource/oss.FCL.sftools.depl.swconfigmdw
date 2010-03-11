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
import java.io.File;
import java.util.Arrays;

import junit.framework.TestCase;

public class TestDictionaryStore extends TestCase {

	private static final int removeStreamUid = 0xFFFFFFA0;
	DictionaryStore store;
	private final String storeName= "teststore.ini";
	private final int storeUid = 0xFFFFFFFA;
	private final int streamUid = 0xFFFFFFFB;
	private final int streamUid_revert = 0xFFFFFFFC;
	private final int streamUid_smoke = 0xFFFFFFFD;
	boolean dataWritten = false;
	
	//Test data
	private final int testData_int = 1234;
	private final String testData_str = "test string";
	private final byte[] testData_bytes  = {'a','b','c','d'};
	
	protected void setUp() throws Exception {
		super.setUp();
		store = new DictionaryStore(storeName, storeUid);
	}
	

	protected void tearDown() throws Exception {
		store.close();
		super.tearDown();
	}

	public void testDictionaryStore() {
		File storeFile = new File(storeName);
		if(!storeFile.exists()) {
			fail("store file didn't get created");
		}
	}

	public void testStreamIO() throws Exception {
		DictionaryStoreOutputStream ostream = (DictionaryStoreOutputStream) store.getOutputStream(streamUid);
		assertNotNull(ostream);
		ostream.writeInt32(testData_int);
		ostream.writeBuf8(testData_str);
		ostream.write(testData_bytes);
		ostream.close();
		store.commit();
		dataWritten = true;
		DictionaryStoreInputStream istream = (DictionaryStoreInputStream) store.getInputStream(streamUid);
		assertNotNull(istream);
		assertEquals(istream.getStreamId(), streamUid);
		assertEquals(istream.readInt32(), testData_int);
		assertEquals(istream.readBuf8(testData_str.length()), testData_str);
		byte[] bytes = new byte[testData_bytes.length];
		istream.read(bytes);
		assertTrue(Arrays.equals(bytes, testData_bytes));
		istream.close();
	}

	public void testClose() {
		store.close();
		assertEquals(store.getPeerHandle(), 0);
	}

	public void testRevert() throws Exception {
		DictionaryStoreOutputStream ostream = (DictionaryStoreOutputStream) store.getOutputStream(streamUid_revert);
		assertNotNull(ostream);
		ostream.writeInt32(testData_int);
		ostream.close();
		store.revert();
		DictionaryStoreInputStream istream = (DictionaryStoreInputStream) store.getInputStream(streamUid_revert);
		assertNotNull(istream);
		assertEquals(istream.getStreamId(), streamUid_revert);
		try {
			istream.readInt32();
			fail("No exception thrown where exception is expected");
		} catch (EOFException e) {
			// ignore expected exception
		}
		istream.close();
	}

	public void testIsNull() throws Exception {
		if(dataWritten) {
		assertTrue(store.isNull());
		}
		else {
			assertFalse(store.isNull());
		}
			
	}

	public void testIsPresent() throws Exception{
		if(dataWritten) {
			assertTrue(store.isPresent(streamUid));
		}
		else {
			assertFalse(store.isPresent(streamUid));
		}
	}
	
	public void testRemove() throws Exception{
		DictionaryStoreOutputStream ostream = (DictionaryStoreOutputStream) store.getOutputStream(removeStreamUid);
		assertNotNull(ostream);
		ostream.writeInt32(testData_int);
		ostream.close();
		store.commit();
		store.remove(removeStreamUid);
		store.commit();
		
		DictionaryStoreInputStream istream = null;
		try {
			istream = (DictionaryStoreInputStream) store.getInputStream(removeStreamUid);
			istream.readInt32();
			fail("Exception not thrown where expected");
		} catch (Exception e) {
			// expected exception
		} finally {
			istream.close();
		}
	}

	public void testGetPeerHandle() {
		assertTrue(store.getPeerHandle() > 0);
	}
	
	public void testSmoke() throws Exception {
		// positive lifecycle and data type marshalling test
		StoreOutputStream outstream = store.getOutputStream(streamUid_smoke);
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
		byte [] somebytes = "test".getBytes();
		outstream.writeBuf8Raw(somebytes);
		outstream.write(somebytes);
		outstream.writeDes16("lalala");
		outstream.writeDes8String("8lalala8");
		outstream.flush();
		outstream.close();
		
		store.commit();
		
		StoreInputStream in = store.getInputStream(streamUid_smoke);
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
		byte [] buf = new byte[somebytes.length];
		assertTrue(Arrays.equals(somebytes, in.readBuf8Raw(64)));
		assertEquals(somebytes.length, in.read(buf));
		assertTrue("test".equals(new String(buf)));
		assertEquals("lalala", in.readDes16(6));
		assertEquals("8lalala8", in.readDes8String(8));
		in.close();
		store.remove(streamUid_smoke);
	}
	
	public void testNegative() throws Exception {
		
		StoreOutputStream outstream = store.getOutputStream(streamUid_smoke);
		outstream.writeInt32(0x12345678);
		outstream.flush();
		outstream.close();
		
		store.commit();
		
		StoreInputStream in = store.getInputStream(streamUid_smoke);
		assertEquals(0x12345678, in.readInt32());
		// test that we throw an exception when readin beyond instream end
		try{
			in.readInt32();
			fail("Expected exception, but didn't get one");
		} catch(EOFException e) {
			// expected
		} finally {
			in.close();
			store.close();
		}

		// test that using closed store does not crash
		try {
			store.commit();
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
			store.getOutputStream(0);
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
	

}
