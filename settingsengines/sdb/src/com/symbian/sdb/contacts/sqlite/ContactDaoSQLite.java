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
import java.util.Set;

import org.apache.log4j.Logger;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.dbms.ContactsDbValidator;
import com.symbian.sdb.contacts.speeddial.SpeedDialManager;
import com.symbian.sdb.contacts.sqlite.model.AbstractSQLiteContact;
import com.symbian.sdb.contacts.sqlite.model.SQLiteCommunicationAddress;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactCard;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactGroup;
import com.symbian.sdb.contacts.sqlite.model.SQLiteEmailAddress;
import com.symbian.sdb.contacts.sqlite.model.SQLitePhoneNumber;
import com.symbian.sdb.database.IConnectionProvider;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.ContactsFlow;
import com.symbian.sdb.mode.flow.SpeedDialModeType;

/**
 * Contact persistence interface for SQLite.
 * 
 * @author krzysztofZielinski
 *
 */
public class ContactDaoSQLite implements ContactsDbValidator {

	private static final Logger logger = Logger.getLogger(ContactsFlow.class);
	
    // ~ Injected Fields =======================================================
    private IConnectionProvider connectionProvider;
    private Set<SQLiteContactGroup> groupsInDB = null;
    private SpeedDialManager speedDialManager;
    
    // ~ Business Methods ======================================================
    
    /**
     * Save given contact in SQLite connectionProvider 
     * 
     * @param contact
     * @return
     */
    public SQLiteContactCard save(SQLiteContactCard contact) {
        
        saveContact(contact);
        // persist groups
        // TODO handle update.
//        for (SQLiteContactGroup contactGroup : contact.getGroups()) {
//            contactGroup = createGroup(contactGroup);
//            assignContactToGroup(contact,contactGroup);
//        }
        
        // persists associated emails
        for (SQLiteEmailAddress emailAddress : contact.getEmailAddresses()) {
            createCommunicationAddress(contact.getContactId(),emailAddress);
        }
        
        // persists associated phone numbers
        for (SQLitePhoneNumber phoneNumber : contact.getPhoneNumbers()) {
            createCommunicationAddress(contact.getContactId(),phoneNumber);
        }
        
        return contact;
    }
    
