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

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Container class for storing VCard properties for contact
 * 
 * @author krzysztofZielinski
 *
 */
public class VCardContactProperties implements IVCardContactProperties {

	Set<SimpleProperty> simpleProperties = new HashSet<SimpleProperty>();
	Set<ListProperty> listProperties = new HashSet<ListProperty>();
	Set<StructuredProperty> structuredProperties = new HashSet<StructuredProperty>();

    Set<SpeedDialVCardTemporaryData> speedDialVCardPropertiesData = new HashSet<SpeedDialVCardTemporaryData>();
	
	public Set<IProperty> getAllProperties() {
		Set<IProperty> allProperties = new HashSet<IProperty>();
		allProperties.addAll(simpleProperties);
		allProperties.addAll(listProperties);
		allProperties.addAll(structuredProperties);

		return Collections.unmodifiableSet(allProperties);
	}

	public Set<SimpleProperty> getSimpleProperties() {
		return simpleProperties;
	}

	public Set<ListProperty> getListProperties() {
		return listProperties;
	}

	public Set<StructuredProperty> getStructuredProperties() {
		return structuredProperties;
	}

	public void addListProperty(ListProperty property) {
		listProperties.add(property);
	}

	public void addSimpleProperty(SimpleProperty property) {
		simpleProperties.add(property);
	}

	public void addStructuredProperty(StructuredProperty property) {
		structuredProperties.add(property);
	}

	public void removeSimpleProperties(Set<IProperty> simplePropertiesToRemove) {
		this.simpleProperties.removeAll(simplePropertiesToRemove);
	}

	public void removeListProperties(Set<IProperty> listPropertiesToRemove) {
		this.listProperties.removeAll(listPropertiesToRemove);
	}

	public void removeStructuredProperties(Set<IProperty> structuredPropertiesToRemove) {
		this.structuredProperties.removeAll(structuredPropertiesToRemove);
	}

	/**
	 * @return the speedDialVCardPropertiesData
	 */
	public Set<SpeedDialData> getSpeedDialData() {
		Set<SpeedDialData> speedDialData = new HashSet<SpeedDialData>();
		speedDialData.addAll(speedDialVCardPropertiesData);
		return speedDialData;
	}

	/**
	 * @param speedDialVCardPropertiesData the speedDialVCardPropertiesData to set
	 */
	public void setSpeedDialVCardPropertiesData(
			Set<SpeedDialVCardTemporaryData> speedDialVCardPropertiesData) {
		this.speedDialVCardPropertiesData = speedDialVCardPropertiesData;
	}

	/**
	 * @return the speedDialVCardPropertiesData
	 */
	public Set<SpeedDialVCardTemporaryData> getSpeedDialVCardPropertiesData() {
		return speedDialVCardPropertiesData;
	}


}
