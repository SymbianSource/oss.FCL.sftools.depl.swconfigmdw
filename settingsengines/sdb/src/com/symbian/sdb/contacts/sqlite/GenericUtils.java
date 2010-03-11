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



package com.symbian.sdb.contacts.sqlite;

import java.io.IOException;
import java.io.OutputStream;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import com.symbian.store.NativeByteArrayInputStream;
import com.symbian.store.NativeByteArrayOutputStream;

public class GenericUtils {

	/**
	 * @param stmt Statement to be closed ignoring exceptions
	 */
	public static void closeQuietly(Statement stmt) {
		if (stmt != null) {
			try {
				stmt.close();
			} catch (SQLException e) {
				// We don't care about this exception as it only happens when closing
			}
		}
	}

	/**
	 * @param rs ResultSet to be closed ignoring exceptions
	 */
	public static void closeQuietly(ResultSet rs) {
		if (rs != null) {
			try {
				rs.close();
			} catch (SQLException e) {
				// We don't care about this exception as it only happens when closing
			}
		}
	}
	
    /**
     * Unconditionally close an <code>NativeByteArrayOutputStream</code>.
     *
     * Any exceptions will be ignored.
     *
     * @param output  the NativeByteArrayOutputStream to close, may be null or already closed
     */
	//TODO: Change NativeByteArrayOutputStream to throw IOException
    public static void closeQuietly(NativeByteArrayOutputStream output) {
        try {
            if (output != null) {
                output.close();
            }
        } catch (Exception e) {
            // ignore
        }
    }
    
    /**
     * Unconditionally close an <code>NativeByteArrayInputStream</code>.
     * 
     * Any exceptions will be ignored.
     *
     * @param output  the NativeByteArrayInputStream to close, may be null or already closed
     */
	//TODO: Change NativeByteArrayInputStream to throw IOException
    public static void closeQuietly(NativeByteArrayInputStream in) {
        try {
            if (in != null) {
            	in.close();
            }
        } catch (Exception e) {
            // ignore
        }
    }
}
