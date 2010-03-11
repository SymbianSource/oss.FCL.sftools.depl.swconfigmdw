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



package com.symbian.sdb.contacts.model;
/**
 * Model class for contact field label
 * @author tanaslam1
 */
public class ContactFieldLabel {
	
	/**
	 * Label length
	 */
	private int length = 0;
	
	/**
	 * Field label
	 */
	private String label = "";
	
	/**
	 * Return label length
	 * @return
	 */
	public int getLength() {
		return length;
	}
	
	/**
	 * Set field label length 
	 * @param length 
	 */
	public void setLength(int length) {
		this.length = length;
	}
	
	/**
	 * Return field label string
	 * @return
	 */
	public String getLabel() {
		return label;
	}
	
	/**
	 * Set field label 
	 * @param lable
	 */
	public void setLabel(String label) {
		this.label = label;
	}
	
} //End of class