    /**
     * Persists communication address in a connectionProvider - used for email addresses and phone numbers
     * 
     * @param contactId id of contact this communication address belongs
     * @param communicationAddress
     */
    public void createCommunicationAddress(Long contactId, SQLiteCommunicationAddress communicationAddress) {
        Connection connection = getConnection();
        String sql = "INSERT INTO \"comm_addr\" VALUES(NULL,?,?,?,?);";
        PreparedStatement preparedStatement = null;
        
        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setInt(1, communicationAddress.getType().getValue());
            preparedStatement.setString(2, communicationAddress.getValue());
            preparedStatement.setString(3, communicationAddress.getExtraValue());
            preparedStatement.setLong(4, contactId);
            
            preparedStatement.execute();
        } catch (SQLException e) {
            throw new ContactsExeption(e);
        }
        finally {
        	GenericUtils.closeQuietly(preparedStatement);
        }
        
    }

    /**
     * Create group in a connectionProvider if necessary
     * 
     * @param contactGroup
     * @return
     */
    private SQLiteContactGroup createGroup(SQLiteContactGroup contactGroup) {
        
        // check if group already exists
        if (!updateGroupIfExists(contactGroup)) {
            // if group dosn't exists save it
            saveContact(contactGroup);    
        }
        return contactGroup;
        // group already exists there is no need to persist it
        // group should have assigned contactId   
    }

    /**
     * Query connectionProvider to check if given contact group exists in a connectionProvider.
     * In the case of successful lookup contact id is being assigned to the group 
     * 
     * @param contactGroup
     * @return
     */
    private boolean updateGroupIfExists(SQLiteContactGroup contactGroup) {
    	boolean r = false;
    	if(contactGroup.getContactId()!=null){
    		return true;
    	}
    	try {
			PreparedStatement statement = getConnection().prepareStatement("SELECT contact_id FROM contact WHERE text_fields = '"+contactGroup.getTextFields()+"';");
			boolean succeeded = statement.execute();
			if(succeeded){
				ResultSet result = statement.getResultSet();
				if (!result.isAfterLast()){
					contactGroup.setContactId(result.getLong(1));
					r = true;
				}
				result.close();
			}
			statement.close();
		} catch (SQLException e) {
			throw new ContactsExeption(e);
		}
		return r;
    }
    
    
    /**
     * Create association between group and contact
     * 
     * @param savedContact already saved contact (id must be already assigned)
     * @param savedContactGroup already saved contactGroup (id must be already assigned)
     */
    private void assignContactToGroup(SQLiteContactCard savedContact, SQLiteContactGroup savedContactGroup) {
        Connection connection = getConnection();
        String sql = "INSERT INTO \"groups\" VALUES(NULL,?,?);";
        PreparedStatement preparedStatement = null;
        
        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setLong(1, savedContactGroup.getContactId());
            preparedStatement.setLong(2, savedContact.getContactId());
            
            preparedStatement.execute();
        } catch (SQLException e) {
            throw new ContactsExeption(e);
        }
        finally {
        	GenericUtils.closeQuietly(preparedStatement);
        }
        // TODO KZ: should we check if association is unique?
    }

    /**
     * Persists contact in a connectionProvider - used for persisting contact cards and groups
     * 
     * @param contact
     */
    public void saveContact(AbstractSQLiteContact contact) {
        Connection connection = getConnection();
        String sql = "INSERT INTO \"contact\" VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);";
        PreparedStatement preparedStatement = null;
        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setInt(1, contact.getTemplateId());
            preparedStatement.setInt(2, contact.getTypeFlags());
            preparedStatement.setInt(3, contact.getAccessCount());
            preparedStatement.setLong(4, contact.getCreationDate());
            preparedStatement.setLong(5, contact.getLastModification());
            preparedStatement.setString(6, contact.getGuidString());
            preparedStatement.setString(7, contact.getFirstName());
            preparedStatement.setString(8, contact.getLastName());
            preparedStatement.setString(9, contact.getCompanyName());
            preparedStatement.setString(10, contact.getFirstNamePrn());
            preparedStatement.setString(11, contact.getLastNamePrn());
            preparedStatement.setString(12, contact.getCompanyNamePrn());
            preparedStatement.setBytes(13, contact.getTextFieldsHeader());
            preparedStatement.setBytes(14, contact.getBinaryFieldsHeader());
            preparedStatement.setString(15, contact.getTextFields());
            preparedStatement.setBytes(16, contact.getBinaryFields());
            
            preparedStatement.execute();
            
        } catch (SQLException e) {
            throw new ContactsExeption(e);
        } finally {
        	GenericUtils.closeQuietly(preparedStatement);
        }
        
        Long contactId = getLastInsertedContactId();
        contact.setContactId(contactId);
    }

    /**
     * Utility method to get connection to connectionProvider
     * 
     * @return
     */
    private Connection getConnection() {
        Connection connection = connectionProvider.getConnection();
        return connection;
    }

    /**
     * Returns last generated id for last inserted contact. 
     * No concurrent access to connectionProvider is assumed (no other insert contact operation is executed this connectionProvider in the meantime) - use transaction otherwise. 
     * 
     * @return
     */
    private long getLastInsertedContactId() {
        Connection connection = getConnection();
        
        String sql = "SELECT seq FROM sqlite_sequence WHERE name=\"contact\"";

        long lastInsertedCotnactId = 0;
        ResultSet resultSet = null;
        
        try {
            Statement statement = connection.createStatement();
            boolean thereAreSomeResults = statement.execute(sql);
            if (thereAreSomeResults) {
                resultSet = statement.getResultSet();
                lastInsertedCotnactId = resultSet.getLong(1);;
            }
            else    {
                throw new ContactsExeption("Problem retriving last inseted contact_id: no result");
            }
            statement.close();
        } catch (SQLException e) {
            // TODO KZ: change exception handling
            throw new ContactsExeption(e);
        }
        finally {
        	GenericUtils.closeQuietly(resultSet);
        }
        
        return lastInsertedCotnactId;
    }

    public AbstractSQLiteContact getContactFromDatabase(
    		AbstractSQLiteContact contact, 
    		int id) {
    	Connection connection = getConnection();
    	String sql = "SELECT * FROM contact WHERE contact_id=" + id;
	    try {
	    	Statement statement = connection.createStatement();
	    	ResultSet set = statement.executeQuery(sql);
	    	
	    	boolean result = set.next();
	    	if (result) {
	    		contact.setTemplateId(set.getInt(1));
	    		//contact.setTypeFlags(set.getInt(3));
	    		contact.setAccessCount(set.getInt(4));
	    		
	    		contact.setCreationDate(set.getLong(5));
	    		contact.setLastModification(set.getLong(6));
	    		
	    		contact.setGuidString(set.getString(7));
	    		
	    		contact.setTextFieldsHeader(set.getBytes(14));
	    		contact.setBinaryFieldsHeader(set.getBytes(15));
	    		contact.setTextFields(set.getString(16));
	    		contact.setBinaryFields(set.getBytes(17));
	    	}
	    	
	    	set.close();
	    	statement.close();
	    	
        } catch (SQLException e) {
            throw new ContactsExeption(e);
        }
    	return contact;
    }
    
	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.dbms.ContactsDbValidator#validateContactsDbSchema()
	 */
	public void validateContactsDbSchema() throws SDBValidationException {
        try	{
        	logger.debug("Validating Contacts schema in existing database");
        	queryExecutesSuccessfuly("SELECT contact_id FROM contact WHERE contact_id < 1");	
        	queryExecutesSuccessfuly("SELECT group_id FROM groups WHERE group_id < 1");
        	queryExecutesSuccessfuly("SELECT contact_id FROM comm_addr WHERE contact_id < 1");
        	queryExecutesSuccessfuly("SELECT preference_id FROM preferences WHERE preference_id < 1");
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

	/**
	 * @param speedDialManager the speedDialManager to set
	 */
	public void setSpeedDialManager(SpeedDialManager speedDialManager) {
		this.speedDialManager = speedDialManager;
	}
}
