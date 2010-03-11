// Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.contacts.importer.vcard;

import java.io.File;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.model.ContactImpl;

public class SpeedDialValidator {
	private Map<File, Set<SpeedDialData>> speedDialFromFiles = new HashMap<File, Set<SpeedDialData>>();
	
    /**
     * every specified key must have valid number assigned - if no such number is specified in vCard 
     * ContactsException will be thrown
     * @param vCardFile
     * @param contacts
     */
	public void addSpeedDialDataFromFile(File vCardFile, Set<ContactImpl> contacts) {
		speedDialFromFiles.put(vCardFile, new HashSet<SpeedDialData>());

    	for (ContactImpl contact : contacts) {
    		for (SpeedDialData speedDial : contact.getSpeedDialData()) {
    			if (speedDial.getSpeedDialValue() == null) {
    			   	//matching property wasn't found
    				throw new ContactsExeption("vCard field " 
    						+ speedDial.getSpeedDialvCardValue() 
    						+ " specified for speed dial key " 
    						+ speedDial.getSpeedDialIndex() 
    						+ " not found in the vCard: " + vCardFile.getAbsolutePath());
    			} 
    		}
    		speedDialFromFiles.get(vCardFile).addAll(contact.getSpeedDialData());
    	}
	}
	
    /**
     * only one number per key can be assigned - if more than one number is assigned 
     * to specific key ContactsException will be thrown
     */
	public void validate() {
		validateSpeedDialNotDoubled(speedDialFromFiles);
	}

    
    /**
     * only one number per key can be assigned - if more than one number is assigned 
     * to specific key ContactsException will be thrown
     * @param Map<File, Set<SpeedDialData>> data
     */
    protected void validateSpeedDialNotDoubled(Map<File, Set<SpeedDialData>> data) {
    	Map<Integer, File> assignedSpeedDial = new HashMap<Integer, File>();
    	
    	for (File vCardFile : data.keySet()) {
    		for (SpeedDialData speedDial : data.get(vCardFile)) {
    			if (assignedSpeedDial.keySet().contains(speedDial.getSpeedDialIndex())) {

    				String errorMessage = "Speed dial key %d defined ";
    				File previousVCard = assignedSpeedDial.get(speedDial.getSpeedDialIndex());
    				if (vCardFile.equals(previousVCard)) {
    					errorMessage += "twice in vCard %s";
    				} else {
    					errorMessage += "in vCard %s and in vCard %s";
    				}   				
    				throw new ContactsExeption(String.format(errorMessage, 
    						speedDial.getSpeedDialIndex(), 
    						vCardFile.getAbsolutePath(), 
    						previousVCard.getAbsolutePath()));
    			} else {
    				assignedSpeedDial.put(speedDial.getSpeedDialIndex(), vCardFile);
    			}		
    		}

    	}
    }
}
