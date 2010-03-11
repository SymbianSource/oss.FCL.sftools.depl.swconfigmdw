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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.speeddial.model.DatabaseSpeedDialData;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialEntry;

/**
 * @author krzysztofZielinski
 *
 */
public class SpeedDialIniFileManagerImpl implements SpeedDialIniFileManager	{

	private static final String NEW_LINE = "\r\n";
	private static final String NULL_SPEED_DIAL_ENTRY_STRING = "NULL SpeedDial Entry";

	public void createNewFile(SpeedDialDataRepository speedDialDataRepository, File iniFile) {
		try {
			FileWriter fstream = new FileWriter(iniFile);
			BufferedWriter out = new BufferedWriter(fstream);

			out.write(String.valueOf(speedDialDataRepository.getCount()));
			out.write(NEW_LINE);
			
			for (DatabaseSpeedDialData databaseSpeedDialData : speedDialDataRepository.getAllSpeedDialData()) {
				out.write(databaseSpeedDialData.getDatabaseName());
				out.write(NEW_LINE);
				
				for (int i = 1; i < databaseSpeedDialData.size() + 1; i++) {
					SpeedDialEntry speedDialEntry = databaseSpeedDialData.getSpeedDialEntry(i);
					writeEntry(out, speedDialEntry);
					out.write(NEW_LINE);					
				}
			}
			out.close();
		} catch (IOException e) {
			throw new SystemException("Error when writing speed dial ini file: " + iniFile);
		}
	}

	private void writeEntry(BufferedWriter out, SpeedDialEntry speedDialEntry) throws IOException {
		if (speedDialEntry.equals(SpeedDialEntry.getEmptyEntry()))	{
			// print NULL entry
			out.write(NULL_SPEED_DIAL_ENTRY_STRING);
		}
		else	{
			out.write(speedDialEntry.getContactId() + ","  + speedDialEntry.getPhoneNumber());
		}
	}

	public SpeedDialDataRepository readFile(File iniFile)	{
		try {
			return tryToReadFile(iniFile);
		} catch (FileNotFoundException e) {
			throw new SystemException("SpeedDial INI doesn't exists: " + iniFile);
		} catch (IOException e) {
			throw new SystemException("Error when reading SpeedDial INI file: " + iniFile);
		} catch (ArithmeticException e) {
			throw new SystemException("Erro when reading SpeedDial INI file (incorrect file format): " + iniFile);
		}
	}

	/**
	 * @param iniFile
	 * @return
	 * @throws FileNotFoundException
	 * @throws IOException
	 */
	SpeedDialDataRepository tryToReadFile(File iniFile) throws FileNotFoundException, IOException {
		SpeedDialDataRepository speedDataRepository = null;
		
		FileReader fstream = new FileReader(iniFile);
		BufferedReader in = new BufferedReader(fstream);
		
		int dbCount = readCount(in);
		speedDataRepository = readRepository(in, dbCount);
		
		if (null == speedDataRepository)	{
			throw new SystemException("Error when reading SpeedDial INI file - No data found");
		}
		
		return speedDataRepository;
	}

	private SpeedDialDataRepository readRepository(BufferedReader in, int dbCount) throws IOException {
		SpeedDialDataRepository speedDataRepository = new SpeedDialDataRepository();
		for (int i = 0; i < dbCount; i++) {
			String databaseName = in.readLine();
			DatabaseSpeedDialData dbSpeedDialData = speedDataRepository.addNewDatabaseSpeedDialData(databaseName);
			
			readDatabaseSpeedDialData(in, dbSpeedDialData);
		}
		return speedDataRepository;
	}

	private void readDatabaseSpeedDialData(BufferedReader in, DatabaseSpeedDialData dbSpeedDialData) throws IOException {
		for (int i = 1; i < dbSpeedDialData.size() + 1; i++) {
			SpeedDialEntry entry = readEntry(in);
			dbSpeedDialData.setSpeedDialEntry(i, entry);
		}
	}

	private SpeedDialEntry readEntry(BufferedReader in) throws IOException {
		String entryLine = in.readLine();
		
		if (entryLine.equals(NULL_SPEED_DIAL_ENTRY_STRING))	{
			return SpeedDialEntry.getEmptyEntry();
		}
		else	{
			String[] entryParts = entryLine.split(",");
			
			long contactId = Long.parseLong(entryParts[0]);
			String phoneNumber = entryParts[1];
			return new SpeedDialEntry(contactId, phoneNumber);
		}
	}

	private int readCount(BufferedReader in) throws IOException {
		String countLine = in.readLine();
		return Integer.parseInt(countLine);
	}
	
}
