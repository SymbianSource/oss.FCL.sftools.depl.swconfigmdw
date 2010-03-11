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

package com.symbian.sdb.contacts.dbms.model;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.symbian.sdb.exception.ContactHeaderCreationException;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreException;
import com.symbian.store.StoreInputStream;
import com.symbian.store.StoreOutputStream;

/**
 * 
 * 
 * @author tanaslam1
 *
 */
public abstract class AbstractContactHeader extends AbstractContactBlobField {

    /**
     * Contact-item field header set
     */
    protected List<ContactFieldHeader> contactFieldHeaders = new ArrayList<ContactFieldHeader>();

    // ~ Constructors =========================================================
    /**
     * Construct contact header from contacts header field list
     * @param contactFieldHeaders list of contacts header fields
     */
    public AbstractContactHeader(List<ContactFieldHeader> contactFieldHeaders) throws ContactHeaderCreationException {
        super();
        this.contactFieldHeaders = contactFieldHeaders;
        try {
        	persistFieldsToBlob();
        } catch (StoreException ex) {
        	throw new ContactHeaderCreationException("Creation of contact header failed: " + ex.getMessage(), ex);
        } catch (IOException ex) {
        	throw new ContactHeaderCreationException("Creation of contact header failed: " + ex.getMessage(), ex);
        }
    }
    /**
     * Construct contact header from blob data
     * @param blob blob header data
     * @throws Exception
     */
    public AbstractContactHeader(byte[] blob) throws ContactHeaderCreationException {
        super();
        this.value = blob;
        try {
        	constructContactHeaderFromBlob();
	    } catch (StoreException ex) {
	    	throw new ContactHeaderCreationException("Creation of contact header failed: " + ex.getMessage(), ex);
	    } catch (IOException ex) {
	    	throw new ContactHeaderCreationException("Creation of contact header failed: " + ex.getMessage(), ex);
	    }
    }

    // ~ Getter/Setter ===================================================
    
    /**
     * Gets an array list of parsed(if construction has been made through blob) 
     * contact field headers
     * 
     * @return list of contact field headers
     */
    public List<ContactFieldHeader> getFieldHeaderList() {

        return contactFieldHeaders;
    }

    /**
     * Read embedded store from blob and construct 
     * contact field header list
     *  
     * @throws StoreExpecption if store construction fails
     * @throws IOException if stream reading fails 
     */
    protected void constructContactHeaderFromBlob() throws StoreException, IOException {
        EmbeddedStore store = null;
        try {
            store = createStoreFromBlob(value);
            contactFieldHeaders = readFieldHeaderListFromStore(store);
        } finally {
            closeStore(store);
        }
    }
    
    /**
     * Generates binary header blob (in store format) 
     * 
     * @throws StoreException if store construction fails
     * @throws IOException if stream reading fails  
     */
    protected void persistFieldsToBlob() throws StoreException, IOException {

        EmbeddedStore store = createNewStore();
        writeContactHeaderToStore(store);
        this.value = store.getContent();
        closeStore(store);
    }
    
    /**
     * Implement this method to persist hint value for contact field header in blob 
     * @param stream Store stream to which data is being written
     * @param fieldHeader
     * @throws IOException
     */
    protected abstract void persistFieldHintValueToBlob(StoreOutputStream stream, 
		 									ContactFieldHeader fieldHeader) throws IOException;
/**
     * 
     * @param stream
     * @param fieldHeader
     * @throws IOException
     */
    protected abstract void persistFieldLabelToBlob(StoreOutputStream stream, 
											ContactFieldHeader fieldHeader) throws IOException;
    /**
     * Implement this method to read additional field header data from blob
     * 
     * @param stream Stream object to read data from
     * @param fieldHeader Contact field header object need to be populated.
     * @throws IOException if stream reading fails
     */
    protected abstract void readFieldHintValueFromBlob(StoreInputStream stream, 
    										ContactFieldHeader fieldHeader) throws IOException;
    /**
     * Implement this method to read additional field header data from blob
     * 
     * @param stream Stream object to read data from
     * @param fieldHeader Contact field header object need to be populated.
     * @throws IOException if stream reading fails
     */
    protected abstract void readAdditionalMappingsFromBlob(StoreInputStream stream, 
    										ContactFieldHeader fieldHeader) throws IOException;
    protected abstract void readVcardMappingFromBlob(StoreInputStream stream, 
											ContactFieldHeader fieldHeader) throws IOException;
    protected abstract void readFieldLabelFromBlob(StoreInputStream stream, 
											ContactFieldHeader fieldHeader) throws IOException;

    //~ Private methods -------------------------------------------------------------
	private EmbeddedStore createStoreFromBlob(byte[] blob) 
								throws StoreException {
		return new EmbeddedStore(blob);
	}
	
	private List<ContactFieldHeader> readFieldHeaderListFromStore(EmbeddedStore store)
								throws StoreException, IOException {
		StoreInputStream stream = null;
		try {
			stream = store.getInputStream(store.rootStream());
			return readFieldHeadersFromStream(stream);
		}
		finally {
			closeStream(stream);
		}
	}
	
	private List<ContactFieldHeader> readFieldHeadersFromStream(StoreInputStream stream)
								throws IOException {
		List<ContactFieldHeader> fieldHeaderList = new ArrayList<ContactFieldHeader>();
		int fieldCount = stream.readCardinality();
		for (int i = 0; i < fieldCount; i++) {
		    fieldHeaderList.add(createFieldHeaderFromStream(stream));
		}
		return fieldHeaderList;
	}
	
