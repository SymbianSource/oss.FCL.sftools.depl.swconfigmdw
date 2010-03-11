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
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashSet;

import org.apache.log4j.Logger;

import com.symbian.dbms.jdbc.DbmsDriver;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.dbms.model.AbstractDBMSContact;
import com.symbian.sdb.contacts.dbms.model.DBMSContactCard;
import com.symbian.sdb.contacts.dbms.model.DBMSContactGroup;
import com.symbian.sdb.contacts.dbms.model.DBMSEmailAddress;
import com.symbian.sdb.contacts.dbms.model.DBMSPhoneNumber;
import com.symbian.sdb.contacts.dbms.model.DBMSTemplate;
import com.symbian.sdb.contacts.dbms.model.IdentityTable;
import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;
import com.symbian.sdb.contacts.model.Preferences;
import com.symbian.sdb.contacts.model.PreferencesManager;
import com.symbian.sdb.contacts.speeddial.SpeedDialAssignmentEntry;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.database.IConnectionProvider;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.ContactsFlow;
import com.symbian.sdb.mode.flow.SpeedDialModeType;
import com.symbian.sdb.util.LongArray;

/**
 * Contact persistence interface for DBMS.
 * 
 * @author krzysztofZielinski
 * 
 */
public class ContactDaoDBMS implements ContactsDbValidator {

	private static final Logger logger = Logger.getLogger(ContactsFlow.class);
	
	// ~ Injected Fields =======================================================
    private IConnectionProvider connectionProvider;
    private PreferencesManager preferencesManager;
    private SpeedDialManager speedDialManager;
    
    // ~ Business Methods ======================================================

    /**
     * Save given contact in DBMS database
     * 
     * @param contact
     * @return
     */
    public DBMSContactCard save(DBMSContactCard contact) {

        // persist groups
        for (DBMSContactGroup contactGroup : contact.getGroups()) {
            contactGroup = ensureGroup(contactGroup);
        }

        saveContact(contact);

        // assign contacts to groups
        for (DBMSContactGroup contactGroup : contact.getGroups()) {
            contactGroup = ensureGroup(contactGroup);
            assignContactToGroup(contact, contactGroup);
        }

        // persists associated emails
        for (DBMSEmailAddress emailAddress : contact.getEmailAddresses()) {
            createEmailAddress(contact.getId(), emailAddress);
        }

        HashSet<Integer> addedNumbers = new HashSet<Integer>();

        // persists associated phone numbers
        for (DBMSPhoneNumber phoneNumber : contact.getPhoneNumbers()) {
			// Only add phone numbers which have not already been added (Only the 7 digit CM_PhoneMatching is checked)  
        	// See RPplPhoneTable::CreateInDbL in rpplphonetable.cpp
        	if (!addedNumbers.contains(phoneNumber.getPhoneMatching())) {
        		addedNumbers.add(phoneNumber.getPhoneMatching());
                createPhoneNumber(contact.getId(), phoneNumber);   
        	}

            createSpeedDialEntryForContact(contact);
        }
        
        return contact;
    }

	/**
	 * @param contact
	 */
	private void createSpeedDialEntryForContact(DBMSContactCard contact) {
		if (speedDialManager.getMode().equals(SpeedDialModeType.CREATE) ||
				speedDialManager.getMode().equals(SpeedDialModeType.UPDATE))	{

			for (SpeedDialData speedDialData : contact.getSpeedDialData()) {
				SpeedDialAssignmentEntry speedDialAssignmentEntry = new SpeedDialAssignmentEntry(speedDialData.getSpeedDialValue(), speedDialData.getSpeedDialIndex(), contact.getId());
				speedDialManager.addSpeeDialEntry(speedDialAssignmentEntry);
			}
		}
	}

    /**
     * Save template.
     * 
     * @param template
     */
    public void saveTemplate(DBMSTemplate template) {
        saveContact(template);
    }

    /**
     * Persists phone number for given contactId
     * 
     * @param contactId
     *            parent contact's id
     * @param phoneNumber
     */
    public void createPhoneNumber(Long contactId, DBMSPhoneNumber phoneNumber) {
        Connection connection = getConnection();
        phoneNumber.setId(contactId);
        String sql = "INSERT INTO phone VALUES(?,?,?);";
        PreparedStatement preparedStatement = null;
        try {
            preparedStatement = connection.prepareStatement(sql);   
            preparedStatement.setLong(1, phoneNumber.getId());
            preparedStatement.setInt(2, phoneNumber.getPhoneMatching());
            preparedStatement.setInt(3, phoneNumber.getExtendedPhoneMatching());

            preparedStatement.execute();
        } catch (SQLException e) {
            throw new SystemException(e);
        }
        finally {
            closePreparedStatement(preparedStatement);
        }

    }

