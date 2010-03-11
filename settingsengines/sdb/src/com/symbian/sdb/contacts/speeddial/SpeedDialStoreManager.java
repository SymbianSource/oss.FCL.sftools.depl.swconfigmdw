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

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.speeddial.model.DatabaseSpeedDialData;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialEntry;
import com.symbian.store.DictionaryStore;
import com.symbian.store.StoreException;
import com.symbian.store.StoreInputStream;
import com.symbian.store.StoreOutputStream;

/**
 * @author krzysztofzielinski
 *
 */
public class SpeedDialStoreManager implements SpeedDialIniFileManager {

	private static final int STRING_MAX_LENGTH = 512;
	private static final int NULL_CONTACT_ID = -1;
	private static final int SPDTABLE_STREAM_UID = 0x10009EF7;
	private static final int CONTACTS_STORE_UID = 0x10009099;
	private static final int NUMBER_OF_SPD_TABLES = 1;
	private static final int SPEED_DIAL_PHONE_LENGTH = 64; // KSpeedDialPhoneLength

	public void createNewFile(SpeedDialDataRepository speedDialDataRepository, File iniFile) {
		DictionaryStore store = null;
		StoreOutputStream ostream = null;
		try {
			deleteFile(iniFile);
			store = new DictionaryStore(iniFile.getAbsolutePath(),CONTACTS_STORE_UID);
			
			//store speed dial information
			ostream = (StoreOutputStream) store.getOutputStream(SPDTABLE_STREAM_UID);
			
			ostream.writeInt32(speedDialDataRepository.getAllSpeedDialData().size());
			
			for (DatabaseSpeedDialData databaseSpeedDialData : speedDialDataRepository.getAllSpeedDialData()) {
				ostream.writeBuf16(databaseSpeedDialData.getDatabaseName());
				for (int i = 	1; i < databaseSpeedDialData.size() + 1; i++) {
					SpeedDialEntry speedDialEntry = databaseSpeedDialData.getSpeedDialEntry(i);
					writeEntry(ostream, speedDialEntry);					
				}
			}
			ostream.close();
			store.commit();
			store.close();
		} catch (StoreException e) {
			throw new SystemException("Error when writing speed dial ini file: " + iniFile);
		} catch (IOException e) {
			throw new SystemException("Error when writing speed dial ini file: " + iniFile);
		}
		finally	{
			if (null != store) 	{
				store.close();
			}
		}
		
	}

	private void deleteFile(File iniFile) {
		if (iniFile.exists())	{
			boolean deletionSuccessful = iniFile.delete();
			if (!deletionSuccessful)	{
				throw new SystemException("Failed to delete speed dial ini file");
			}
		}
	}

	private void writeEntry(StoreOutputStream out, SpeedDialEntry speedDialEntry) throws IOException {
		if (speedDialEntry.equals(SpeedDialEntry.getEmptyEntry()))	{
			out.writeInt32(NULL_CONTACT_ID);
			out.writeBuf16("");
		} else	{
			out.writeInt32((int)speedDialEntry.getContactId());
			out.writeBuf16(speedDialEntry.getPhoneNumber());
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
			throw new SystemException("Error when reading SpeedDial INI file (incorrect file format): " + iniFile);
		}
	}

	/**
	 * @param iniFile
	 * @return
	 * @throws FileNotFoundException
	 * @throws IOException
	 */
	private SpeedDialDataRepository tryToReadFile(File iniFile) throws FileNotFoundException, IOException {
		SpeedDialDataRepository speedDataRepository = null;

		DictionaryStore store = null;
		StoreInputStream istream = null;
		try	{
			store = new DictionaryStore(iniFile.getAbsolutePath(),CONTACTS_STORE_UID);
			istream = store.getInputStream(SPDTABLE_STREAM_UID);

			int dbCount = istream.readInt32();
			speedDataRepository = readRepository(istream, dbCount);

			if (null == speedDataRepository)	{
				throw new SystemException("Error when reading SpeedDial INI file - No data found");
			}
		} finally	{
			if (null != istream) istream.close();
			if (null != store) store.close();
		}

		return speedDataRepository;
	}

	private SpeedDialDataRepository readRepository(StoreInputStream istream, int dbCount) throws IOException {
		SpeedDialDataRepository speedDataRepository = new SpeedDialDataRepository();
		for (int i = 0; i < dbCount; i++) {
			String databaseName = istream.readBuf16(STRING_MAX_LENGTH);
			
			DatabaseSpeedDialData dbSpeedDialData = speedDataRepository.addNewDatabaseSpeedDialData(databaseName);
			
			readDatabaseSpeedDialData(istream, dbSpeedDialData);
		}
		return speedDataRepository;
	}

	private void readDatabaseSpeedDialData(StoreInputStream istream, DatabaseSpeedDialData dbSpeedDialData) throws IOException {
		for (int i = 1; i < dbSpeedDialData.size() + 1; i++) {
			SpeedDialEntry entry = readEntry(istream);
			dbSpeedDialData.setSpeedDialEntry(i, entry);
		}
	}

	private SpeedDialEntry readEntry(StoreInputStream istream) throws IOException {
		long contactId = istream.readInt32();
		
		if (contactId == NULL_CONTACT_ID)	{
			istream.readBuf16(SPEED_DIAL_PHONE_LENGTH);
			return SpeedDialEntry.getEmptyEntry();
		}
		else	{
			String phoneNumber = istream.readBuf16(SPEED_DIAL_PHONE_LENGTH);
			return new SpeedDialEntry(contactId, phoneNumber);
		}
	}
}
