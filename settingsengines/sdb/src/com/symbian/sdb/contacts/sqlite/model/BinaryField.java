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

package com.symbian.sdb.contacts.sqlite.model;
/**
 * The class that encapsulate contact binary field  
 * @author Tanaslam1
 *
 */
public class BinaryField {
	
	/**
	 * size of field data in bytes   
	 */
	private int length = 0;
	
	/**
	 * streamId from binary field header 
	 */
	private FieldHeader header = null;
	
	/**
	 * Binary field contents
	 */
	private byte[] data = null;
	
	/**
	 * 
	 * 
	 */
	public BinaryField() {
		super();
		this.header = null;
		this.length = 0;
		this.data = null;
	}
	/**
	 *Constructor that initialise class members 
	 * @param length
	 * @param data
	 */
	public BinaryField(FieldHeader header, int length, byte[] data) {
		super();
		this.header = header;
		this.length = length;
		this.data = data;
	}

	/**
	 * returns binary field data length
	 * @return
	 */
	public int getLength() {
		return length;
	}
	
	/**
	 * set binary field data length
	 * @param length
	 */
	public void setLength(int length) {
		this.length = length;
	}
	
	/**
	 * get binary field contents in byte array
	 * @return
	 */
	public byte[] getData() {
		return data;
	}

	/**
	 * 
	 * @param data
	 */
	public void setData(byte[] data) {
		this.data = data;
	}

	public FieldHeader getHeader() {
		return header;
	}

	public void setHeader(FieldHeader header) {
		this.header = header;
	}
	
	
	
	
}
