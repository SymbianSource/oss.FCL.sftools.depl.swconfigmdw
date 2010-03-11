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

import java.io.File;

import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;

/**
 * @author krzysztofZielinski
 *
 */
public interface SpeedDialIniFileManager {

	/**
	 * @param any
	 * @param string
	 */
	void createNewFile(SpeedDialDataRepository speedDialDataRepository, File iniFile);

	public SpeedDialDataRepository readFile(File iniFile);

}
