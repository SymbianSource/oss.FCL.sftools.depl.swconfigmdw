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


import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import org.apache.log4j.Logger;

import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.contacts.model.Preferences;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder.SortOrderEntry;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder.SortOrderType;
import com.symbian.sdb.contacts.template.ContactMapTypes;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBRuntimeException;
import com.symbian.sdb.util.LongArray;
import com.symbian.sdb.util.SymbianSpecificUtils;


/**
 * Manages Preferences table creation and reading for SQLite.
 * <p>
 */
//TODO Case for an abstract class? see sort order preferences.
public class SQLitePreferences implements Preferences {
	private static final Logger logger = Logger.getLogger(SQLitePreferences.class);
	public static final String SQLITE_PREFERENCES_DATA_SCHEMA_VERSION = "contacts.preferences.dataSchemaVersion";
	public static final String SQLITE_PREFERENCES_PREFERRED_CARD_TEMPLATE_ID = "contacts.preferences.preferredCardTemplateId";
	public static final String SQLITE_PREFERENCES_MACHINE_ID = "contacts.preferences.machineId";
	public static final String SQLITE_PREFERENCES_SORT_ORDER = "contacts.preferences.sortOrder";
	
	int preferenceId = 1;
	int dataSchemaVersion = 1;
	int preferredCardTemplateId = -1;
	long machineId = 0L;
	long creationDate = SymbianSpecificUtils.convertToSymbianTimestamp(System.currentTimeMillis());
	List<SortOrderEntry> sortOrderEntries = new ArrayList<SortOrderEntry>();
	
	Configuration configuration;
	TemplateMapper mapper;
	public SQLitePreferences(Configuration configuration, TemplateMapper mapper) {	
		this.configuration = configuration;
		this.mapper = mapper;
	}
	
	public void persistToDb(DBManager manager) throws SDBExecutionException {
		byte [] sortOrderBytes = PreferencesSortOrder.createSortOrderBlob(sortOrderEntries);
        Connection connection = manager.getConnection();
        Statement stmt = null;
        PreparedStatement stmt2 = null;
        try{
	        stmt = connection.createStatement();
	        stmt.executeUpdate("DELETE FROM preferences");
	        String sql = "INSERT INTO preferences VALUES(?,?,?,?,?,?)";
	        stmt2 = connection.prepareStatement(sql);
	        stmt2.setInt(1, preferenceId);
	        stmt2.setInt(2, dataSchemaVersion);
	        stmt2.setInt(3, preferredCardTemplateId);
	        stmt2.setLong(4, machineId);
	        stmt2.setLong(5, creationDate);
	        stmt2.setBytes(6, sortOrderBytes);
	        stmt2.execute();
        } catch (SQLException e) {
			throw new SDBExecutionException("Unable to write preferences to database.", e);
		} finally {
        	GenericUtils.closeQuietly(stmt);
        	GenericUtils.closeQuietly(stmt2);
        }
	}

