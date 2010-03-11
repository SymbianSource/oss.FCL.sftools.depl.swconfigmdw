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

package com.symbian.sdb.util;

import java.io.IOException;

import com.symbian.store.NativeByteArrayInputStream;
import com.symbian.store.NativeByteArrayOutputStream;

public class IntArray {
	int [] array;
	int count;
	public IntArray(){
		array = new int[10];
		count = 0;
	}
	public IntArray(int size){
		array = new int[size];
		count = 0;
	}
	public void clear(){
		count = 0;
	}
	public void add(int a) {
		if ( count == array.length ) {
			// grow array
			int [] newarray = new int[2*array.length];
			System.arraycopy(array, 0, newarray, 0, array.length);
			array = newarray;
		}
		array[count] = a;
		count++;
	}
	public int size(){
		return count;
	}
	public int get(int pos) {
		if ( pos > count || pos < 0 ) {
			throw new ArrayIndexOutOfBoundsException();
		}
		return array[pos];
	}
	public int[] getAsArray(){
		int [] ret = new int[count];
		System.arraycopy(array, 0, ret, 0, count);
		return ret;
	}
	
	/**
	 * Parses an int array from a blob used for preferences and groups2 tables.
	 * 
	 * The array is stored as a sequence of 32-bit integers<p>
	 * 
	 * array-len [array-element]*
	 * 
	 * 
	 * @param blob
	 * @return
	 * @throws IOException
	 */
	public static IntArray parseBlob(byte[] blob) throws IOException {
		IntArray ret = null;
		NativeByteArrayInputStream in = null;
		try {
			in = new NativeByteArrayInputStream(blob);
			int count = in.readInt32();
			ret = new IntArray(count);
			for ( int i = 0 ; i < count ; i ++) {
				ret.add(in.readInt32());
			}
		} finally {
			if ( in != null ) { try{in.close();in=null;}catch(Exception e){}}
		}
		return ret;
	}

	/**
	 * Creates the blob from an int array - used for preferences and groups2 tables.
	 * 
	 * The array is stored as a sequence of 32-bit integers<p>
	 * 
	 * array-len [array-element]*
	 * 
	 * 
	 * @param blob
	 * @return
	 * @throws IOException
	 */
	public static byte [] makeBlob(IntArray array) throws IOException {
		if ( array == null ) {
			return null;
		}
		NativeByteArrayOutputStream out = null;
		byte [] blob = null;
		int [] list = array.getAsArray();
		try{
			out = new NativeByteArrayOutputStream();
			out.writeInt32(list.length);
			for (int i = 0; i < list.length; i++) {
				out.writeInt32(list[i]);
			}
			blob = out.toByteArray();
		} finally {
			if ( out != null ) { try{out.close();out=null;}catch(Exception e){}}
		}
		return blob;
	}

}