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
import java.io.InputStream;
import java.io.OutputStream;

public abstract class StreamStore implements Store {
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
	
	protected StreamStore() {
		_initNative();
	}

	protected StreamStore(int peerHandle ) {
		this.peerHandle = peerHandle;
	}
	
	public StoreInputStream getInputStream(int streamId) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		return new EmbeddedStoreInputStream(this, streamId);
	}
	
	public StoreOutputStream getOutputStream(int streamId) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		return new EmbeddedStoreOutputStream(this, streamId);
	}
	
	public StoreOutputStream getOutputStream() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		return new EmbeddedStoreOutputStream(this);
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
	
	public int compact() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _compact(peerHandle);
		if ( result < KErrNone ) {
			throw new StoreException(result);
		}
		return result;
	}
	
	public void delete(int streamId) throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _delete(peerHandle, streamId);
		if ( result != KErrNone ) {
			throw new StoreException(result);
		}
	}
	
	public int extend() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _extend(peerHandle);
		if ( result < KErrNone ) {
			throw new StoreException(result);
		}
		return result;
	}
	
	public int reclaim() throws StoreException {
		if ( peerHandle <= 0 ) {
			throw new StoreException("Store closed (not bound to a native object)");
		}
		int result = _reclaim(peerHandle);
		if ( result < KErrNone ) {
			throw new StoreException(result);
		}
		return result;
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

	public static String translateNativeError(int error) {
		return _translateNativeError(error);
	}
	
	public abstract byte[] getContent() throws StoreException ;
	public abstract void close();
	
	private native int _initNative();
	private native int _delete(int peerHandle, int streamId); 
	private native int _compact(int peerHandle); 
	private native int _extend(int peerHandle); 
	private native int _reclaim(int peerHandle); 
	private native int _commit(int peerHandle);
	private native int _revert(int peerHandle); 
	public static native String _translateNativeError(int error);
}
