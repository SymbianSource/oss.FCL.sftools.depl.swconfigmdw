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

import java.util.Set;

/**
 * Represents container interface for storing VCard properties for contact
 * 
 * @author krzysztofZielinski
 *
 */
public interface IVCardContactProperties {

	public Set<IProperty> getAllProperties();

	public Set<SimpleProperty> getSimpleProperties();
	public Set<ListProperty> getListProperties();
	public Set<StructuredProperty> getStructuredProperties();
	
	public void addSimpleProperty(SimpleProperty property);
	public void addListProperty(ListProperty property);
	public void addStructuredProperty(StructuredProperty property);

	public void removeSimpleProperties(Set<IProperty> simplePropertiesToRemove);
	public void removeListProperties(Set<IProperty> listPropertiesToRemove);
	public void removeStructuredProperties(Set<IProperty> structuredPropertiesToRemove);

	/**
	 * @return the speedDialVCardPropertiesData
	 */
	public Set<SpeedDialData> getSpeedDialData();

	/**
	 * @param speedDialVCardPropertiesData the speedDialVCardPropertiesData to set
	 */
	public void setSpeedDialVCardPropertiesData(Set<SpeedDialVCardTemporaryData> speedDialVCardPropertiesData);

	/**
	 * @return the speedDialVCardPropertiesData
	 */
	public Set<SpeedDialVCardTemporaryData> getSpeedDialVCardPropertiesData();
}