    /**
     * Persists email address for given contactId
     * 
     * @param contactId
     *            parent cotnact's id
     * @param emailAddress
     */
    public void createEmailAddress(Long contactId, DBMSEmailAddress emailAddress) {
        Connection connection = getConnection();
        String sql = "INSERT INTO emailTable VALUES(?,?,?);";
        PreparedStatement preparedStatement = null;
        try {
            emailAddress.setFiledId(getLastInsertedEmailId() + 1);
            emailAddress.setParentCMID(contactId);

            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setLong(1, emailAddress.getFiledId());
            preparedStatement.setLong(2, emailAddress.getParentCMID());
            preparedStatement.setString(3, emailAddress.getValue());

            preparedStatement.execute();
        } catch (SQLException e) {
            throw new SystemException(e);
        }
        finally {
            closePreparedStatement(preparedStatement);
        }
    }

    /**
     * Create group (and all associated groups) in a database if
     * necessary
     * 
     * @param contactGroup
     * @param groupLevel
     * @return
     */
    public DBMSContactGroup ensureGroup(DBMSContactGroup contactGroup) {
        long id = getGroupId(contactGroup.getSearchableText());
        // check if group already exists
        if (id == -1) {
            // if group dosn't exists save it
            saveContact(contactGroup);
            PreparedStatement preparedStatement = null;
            try {
                String sql = "INSERT INTO groups2 VALUES(?,?)";
                preparedStatement = getConnection().prepareStatement(sql);
                preparedStatement.setLong(1, contactGroup.getId());
                LongArray members = contactGroup.getMembers();
                byte[] blob = null;
                if ( members.size() != 0 ) { 
                    blob = LongArray.makeBlob(members);
                }
                preparedStatement.setBytes(2, blob);
                
                preparedStatement.execute();
                id = DbmsDriver.getMax(getConnection(), "groups2", "CM_Id");
                
                Preferences preferences = preferencesManager.getPreferences();
                preferences.addGroupId((int)id);
            } catch (SDBExecutionException e) {
                throw new SystemException(e);
            } catch (SQLException e) {
                throw new SystemException(e);
            } catch (IOException e) {
                throw new SystemException(e);
            } finally {
                closePreparedStatement(preparedStatement);
            }
        } else {
            // read the group members from db
            Statement statement = null;
            ResultSet rs = null;
	        try {
	            String sql = "SELECT CM_GroupMembers FROM groups2 WHERE CM_ID="+id;
	            statement = getConnection().createStatement();
	            rs = statement.executeQuery(sql); 
	            if ( rs.first() ) {
	            	byte [] blob = rs.getBytes(1);
	            	if ( blob != null ) {
	            		LongArray members = LongArray.parseBlob(blob);
	            		contactGroup.setMembers(members);
	            	}
	            } else {
	            	// hmmm, no entry in the groups table?
		            throw new SystemException("Inter-table dependency broken in Groups", null);
	            }
	        } catch (SQLException e) {
	            throw new SystemException(e);
	        } catch (IOException e) {
	            throw new SystemException(e);
	        } finally {
	        	if ( rs!=null) {
	        		try{rs.close();rs = null;} catch (Exception e) {}
	        	}
	        	if ( statement!=null) {
	        		try{statement.close();statement = null;} catch (Exception e) {}
	        	}
	        }
        }
        
        contactGroup.setId(new Long(id));
        return contactGroup;
    }

