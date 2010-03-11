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

package com.symbian.sdb.mode.flow.ced;

import java.io.File;
import java.io.IOException;
import java.util.Map;

/**
 * @author jamesclark
 *
 */
public interface IProcessBuilder {

	/**
	 * @see java.lang.ProcessBuilder#directory(File)
	 * @param exeDirectory
	 */
	ProcessBuilder directory(File exeDirectory);

	/**
	 * @see java.lang.ProcessBuilder#redirectErrorStream(boolean)
	 * @return
	 * @param exeDirectory
	 */
	ProcessBuilder redirectErrorStream(boolean redirectErrorStream);
	
	/**
	 * @see java.lang.ProcessBuilder#start()
	 * @return
	 * @throws IOException 
	 */
	Process start() throws IOException;

	/**
	 * @see java.lang.ProcessBuilder#directory()
	 * @return 
	 */
	File directory();
	
	/**
	 * @see java.lang.ProcessBuilder#environment()
	 * @return 
	 */
	Map<String, String> environment();
}
