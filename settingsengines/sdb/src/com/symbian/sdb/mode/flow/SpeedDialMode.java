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



package com.symbian.sdb.mode.flow;

import java.io.File;

/**
 * @author krzysztofZielinski
 *
 */
public class SpeedDialMode {

	private SpeedDialModeType speediDialModeType;
	private File speedDialIniFile;
	
	public SpeedDialMode(SpeedDialModeType speediDialModeType, File speedDialIniFile) {
		super();
		this.speediDialModeType = speediDialModeType;
		this.speedDialIniFile = speedDialIniFile;
	}

	public SpeedDialModeType getSpeediDialModeType() {
		return speediDialModeType;
	}

	public File getSpeedDialIniFile() {
		return speedDialIniFile;
	}

	public boolean isNone() {
		return getSpeediDialModeType().equals(SpeedDialModeType.NONE);
	}
}
