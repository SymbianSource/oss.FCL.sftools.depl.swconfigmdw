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

package com.symbian.store;

import java.io.File;

public class DictionaryStore implements Store {
	int peerHandle;
	int KErrNone = 0;
	
	static {
//		try{  
//            String libpath = System.getProperty("com.symbian.dbms.lib.path");
//            String libname = System.getProperty("com.symbian.dbms.lib.name");
//            if(libpath == null)
//            {
//                System.loadLibrary("dbmsjdbc");
//            } else
//            {
//                if(libname == null)
//                    libname = System.mapLibraryName("dbmsjdbc");
//                System.load((new File(libpath, libname)).getAbsolutePath());
//            }
//		} catch ( Exception e) {
//			e.printStackTrace();
//		}
		try{  
	        String libpath = System.getProperty("com.symbian.dbms.lib.path");
	        
	        // Build system builds dlls with preceding 'lib' on both windows and 
	        // linux. Linux loader expects library name without preceding 'lib'
	        // while Windows loader expects file name without extension.
	        // Using prefix for windows only resolves the problem.
	        
	        String libPrefix = "";
	        if ( System.getProperty("os.name").toLowerCase().indexOf("win") != -1) {
	        	libPrefix = "lib";
	        }
            String symportLibName = libPrefix+"symport";
	        String driverLibName = libPrefix+"dbmsjdbc";
	        if (libpath == null) {
	            System.loadLibrary(symportLibName);
	            System.loadLibrary(driverLibName);
	        } else {
	            System.load(new File(libpath, System.mapLibraryName(symportLibName)).getAbsolutePath());
	            System.load(new File(libpath, System.mapLibraryName(driverLibName)).getAbsolutePath());
	        }
		} catch ( Exception e) {
			e.printStackTrace();
		}
	}
		
	public DictionaryStore(String fileName, int uid3)throws StoreException {
		int inres = _initNative();
		if ( inres != KErrNone ) {
			throw new StoreException(inres);
		}
		int result = _create(fileName, uid3);
		if (result <= 0) {
			throw new StoreException(result);
		}
		peerHandle = result;
	}
	

	public StoreInputStream getInputStream(int uid) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		return new DictionaryStoreInputStream(this, uid);
	}
	
	public StoreOutputStream getOutputStream(int uid) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		return new DictionaryStoreOutputStream(this, uid);
	}
	
	public void close() {
		if( peerHandle > 0 ) {
			_close(peerHandle);
			peerHandle = 0;
		}
	}

	public void commit() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _commit(peerHandle);
		if ( result != KErrNone ) {
			throw new StoreException(result);
		}
	}

	public void revert() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _revert(peerHandle);
		if ( result != KErrNone ) {
			throw new StoreException(result);
		}
	}
	
	public void remove(int uid) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _remove(peerHandle, uid);
		if ( result != KErrNone ) {
			throw new StoreException(result);
		}
	}
	
	/**
	 * Tests whether the dictionary stores stream dictionary is empty.
	 * @return true if empty, false otherwise
	 */
	public boolean isNull() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _isNull(peerHandle);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
		return result==0?false:true;
	}

	public boolean isPresent(int uid) throws StoreException{
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _isPresent(peerHandle, uid);
		if ( result < 0 ) {
			throw new StoreException(result);
		}
		return result==0?false:true;
	} 

	public int getPeerHandle() {
		return peerHandle;
	}
	
	private native int _initNative();
	private native int _create(String fileName, int uid3);
	private native void _close(int peerHandle);
	private native int _commit(int peerHandle);
	private native int _revert(int peerHandle); 
	private native int _remove(int peerHandle, int uid);
	private native int _isNull(int peerHandle);
	private native int _isPresent(int peerHandle, int uid);
}