    /**
     * Query databaser to check if given contact group exists in a
     * database. In the case of successful lookup contact id is to be
     * assigned to the group
     * 
     * @param contactGroup
     * @return
     */
    private int getGroupId(String groupName) {

        Connection connection = getConnection();
        String sql = "SELECT CM_Id FROM CONTACTS WHERE CM_SearchableText=?";
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;
        int id = -1;
        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setString(1, groupName);
            
            preparedStatement.execute();
            resultSet = preparedStatement.getResultSet();
            boolean hasSomeResults = resultSet.first();
            if ( hasSomeResults ) {
                id = resultSet.getInt(1);
            }
        } catch(Exception e) {
            throw new SystemException("Exception occured while looking for a pre-existing group", e);
        } finally {
            if ( resultSet != null ) { 
            	try{resultSet.close();}catch(Exception e){}; 
            }
            if ( preparedStatement != null ) { 
                try{preparedStatement.close();}catch(Exception e){}; 
            }
        }
        return id;
    }

    /**
     * Create association between group and contact (groups and groups2 tables). 
     * Contact can be a contact 2nd level group card or a group (only 2 levels of groups are supported by Symbian contacts model)
     * 
     * @param savedContact already saved contact (id must be already assigned) 
     * @param savedContactGroup already saved contactGroup (id must be already assigned)
     */
    private void assignContactToGroup(AbstractDBMSContact savedContact, DBMSContactGroup savedContactGroup) {

        // check if association already exists
        boolean alreadyMember = false;
        LongArray members = savedContactGroup.getMembers();
        for( int i = 0 ; i < members.size(); i++ ) {
            if ( savedContact.getId() ==  members.get(i) ) {
                // association already exists
                alreadyMember = true;
                break;
            }
        }
        if ( !alreadyMember ) {
            // add the member to the group
            savedContactGroup.addMember(savedContact);
        
            Connection connection = getConnection();
            PreparedStatement preparedStatement = null;
            try {
                String sql = "INSERT INTO groups VALUES(?,?)";
                preparedStatement = connection.prepareStatement(sql);
                preparedStatement.setLong(1, savedContactGroup.getId());
                preparedStatement.setLong(2, savedContact.getId());
                
                preparedStatement.execute();
            } catch (SQLException e) {
                throw new SystemException(e);
            } finally {
                if ( preparedStatement!=null) {
                    try{
                        preparedStatement.close();
                        preparedStatement = null;
                    } catch (Exception e) {}
                }
            }
            // update
            try {
                String sql = "UPDATE groups2 SET CM_GroupMembers=? WHERE CM_ID=" 
                                + savedContactGroup.getId();
                preparedStatement = connection.prepareStatement(sql);
                byte[] blob = LongArray.makeBlob(savedContactGroup.getMembers());
                preparedStatement.setBytes(1, blob);
                
                preparedStatement.execute();
            } catch (SQLException e) {
                throw new SystemException(e);
            } catch (IOException e) {
                throw new SystemException(e);
            } finally {
                closePreparedStatement(preparedStatement);
            }
        }
    }

    /**
     * Persists contact in a database - used for persisting contact cards
     * and groups
     * 
     * @param contact
     */
    private void saveContact(AbstractDBMSContact contact) {

        Long contactId = saveContactInContactTable(contact);
        IdentityTable identityTable = contact.getIdentityTable();
        saveContactInIdentityTable(contactId, identityTable);
    }

    /**
     * Saves contact data stored in 'identityTable' table
     * 
     * @param contactId
     * @param identityTable
     */
    private void saveContactInIdentityTable(Long contactId, IdentityTable identityTable) {
        Connection connection = getConnection();
        PreparedStatement preparedStatement = null;
        try {
            String sql = "INSERT INTO identityTable VALUES (?,?,?,?,?,?,?,?,?,?,?)";

            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setLong(1, contactId);
            preparedStatement.setString(2, identityTable.getFirstName());
            preparedStatement.setString(3, identityTable.getLastName());
            preparedStatement.setString(4, identityTable.getCompanyName());
            preparedStatement.setInt(5, identityTable.getType().getValue());
            preparedStatement
                    .setInt(6, identityTable.getAttribute().getValue());
            preparedStatement.setInt(7, identityTable.getContactHintField()
                    .getValue());
            preparedStatement.setInt(8, identityTable.getContactExtHintField()
                    .getValue());
            preparedStatement.setString(9, identityTable.getFirstNamePrn());
            preparedStatement.setString(10, identityTable.getLastNamePrn());
            preparedStatement.setString(11, identityTable.getCompanyNamePrn());

            preparedStatement.execute();

        } catch (SQLException e) {
            throw new SystemException(e);
        } finally {
            if (preparedStatement != null) {
                try {
                    preparedStatement.close();
                } catch (SQLException e) {
                    throw new SystemException(e);
                }
            }
        }
    }

    /**
     * Saves contact data stored in 'Contacts' table
     * 
     * @param contact
     * @return
     */
    private Long saveContactInContactTable(AbstractDBMSContact contact) {
        Connection connection = getConnection();
        PreparedStatement preparedStatement = null;
        try {
            String sql = "INSERT INTO contacts (CM_Type, CM_PrefTemplateRefId, CM_UIDString, CM_Last_modified, CM_ContactCreationDate, " +
                    "CM_Attributes, CM_ReplicationCount, CM_Header, CM_TextBlob, CM_SearchableText) VALUES (?,?,?,?,?,?,?,?,?,?)";

            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setInt(1, contact.getType().getValue());
            preparedStatement.setInt(2, contact.getPrefTemplateRefId());
            preparedStatement.setString(3, contact.getUIDString());
            preparedStatement.setDate(4, new Date(contact.getLastModified()
                    .getTime()));
            preparedStatement.setDate(5, new Date(contact
                    .getContactCreationDate().getTime()));
            preparedStatement.setInt(6, contact.getAttributes().getValue());
            preparedStatement.setInt(7, contact.getReplicationCount());
            preparedStatement.setBytes(8, contact.getHeader().getBlob());
            preparedStatement.setBytes(9, contact.getTextBlob().getBlob());
            preparedStatement.setString(10, contact.getSearchableText());

            preparedStatement.execute();
        } catch (SQLException e) {
            throw new SystemException(e);
        } finally {
            closePreparedStatement(preparedStatement);
        }

        Long contactId = -1L;
        try {
            contactId = getLastInsertedContactId();
            contact.setId(contactId);
        } catch (SQLException e) {
            throw new SystemException(e);
        }

        return contactId;
    }

    private void closePreparedStatement(PreparedStatement preparedStatement) {
        if (preparedStatement != null) {
            try {
                preparedStatement.close();
            } catch (SQLException e) {
                throw new SystemException(e);
            }
        }
    }
    
    /**
     * Utility method to get connection to database
     * 
     * @return
     */
    private Connection getConnection() {
        return connectionProvider.getConnection();
    }

    /**
     * Returns id for contacts table.
     * 
     * @param contact
     * @return
     */
    private long getLastInsertedContactId() throws SQLException {
        return getLastInsertedValueIntoTable("CONTACTS", "CM_Id");
    }

    private long getLastInsertedEmailId() throws SQLException {
        return getLastInsertedValueIntoTable("EMAILTABLE", "EMail_FieldID");
    }
    
    private long getLastInsertedValueIntoTable(String tableName, String columnName) throws SQLException {
        Connection connection = getConnection();
        long lastId = DbmsDriver.getMax(connection, tableName, columnName);
         
        return lastId;
    }

    //TODO not used
    private void closeResultSet(ResultSet resultSet) {
        if (null != resultSet) {
            try {
                resultSet.close();
            } catch (SQLException e) {
                throw new SystemException(e);
            }    
        }
    }
    
    public byte[] readContactHeader(long contactId) {
        byte[] result = null;
        String sql = "select CM_Header from contacts where cm_id=" + contactId;
        Connection connection = getConnection();
        try {
            Statement stm = connection.createStatement();
            ResultSet set = stm.executeQuery(sql);
            if (set.next()) {
                // preparedStatement.setBytes(8,
                // contact.getHeader().getValue());
                result = set.getBytes(1);
            }
            set.close();
            stm.close();
        } catch (SQLException e) {
            throw new SystemException(e);
        }
        return result;
    }

    public boolean templateExistsInDB(long templateId) {
        byte[] header = readContactHeader(templateId);
        return (null != header);
    }

    public void validateContactsDbSchema() throws SDBValidationException	{
        try	{
        	logger.debug("Validating Contacts schema in existing database");
        	queryExecutesSuccessfuly("SELECT parent_cmid FROM IdentityTable WHERE parent_cmid < 1");	
        	queryExecutesSuccessfuly("SELECT cm_id FROM Contacts WHERE cm_id < 1");
        	queryExecutesSuccessfuly("SELECT cm_id FROM Phone WHERE cm_id < 1");
        	queryExecutesSuccessfuly("SELECT email_fieldId FROM EmailTable WHERE email_fieldId < 1");
        	queryExecutesSuccessfuly("SELECT cm_id FROM Groups WHERE cm_id < 1");
        	queryExecutesSuccessfuly("SELECT cm_id FROM Groups2 WHERE cm_id < 1");
        	queryExecutesSuccessfuly("SELECT cm_prefFileId FROM Preferences WHERE cm_prefFileId < 1");
        	queryExecutesSuccessfuly("SELECT cm_id FROM Sync WHERE cm_id < 1");
        }
    	catch (Exception e) {
			throw new SDBValidationException("Database (contacts db schema) is invalid", e);
		}
    }

	void queryExecutesSuccessfuly(String sql) {
        Connection connection = getConnection();
        try {
            Statement stm = connection.createStatement();
            stm.executeQuery(sql);
            stm.close();
        } catch (SQLException e) {
        	logger.debug("Contacts DB schema validation failed for query: " + sql, e);
        	throw new SystemException(e);
        }
	}
    
    
    // ~ Getters/Setters =======================================================

    public void setConnectionProvider(IConnectionProvider connectionProvider) {
        this.connectionProvider = connectionProvider;
    }

    public void setPreferencesManager(PreferencesManager preferencesManager) {
        this.preferencesManager = preferencesManager;
    }

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}

}
