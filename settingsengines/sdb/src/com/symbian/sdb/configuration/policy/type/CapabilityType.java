// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.configuration.policy.type;
/**
 * This enum represents the allowed set of capabilities
 * a user can set
 * @author stephenroberts
 *
 */
public enum CapabilityType {

	TCB(0),
	COMMDD(1),
	POWERMGMT(2),
	MULTIMEDIADD(3),
	READDEVICEDATA(4),
	WRITEDEVICEDATA(5),
	DRM(6),
	TRUSTEDUI(7),
	PROTSRV(8),
	DISKADMIN(9),
	NETWORKCONTROL(10),
	ALLFILES(11),
	SWEVENT(12),
	NETWORKSERVICES(13),
	LOCALSERVICES(14),
	READUSERDATA(15),
	WRITEUSERDATA(16),
	LOCATION(17),
	SURROUNDINGSDD(18),
	USERENVIRONMENT(19),		
	NONE(-1)
	;
	
	private Integer fValue;
	
	private CapabilityType(int aArg){
		fValue = aArg;
	}
	
	public byte toByte(){
		return fValue.byteValue();
	}
}

