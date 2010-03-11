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

package com.symbian.sdb.util;

import java.util.List;

import com.symbian.sdb.mode.flow.ced.IProcessBuilder;
import com.symbian.sdb.mode.flow.ced.ProxyProcessBuilder;

/**
 * @author jamesclark
 *
 */
public class ProcessBuilderFactory {

	public static IProcessBuilder getProcessBuilder(List<String> commandParameters){
		return new ProxyProcessBuilder(commandParameters);
	}
	/*
	public static ProcessBuilder getProcessBuilder(List<String> commandParameters){
		return new ProcessBuilder(commandParameters);
	}
	*/
}
