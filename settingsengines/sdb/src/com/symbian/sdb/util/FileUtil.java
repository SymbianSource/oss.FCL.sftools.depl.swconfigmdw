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

package com.symbian.sdb.util;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.Reader;
import java.io.Writer;
import java.sql.Connection;

import com.symbian.sdb.settings.Settings;

public final class FileUtil {

	public static String LINE_SEPARATOR = System.getProperty("line.separator");

	/**
	 * Private Constructor
	 *
	 */
	private FileUtil(){
		
	}
	
	/**
	 * Takes a filename and appends the string, before the file 
	 * extension, if there is one
	 * @param aFilename
	 * @param aString
	 */
	public static final String appendToFilename(String aFilename, String aString){	
		
		if(aFilename == null)
			return null;
		
		StringBuilder lStrBuff = new StringBuilder();		
		int lPos = aFilename.lastIndexOf(".");
		
		if(lPos > 0 ){			
			return lStrBuff.append(aFilename.substring(0, lPos)).append(aString).append(".").append(aFilename.subSequence(lPos+1, aFilename.length())).toString();
		} else{
			return lStrBuff.append(aFilename).append(aString).toString(); 
		}
	}
	
	/**
	 * Takes a part of a path and appends to it 
	 * @param initial path
	 * @param appended path segment
	 */
	public static final String concatFilePath(String path, String appendPath){	
		if(path == null){
			path = "";
		}
		if(appendPath == null){
			appendPath = "";
		}
		if(!path.endsWith("/")||!path.endsWith("\\")){
			path+=File.separator;
		}
		return path+appendPath;
	}
	
	/**
	 * Copies src file to dst file.
	 * If the dst file does not exist, it is created
	 */
    public static void copy(File source, File destination)	throws IOException{
    	copy(source.getAbsolutePath(), destination.getAbsolutePath());
    }
	
	/**
	 * Copies src file to dst file.
	 * If the dst file does not exist, it is created
	 */

    public static void copy(String aSrc, String aDst)	throws IOException
    {	    	
    	BufferedInputStream lIn = new BufferedInputStream( new FileInputStream(new File(aSrc)) );
    	BufferedOutputStream lOut = new BufferedOutputStream( new FileOutputStream(new File(aDst)) );
    	
    	
    	byte buffer[] = new byte[1024];
    	int read = -1;
    	
    	while ((read = lIn.read(buffer, 0, 1024)) != -1){
    		lOut.write(buffer, 0, read);
    	}
    	
		lOut.flush();
		lOut.close();		
		lIn.close();
    }	
    
    /**
     * Determines the name of the output Db file
     * @param requestedFile The requested file. If not null this is the supplied output file.
     * @return the file name which is either the requested file or the default db name (with an optional appended number to ensure uniqueness) 
     */
	public static File determineOutputFile(File requestedFile){
		File dbFile = requestedFile;
		if(dbFile == null) {
			dbFile = new File(System.getProperty(Settings.SDBPROPS.dbname.toString()));
			File newDbFile = dbFile;
			int x =0;
			while(newDbFile.exists()){
			    newDbFile = new File(FileUtil.appendToFilename(dbFile.getPath(), "_" + x));
			    x++;
			}	
			dbFile = newDbFile;
		}
		return dbFile;
	}
	
	public static void closeSilently(InputStream in){
		try {
			if(in!=null){
				in.close();
			}
		} catch (IOException e) {
		}
	}
	
	public static void closeSilently(OutputStream out){
		try {
			if(out!=null){
				out.close();
			}
		} catch (IOException e) {
		}
	}

	public static void closeSilently(Reader out) {
		try {
			if(out!=null){
				out.close();
			}
		} catch (IOException e) {
		}
	}
	
	public static void closeSilently(Writer out) {
		try {
			if(out!=null){
				out.flush();
				out.close();
			}
		} catch (IOException e) {
		}
	}
	
	public static void closeSilently(Connection out) {
		try {
			if(out!=null){
				out.close();
			}
		} catch (java.sql.SQLException e) {
		}
	}
	
	public static String readFile(File file)	{
		StringBuilder fileContentBuilder = new StringBuilder();

		FileInputStream fis = null;
		BufferedInputStream bis = null;
		DataInputStream dis = null;

		try {
			fis = new FileInputStream(file);

			bis = new BufferedInputStream(fis);
			dis = new DataInputStream(bis);

			while (dis.available() != 0) {

				fileContentBuilder.append(dis.readLine());
			}

			fis.close();
			bis.close();
			dis.close();

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return fileContentBuilder.toString();
	}

	/**
	 * @param iniFilePath
	 * @throws IOException 
	 */
	public static void deleteIfExists(String iniFilePath) throws IOException {
		File file = new File(iniFilePath);
		if (file.exists())	{
			boolean successful = file.delete();
			if (!successful)	{
				throw new IOException("Couldn't delete file: " + iniFilePath);
			}
		}
	}
}
