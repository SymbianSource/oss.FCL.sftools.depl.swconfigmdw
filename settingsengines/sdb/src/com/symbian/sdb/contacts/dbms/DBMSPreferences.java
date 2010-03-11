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

package com.symbian.sdb.contacts.dbms;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import org.apache.log4j.Logger;

import com.symbian.sdb.configuration.Configuration;
import com.symbian.sdb.contacts.model.Preferences;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder.SortOrderEntry;
import com.symbian.sdb.contacts.model.common.PreferencesSortOrder.SortOrderType;
import com.symbian.sdb.contacts.sqlite.GenericUtils;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateMapper;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.util.LongArray;

//TODO Case for an abstract class? see sort order preferences.
public class DBMSPreferences implements Preferences {
	private static final Logger logger = Logger.getLogger(DBMSPreferences.class);
	public static final String DBMS_PREFERENCES_TEMPLATE_ID = "contacts.preferences.TemplateId";
	public static final String DBMS_PREFERENCES_OWN_CARD = "contacts.preferences.OwnCardId";
	public static final String DBMS_PREFERENCES_CARD_TEMPLATE_REF_ID = "contacts.preferences.CardTemplateRefId";
	public static final String DBMS_PREFERENCES_CARD_TEMPLATE_ID = "contacts.preferences.CardTemplateId";
	public static final String DBMS_PREFERENCES_GROUP_ID_LIST = "contacts.preferences.GroupIdList";
	public static final String DBMS_PREFERENCES_MACHINE_UID = "contacts.preferences.MachineUID";
	public static final String DBMS_PREFERENCES_SORT_ORDER = "contacts.preferences.SortOrder";
	
	
	int CM_PrefFileId;             // Always NULL - EDbColInt16
	int CM_PrefTemplateId = 0;         // EDbColInt32 CM_Id of System template 
	int CM_PrefOwnCardId = -1;          // EDbColInt32
	int CM_PrefCardTemplateRefId = -1; // EDbColInt32 CM_Id of User Added template
	//	byte[] CM_PrefCardTemplateId = null;     // EDbColLongBinary
	LongArray cardTemplateIdInts = new LongArray();
	//	byte[] CM_PrefGroupIdList;        // EDbColLongBinary
	LongArray groupIdListInts = new LongArray();
	int CM_PrefFileVer = 8;            // Allways 8 - EDbColInt32
	long CM_creationdate = System.currentTimeMillis();           // EDbColDateTime
	long CM_MachineUID = 6541731268600818345L;            // EDbColInt64

	// byte[] CM_PrefSortOrder;          // EDbColLongBinary
	List<SortOrderEntry> sortOrderEntries = new ArrayList<SortOrderEntry>();
	

	Configuration configuration;
	TemplateMapper mapper;
	
	
	public DBMSPreferences(Configuration configuration, TemplateMapper mapper) {	
		this.configuration = configuration;
		this.mapper = mapper;
	}
	
	public void persistToDb(DBManager manager) throws SDBExecutionException {
		byte [] sortOrderBytes = PreferencesSortOrder.createSortOrderBlob(sortOrderEntries);
        Connection connection = manager.getConnection();
        Statement stmt = null;
        PreparedStatement pstmt = null;
        
        byte[] generated_CM_PrefCardTemplateId = null;
        byte[] generated_CM_PrefGroupIdList = null;
        
		try {
			generated_CM_PrefCardTemplateId = LongArray.makeBlob(cardTemplateIdInts);
		} catch (IOException e) {
			throw new SDBExecutionException("Unable to generate CM_PrefCardTemplateId field.", e);
		}
       
		try {
			generated_CM_PrefGroupIdList = LongArray.makeBlob(groupIdListInts);
		} catch (IOException e) {
			throw new SDBExecutionException("Unable to generate CM_PrefGroupIdList field.", e);
		}
        
        try{
	        stmt = connection.createStatement();
	        stmt.executeUpdate("DELETE FROM preferences");
	        String sql = "INSERT INTO preferences VALUES(?,?,?,?,?,?,?,?,?,?)";
	        pstmt = connection.prepareStatement(sql);
	        pstmt.setNull(1, java.sql.Types.INTEGER);
	        pstmt.setInt(2, CM_PrefTemplateId);
	        pstmt.setInt(3, CM_PrefOwnCardId);
	        pstmt.setInt(4, CM_PrefCardTemplateRefId);
	        pstmt.setBytes(5, generated_CM_PrefCardTemplateId);
	        pstmt.setBytes(6, generated_CM_PrefGroupIdList);
	        pstmt.setInt(7, CM_PrefFileVer);
	        pstmt.setDate(8, new java.sql.Date(CM_creationdate));
	        pstmt.setLong(9, CM_MachineUID);
	        pstmt.setBytes(10, sortOrderBytes);
	        pstmt.execute();
        } catch (SQLException e) {
			throw new SDBExecutionException("Unable to write preferences to database.", e);
		} finally {
			GenericUtils.closeQuietly(stmt);
			GenericUtils.closeQuietly(pstmt);
        }
	}

