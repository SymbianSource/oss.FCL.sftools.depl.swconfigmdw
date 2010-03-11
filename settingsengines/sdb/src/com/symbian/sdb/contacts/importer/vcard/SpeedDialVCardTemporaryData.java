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

package com.symbian.sdb.contacts.importer.vcard;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.importer.VCardParseException;

/**
 * Class responsible for keeping temporary speed dial data when parsing vcard file.
 *
 */
public class SpeedDialVCardTemporaryData implements SpeedDialData {

	public static final String SPEEDDIAL_VCARD_PROPERTY_NAME = "X-SPEEDDIAL";
	private String speedDialIndex;
	private String speedDialVCardField;
	private String speedDialValue;
	
	/**
	 * @param speedDialIndex
	 * @param speedDialVCardField
	 */
	private SpeedDialVCardTemporaryData(String speedDialIndex,
			String speedDialVCardField) {
		super();
		this.speedDialIndex = speedDialIndex;
		this.speedDialVCardField = speedDialVCardField;
		
		int speedDialIndexInteger = Integer.parseInt(speedDialIndex);
		if (!(speedDialIndexInteger > 0) || !(speedDialIndexInteger <= 9))	{
			throw new ContactsExeption("Incorrect speed dial index number: " + speedDialIndex + ", it should be number between 1 and 9");
		}
	}

	/**
	 * @param speedDialProperty
	 * @return
	 * @throws VCardParseException
	 */
	public static SpeedDialVCardTemporaryData valueOf(SimpleProperty speedDialProperty)  throws VCardParseException	{
		// speedDialProperty should be in the following format: X-SPEEDDIAL:<Speed dial value>:<Speed dial field> 
		
		if (!isSpeedDialProperty(speedDialProperty))	{
			throw new VCardParseException("Unexpected vcard property: " + speedDialProperty.getName() + ", property " + 1 + " was expected.");			
		}

		String speedDialData = new String(speedDialProperty.getValue());
		String[] speedDialDataParts = speedDialData.split(":",2);
		
		if (speedDialDataParts.length != 2)	{
			throw new VCardParseException("Speed Dial vcard property (" + speedDialProperty.getName() + ") value is not in X-SPEEDDIAL:<Speed dial value>:<Speed dial field> format: " + speedDialData);
		}
		
		return new SpeedDialVCardTemporaryData(speedDialDataParts[0], speedDialDataParts[1]);
	}

	/**
	 * @param simpleProperty
	 */
	public static boolean isSpeedDialProperty(SimpleProperty simpleProperty) {
		return SPEEDDIAL_VCARD_PROPERTY_NAME.equals(simpleProperty.getName());
	}

	/**
	 * @param matchedProperty
	 * @return
	 * @throws VCardParseException
	 */
	public boolean matchesVCardProperty(SimpleProperty matchedProperty) throws VCardParseException {
		String speedDialPropertyElements[] = this.speedDialVCardField.toUpperCase().split(":");
		
		if (speedDialPropertyElements.length < 2)	{
			throw new VCardParseException("Invalid vcard field for speed dial assignment: " + this.speedDialVCardField);
		}
		String speedDialPropertyName = speedDialPropertyElements[0]; 
		List<String> speedDialPropertyParameters = Arrays.asList(speedDialPropertyElements).subList(1, speedDialPropertyElements.length);
		
		List<String> matchedPropertyParameters = new ArrayList<String>();
		for (String parameter : matchedProperty.getParameters().getValuesForTypeParameter()) {
			matchedPropertyParameters.add(parameter.toUpperCase());
		}
		
		// case insensitive comparison
		if (matchedProperty.getName().toUpperCase().equals(speedDialPropertyName.toUpperCase()))	{
			if (matchedPropertyParameters.containsAll(speedDialPropertyParameters))	{
				return true;
			}
		}
		
		return false;
	}

	/**
	 * @param simpleProperty
	 */
	public void setValue(SimpleProperty simpleProperty) {
		if (matchesVCardProperty(simpleProperty))	{
			this.speedDialValue = new String(simpleProperty.getValue());	
		} else {
			throw new ContactsExeption("Cannot set value from incompatible vcard property.");
		}
	}

	public String getSpeedDialvCardValue() {
		return speedDialVCardField;
	}
	
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.importer.vcard.SpeedDialData#getSpeedDialIndex()
	 */
	public int getSpeedDialIndex() {
		return Integer.parseInt(speedDialIndex);
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.importer.vcard.SpeedDialData#getSpeedDialValue()
	 */
	public String getSpeedDialValue() {
		return speedDialValue;
	}
}