	public void readFromConfig() throws SDBExecutionException {
		String dataSchemaVersionString = configuration.getOption(SQLITE_PREFERENCES_DATA_SCHEMA_VERSION);
		if ( dataSchemaVersionString != null ) {
			dataSchemaVersion = Integer.parseInt(dataSchemaVersionString);
		}
		String preferredCardTemplateIdString = configuration.getOption(SQLITE_PREFERENCES_PREFERRED_CARD_TEMPLATE_ID);
		if ( preferredCardTemplateIdString != null ) {
			preferredCardTemplateId = Integer.parseInt(preferredCardTemplateIdString);
		}
		String machineIdString = configuration.getOption(SQLITE_PREFERENCES_MACHINE_ID);
		if ( machineIdString != null ) {
			machineId = Integer.parseInt(machineIdString);
		}
		String sortOrderEntriesString = configuration.getOption(SQLITE_PREFERENCES_SORT_ORDER);
		if ( sortOrderEntriesString != null ) {
			String [] sortOrderStrings = sortOrderEntriesString.split(",");
			try {
				HashMap<String, String> map1 = mapper.getMapping(ContactMapTypes.field_type_mapping);
			} catch (MappingMissingException e) {
				throw new SDBRuntimeException("Unable to obtain lookups for "+ContactMapTypes.field_type_mapping, e);
			}

			for (String sortOrderEntry : sortOrderStrings) {
				String [] entry = sortOrderEntry.split(":");
				if ( entry.length != 2 ) {
					throw new SDBExecutionException("Bad configuration for " + SQLITE_PREFERENCES_SORT_ORDER+". Entry "+sortOrderEntry+" is not a \"key:value\" pair.");
				}
				String pref = entry[0];
				String val = entry[1];
				if ( !pref.endsWith("Value")) {
					pref += "Value";
				}
				Integer value = null;
				try {
					value = mapper.getFieldType(pref);
					
					SortOrderType type;
					try {
						type = SortOrderType.valueOf(val);
					} catch (IllegalArgumentException e) {
						// Default to descending
						type = SortOrderType.EDesc;
					}

					SortOrderEntry ent = new SortOrderEntry(value, type);
					sortOrderEntries.add(ent);
				} catch (MappingMissingException e) {
					logger.warn("Could not find field type for " + pref + ". Ignoring sort order preference.");
					logger.debug("Stack Trace: ",e);
				}
			}
		}
	}

	public void readFromDb(DBManager manager) throws SDBExecutionException {
        Connection connection = manager.getConnection();

        Statement stmt = null;
        ResultSet rs = null;
        
        try{
	        stmt = connection.createStatement();
	        rs = stmt.executeQuery("SELECT * FROM preferences");
	        if( rs.first() ) {
	        	preferenceId = rs.getInt(1);
	        	dataSchemaVersion = rs.getInt(2);
	        	preferredCardTemplateId = rs.getInt(3);
	        	machineId = rs.getLong(4);
	        	creationDate = rs.getLong(5);
	            byte [] sortOrderBlob = rs.getBytes(6);
	            sortOrderEntries = PreferencesSortOrder.createSortOrderEntries(sortOrderBlob);
	        } else {
	        	throw new SDBExecutionException("Preferences table is empty");
	        }
        } catch (SQLException e) {
			throw new SDBExecutionException("Can not read preferences from database", e);
		} finally {
        	GenericUtils.closeQuietly(stmt);
        	
        	GenericUtils.closeQuietly(rs);
        }
	}

	public int getPreference_id() {
		return preferenceId;
	}

	public void setPreference_id(int preference_id) {
		this.preferenceId = preference_id;
	}

	public int getDataSchemaVersion() {
		return dataSchemaVersion;
	}

	public void setDataSchemaVersion(int dataSchemaVersion) {
		this.dataSchemaVersion = dataSchemaVersion;
	}

	public int getPreferredCardTemplateId() {
		return preferredCardTemplateId;
	}

	public void setPreferredCardTemplateId(int preferredCardTemplateId) {
		this.preferredCardTemplateId = preferredCardTemplateId;
	}

	public long getMachineId() {
		return machineId;
	}

	public void setMachineId(long machineId) {
		this.machineId = machineId;
	}

	public long getCreationDate() {
		return creationDate;
	}

	public void setCreationDate(long creationDate) {
		this.creationDate = creationDate;
	}
	
	public void addSortOrderEntry(SortOrderEntry entry) {
		sortOrderEntries.add(entry);
	}

	public void addSortOrderEntry(int uid, SortOrderType type) {
		sortOrderEntries.add(new SortOrderEntry(uid, type));
	}
	
	public List sortOrderEntries(){
		return Collections.unmodifiableList(sortOrderEntries);
	}
	
	// not used for SQLite
	public void addGroupId(int id){
		throw new UnsupportedOperationException("SQLite database does not keep group ids in preferences table.");
	}
	public void addCardTemplateId(int id){
		throw new UnsupportedOperationException("SQLite database does not keep template ids in preferences table.");
	}

	public LongArray getCardTemplateIds() {
		throw new UnsupportedOperationException("SQLite database does not keep template ids in preferences table.");
	}

	public LongArray getGroupIds() {
		throw new UnsupportedOperationException("SQLite database does not keep group ids in preferences table.");
	}


}