	public void readFromConfig() throws SDBExecutionException {
		String CM_PrefTemplateIdString = configuration.getOption(DBMS_PREFERENCES_TEMPLATE_ID);
		if ( CM_PrefTemplateIdString != null ) {
			CM_PrefTemplateId = Integer.parseInt(CM_PrefTemplateIdString);
		}
		
		String CM_PrefOwnCardIdString = configuration.getOption(DBMS_PREFERENCES_OWN_CARD);
		if ( CM_PrefOwnCardIdString != null ) {
			CM_PrefOwnCardId = Integer.parseInt(CM_PrefOwnCardIdString);
		}
		
		String CM_PrefCardTemplateRefIdString = configuration.getOption(DBMS_PREFERENCES_CARD_TEMPLATE_REF_ID);
		if ( CM_PrefCardTemplateRefIdString != null ) {
			CM_PrefCardTemplateRefId = Integer.parseInt(CM_PrefCardTemplateRefIdString);
		}
		
		String CM_PrefCardTemplateIdString = configuration.getOption(DBMS_PREFERENCES_CARD_TEMPLATE_ID);
		if ( CM_PrefCardTemplateIdString != null ) {
			cardTemplateIdInts = parseIntList(CM_PrefCardTemplateIdString);
		}
		
		String CM_PrefGroupIdListString = configuration.getOption(DBMS_PREFERENCES_GROUP_ID_LIST);
		if ( CM_PrefGroupIdListString != null ) {
			groupIdListInts = parseIntList(CM_PrefGroupIdListString);
		}
		
		String CM_MachineUIDString = configuration.getOption(DBMS_PREFERENCES_MACHINE_UID);
		if ( CM_MachineUIDString != null ) {
			CM_MachineUID = Long.parseLong(CM_MachineUIDString);
		}
		
		String sortOrderEntriesString = configuration.getOption(DBMS_PREFERENCES_SORT_ORDER);
		if ( sortOrderEntriesString != null ) {
			String [] ents = sortOrderEntriesString.split(",");
			for (int i = 0; i < ents.length; i++) {
				String [] kv = ents[i].split(":");
				if ( kv.length != 2 ) {
					throw new SDBExecutionException("Bad configuration for " + DBMS_PREFERENCES_SORT_ORDER+". Entry "+ents+" is not a \"key:value\" pair.");
				}
				String pref = kv[0];
				String val = kv[1];
				if ( !pref.endsWith("Value")) {
					pref += "Value";
				}
				
				try {
					Integer fieldTypeValue = mapper.getFieldType(pref);

					SortOrderType type;
					try {
						type = SortOrderType.valueOf(val);
					} catch (IllegalArgumentException e) {
						// Default to descending
						type = SortOrderType.EDesc;
					}
					
					SortOrderEntry ent = new SortOrderEntry(fieldTypeValue, type);
					sortOrderEntries.add(ent);
				}
				 catch (MappingMissingException e) {
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
	            CM_PrefTemplateId = rs.getInt(2);
	            CM_PrefOwnCardId = rs.getInt(3);
	            CM_PrefCardTemplateRefId = rs.getInt(4);
	            byte [] CM_PrefCardTemplateId = rs.getBytes(5);
	            
	            try {
					cardTemplateIdInts = LongArray.parseBlob(CM_PrefCardTemplateId);
				} catch (IOException e) {
					throw new SDBExecutionException("Can not read template ID from CM_PrefCardTemplateId field.", e);
				}
	            
	            byte [] CM_PrefGroupIdList = rs.getBytes(6);
	            
	            try {
	            	groupIdListInts = LongArray.parseBlob(CM_PrefGroupIdList);
				} catch (IOException e) {
					throw new SDBExecutionException("Can not read group ID list from CM_PrefGroupIdList field.", e);
				}
	            
	            CM_PrefFileVer = rs.getInt(7);
	            java.sql.Date tmp = rs.getDate(8);
	            if ( tmp != null ) {
	            	CM_creationdate = tmp.getTime();
	            } else {
	            	CM_creationdate = System.currentTimeMillis();
	            }
	            CM_MachineUID = rs.getLong(9);
	            byte [] sortOrderBlob = rs.getBytes(10);
	            sortOrderEntries = PreferencesSortOrder.createSortOrderEntries(sortOrderBlob);
	        } else {
	        	throw new SDBExecutionException("Preferences table is empty");
	        }
        } catch (SQLException e) {
			throw new SDBExecutionException("Can not read preferences from database", e);
		} finally {
			GenericUtils.closeQuietly(rs);
			GenericUtils.closeQuietly(stmt);
        }
	}

	// conversion functions
	
	public LongArray parseIntList(String commaSeparatedInts) {
		String [] strs = commaSeparatedInts.split(",");
		LongArray array = new LongArray(strs.length);
		for (int i = 0; i < strs.length; i++) {
			array.add(Integer.parseInt(strs[i]));
		}
		return array;
	}


	// getters/setters
	
	public int getCM_PrefFileId() {
		return CM_PrefFileId;
	}

	public void setCM_PrefFileId(int prefFileId) {
		CM_PrefFileId = prefFileId;
	}

	public int getCM_PrefTemplateId() {
		return CM_PrefTemplateId;
	}

	public void setCM_PrefTemplateId(int prefTemplateId) {
		CM_PrefTemplateId = prefTemplateId;
	}

	public int getCM_PrefOwnCardId() {
		return CM_PrefOwnCardId;
	}

	public void setCM_PrefOwnCardId(int prefOwnCardId) {
		CM_PrefOwnCardId = prefOwnCardId;
	}

	public int getCM_PrefCardTemplatePrefId() {
		return CM_PrefCardTemplateRefId;
	}

	public void setCM_PrefCardTemplatePrefId(int prefCardTemplatePrefId) {
		CM_PrefCardTemplateRefId = prefCardTemplatePrefId;
	}

	public int getCM_PrefFileVer() {
		return CM_PrefFileVer;
	}

	public void setCM_PrefFileVer(int prefFileVer) {
		CM_PrefFileVer = prefFileVer;
	}

	public long getCM_creationdate() {
		return CM_creationdate;
	}

	public void setCM_creationdate(long cm_creationdate) {
		CM_creationdate = cm_creationdate;
	}

	public long getCM_MachineUID() {
		return CM_MachineUID;
	}

	public void setCM_MachineUID(long machineUID) {
		CM_MachineUID = machineUID;
	}

	public void addGroupId(int id){
		if ( groupIdListInts == null ) {
			groupIdListInts = new LongArray();
		}
		if ( !groupIdListInts.contains(id) ) {
			groupIdListInts.add(id);
		}
	}
	
	public void addCardTemplateId(int id){
		if ( cardTemplateIdInts == null ) {
			cardTemplateIdInts = new LongArray();
		}
		if ( !cardTemplateIdInts.contains(id) ) {
			cardTemplateIdInts.add(id);
		}		
	}

	public LongArray getCardTemplateIds() {
		return cardTemplateIdInts;
	}
	public LongArray getGroupIds() {
		return groupIdListInts;
	}
}
