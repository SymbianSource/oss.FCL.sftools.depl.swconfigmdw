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
import java.util.List;
import java.util.Map;


/**
 * @author jamesclark
 * 
 */
public class ProxyProcessBuilder implements IProcessBuilder {

	private ProcessBuilder _delegate;

	/**
	 * 
	 */
	public ProxyProcessBuilder(List<String> args) {
		_delegate = new ProcessBuilder(args);
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * com.symbian.sdb.mode.flow.ced.IProcessBuilder#redirectErrorStream(boolean)
	 */
	public ProcessBuilder redirectErrorStream(boolean redirectErrorStream){
		return _delegate.redirectErrorStream(redirectErrorStream);
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * com.symbian.sdb.mode.flow.ced.IProcessBuilder#directory(java.io.File)
	 */
	public ProcessBuilder directory(File exeDirectory) {
		return _delegate.directory(exeDirectory);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#start()
	 */
	public Process start() throws IOException {
		return _delegate.start();
	}
	/* (non-Javadoc)
	 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#directory()
	 */
	public File directory() {
		return _delegate.directory();
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.mode.flow.ced.IProcessBuilder#environment()
	 */
	public Map<String, String> environment() {
		return _delegate.environment();
	}

}
