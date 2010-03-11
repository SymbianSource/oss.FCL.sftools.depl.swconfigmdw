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



package com.symbian.sdb.contacts.speeddial;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Represents all the data provided by user assigning phone number with speed dial number
 * Potentially multiple assignment
 * 
 * @author krzysztofZielinski
 *
 */
public class SpeedDialAssignmentData {

	private Set<SpeedDialAssignmentEntry> speedDialAssignmentEntries = new HashSet<SpeedDialAssignmentEntry>();
	
	public Set<SpeedDialAssignmentEntry> getAllEntries()	{
		return Collections.unmodifiableSet(this.speedDialAssignmentEntries);
	}
	
	public SpeedDialAssignmentData addEntry(SpeedDialAssignmentEntry newSpeedDialAssignmentEntry)	{
		this.speedDialAssignmentEntries.add(newSpeedDialAssignmentEntry);
		return this;
	}
}