	private void closeStream(StoreInputStream stream) throws IOException {
		if( null != stream )
			stream.close();
	}
	
	private ContactFieldHeader createFieldHeaderFromStream(
			StoreInputStream stream) throws IOException {
		ContactFieldHeader field = readFieldHeaderDataFromStream(stream); //read and set field header
		return field;
	}
	
	private ContactFieldHeader readFieldHeaderDataFromStream(StoreInputStream stream) throws IOException {
		ContactFieldHeader fieldHeader = new ContactFieldHeader();
		fieldHeader.setAttributesContainer(readAttributesFromStream(stream)); //read and set attributes
		fieldHeader.setStreamId(stream.readUInt32()); //read and set stream Id
		readFieldHintValueFromBlob(stream, fieldHeader); //read hint value
		readAdditionalMappingsFromBlob(stream, fieldHeader);//read addition mappings
		readVcardMappingFromBlob(stream, fieldHeader); //read vCard mapping
		readFieldLabelFromBlob(stream, fieldHeader);
		return fieldHeader;
	}
	
	private ContactFieldAttribute readAttributesFromStream(
			StoreInputStream stream) throws IOException {
		//read attributes store  
		ContactFieldAttribute attrib = new ContactFieldAttribute();
		attrib.setCompositeAttributes(stream.readUInt32());

		//read extended attributes
		attrib.setExtendedAttributes(stream.readUInt32());
		return attrib;
	}   
    
 
    
	private void writeContactHeaderToStore(EmbeddedStore store) 
							throws StoreException, IOException {	
		StoreOutputStream stream = null;
		try{
        	stream = createRootStreamInStore(store);
            //write header data to store stream
            writeContactHeaderToStream(stream);
            //commit data to store
            store.commit();
        }
        finally {
        	closeStream(stream);	
        }
    }
	
	private StoreOutputStream createRootStreamInStore(EmbeddedStore store)
							throws StoreException {
		StoreOutputStream stream;
		stream = store.getOutputStream();
		store.setRoot(stream.getStreamId());
		return stream;
	}
	
	private EmbeddedStore createNewStore() 
							throws StoreException {
		EmbeddedStore store;
		store = new EmbeddedStore();
		return store;
	}
	
	private void writeContactHeaderToStream(StoreOutputStream stream)
							throws IOException {
		writeFieldCount(stream); //write field count
		writeContactHeaderFieldsToStream(stream); //write header fields
	}
	
	private void closeStore(EmbeddedStore store) {
		if( store != null )
			store.close();
	}
	
	private void closeStream(StoreOutputStream stream) throws IOException {
		if( stream != null )
			stream.close();
	}
	
	private void writeContactHeaderFieldsToStream(StoreOutputStream stream)
															throws IOException {
		for (ContactFieldHeader fieldHeader : contactFieldHeaders) {
		    writeFieldHeaderToStream(stream, fieldHeader);
		}
	}
	private void writeFieldHeaderToStream(StoreOutputStream stream,
									ContactFieldHeader fieldHeader) throws IOException {
		writeAttributeData(stream, fieldHeader); //write attributes
		writeStreamId(stream, fieldHeader);		//write stream id
		persistFieldHintValueToBlob(stream, fieldHeader); //write hints 
		persistAdditionalMappingsToBlob(stream, fieldHeader); //write additional mappings
		persistVcardMappingToBlob(stream, fieldHeader);//vCard mapping
		persistFieldLabelToBlob(stream, fieldHeader); //write field label
		
	}
    
	private void writeStreamId(StoreOutputStream stream,
										ContactFieldHeader fieldHeader) throws IOException {	
		stream.writeUInt32(fieldHeader.getStreamId()); //write stream Id
	}
	
	private void writeAttributeData(StoreOutputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		  
		stream.writeUInt32(getCompositeAttributes(fieldHeader)); //write attribute store
		stream.writeUInt32(getExtendedAttributes(fieldHeader));  //write extended attribute
	}
	
	private long getExtendedAttributes(ContactFieldHeader fieldHeader) {
		return fieldHeader.getAttributesContainer().getExtendedAttributes();
	}
	
	private long getCompositeAttributes(ContactFieldHeader fieldHeader) {
		return fieldHeader.getAttributesContainer().getCompositeAttributes();
	}
	
	private void writeFieldCount(StoreOutputStream stream) throws IOException {
		stream.writeCardinality(contactFieldHeaders.size());
	}

	public void persistAdditionalMappingsToBlob(StoreOutputStream stream, ContactFieldHeader fieldHeader)
	throws IOException {
		//write additional fields
		int additionalFieldCount = fieldHeader.getAttributesContainer().getAdditionalFieldCount();
		if (additionalFieldCount > 0) {
			for (int i = 0; i < additionalFieldCount; i++) //Hack
				stream.writeInt32((fieldHeader.getFieldAdditionalUIDValues())[i]);
		}
	}
	
	public void persistVcardMappingToBlob(StoreOutputStream stream,
			ContactFieldHeader fieldHeader) throws IOException {
		if(-1 != fieldHeader.getFieldVcardMapping())
			stream.writeInt32(fieldHeader.getFieldVcardMapping());	//write vCard mapping
	}
}
