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

package com.symbian.sdb.contacts.sqlite.model;
import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;
import static junit.framework.Assert.fail;

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.apache.commons.io.FileUtils;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.contacts.helper.HexStringConverter;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.mode.DBType;
import com.symbian.store.EmbeddedStore;
import com.symbian.store.StoreInputStream;



/**
 * Unit test for FieldHeader Class
 * @author Tanaslam1
 *
 */

public class BinaryFieldBlobTest {
	
	
	private static DBManager dbManager = null;
	private static File db;
	
	
	private final int attribFlags = 0x100204;
	private final int streamId = 0x4;
	private final long templateId = 0x2;
	private final long fieldGuid = 0x31;
	
	@BeforeClass
	public static void createTempDB() throws Exception {
		db = File.createTempFile("binaryfieldtestTemp", "db");
		FileUtils.copyFile(new File("tests/config/binaryfieldtest.db"), db);
	}
	
	@Before
	public void setUp() throws Exception {
		System.setProperty("org.sqlite.lib.path", "lib/");
		//library path for EmbeddedStore native DLL
		System.setProperty("com.symbian.dbms.lib.path", "lib/"); 
		if (null == dbManager)    {
		    dbManager = new DBManager();    
		}
	}
	
	@Test   
	public void testBinaryFieldHeaderObject() throws Exception {
		
		FieldHeader header  =  new FieldHeader();
		header.setAttributes(this.attribFlags);

		header.setStreamId(this.streamId);
		header.setFieldId(this.templateId);
		header.setContactFieldGuid(this.fieldGuid);
		
		assertEquals(this.attribFlags, header.getAttributesContainer().getValue());
		assertEquals(this.streamId, header.getStreamId());
		assertEquals(this.templateId, header.getFieldId());
		assertEquals(this.fieldGuid, header.getContactFieldGuid());
		
	}
	
	@Test
	public void testBinaryFieldObject() throws Exception {
		
		BinaryField field = new BinaryField();
		
		//Initialise header of the field
		FieldHeader header  =  new FieldHeader();
		header.setAttributes(this.attribFlags);

		header.setStreamId(this.streamId);
		header.setFieldId(this.templateId);
		header.setContactFieldGuid(this.fieldGuid);
		
		//Set header
		field.setHeader(header);
		
		String hexData = "00000000450900002D4AFFD8FFE000104A46494600010100000100010000FFDB008400080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C2837292C30313434341F27393D38323C2E333432010909090C0B0C180D0D1832211C213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232FFC00011080060005003012200021101031101FFC401A20000010501010101010100000000000000000102030405060708090A0B100002010303020403050504040000017D01020300041105122131410613516107227114328191A1082342B1C11552D1F02433627282090A161718191A25262728292A3435363738393A434445464748494A535455565758595A636465666768696A737475767778797A838485868788898A92939495969798999AA2A3A4A5A6A7A8A9AAB2B3B4B5B6B7B8B9BAC2C3C4C5C6C7C8C9CAD2D3D4D5D6D7D8D9DAE1E2E3E4E5E6E7E8E9EAF1F2F3F4F5F6F7F8F9FA0100030101010101010101010000000000000102030405060708090A0B1100020102040403040705040400010277000102031104052131061241510761711322328108144291A1B1C109233352F0156272D10A162434E125F11718191A262728292A35363738393A434445464748494A535455565758595A636465666768696A737475767778797A82838485868788898A92939495969798999AA2A3A4A5A6A7A8A9AAB2B3B4B5B6B7B8B9BAC2C3C4C5C6C7C8C9CAD2D3D4D5D6D7D8D9DAE2E3E4E5E6E7E8E9EAF2F3F4F5F6F7F8F9FAFFDA000C03010002110311003F00F7EAE7FC51E31D2BC276D1BDF3BC97139DB6F6902EF9A76F455FEBD28F18F8A20F09E8325FBC467B87610DADB27DE9E56E1547F5F615CB7863C313DBDD3EBFAFBADDF886E866490F2B6EBDA28C7603A6475AF2B34CD2965F4B9E7AC9ECBBFF00C02E107376440CDE3BF15379B737A9E18D3DB95B6B6025BA61FED39E14FD3F2A6B7C2FD02E403A9CBA96A72777BCBE91C9FC0102BB5A2BF3EC4F10E615E57E7E55DA3A7FC1FC4EA54A0BA1C527C2BF0CDBE5AC63BDB093B496B7B2A30FFC7A97FB3FC6FE1A225D1F5B1AE5AA8E6C755004847A2CC3BFD7F5AED28A9C3E7F985095FDA392ECF5FCC6E941F429785BC75A7F896596C5A2974FD6201FE91A75CF1227B8FEF2FB8FD2BAAAF3FF001478561D7E28AE6DE5365AC5A7CF677D1F0F1B0EC7D54F715A7E05F15CDE21B1B8B4D4A25B6D734E7F26FA01D377675FF658722BEFF28CE296634DD95A6B75FAAF2396A5370675D451457B266797485BC55F14EEA797E6D3FC368208149F95AE9C65DBEAAB81F953FE25F89E7F0A78367BDB4205DCAEB042C4676B37F17E001FC6A2F860C2E7C3171A991FBCD4750B9BA63EB99081FA0157BC7DE173E2EF0A5C69B1BAA5C8225819BA6F5E80FB1E47E35F9B6618AA75B3A5F58F82324BCACBFE0EE75C22D53D373E6DD1BC7DE22D23598F515D4EEA76DE0CB1CD33324A3B820FF915F595A5D25ED9C3731E764D1AC8B9F46008FE75F32E8DF08BC537FAD47697B612595B2B8F3AE2465DA17BEDC13B8FA62BE9DB7823B6B78E08976C71A0451E800C0FD0574715D4C1CE54FD834E5ADED6DBA5EDF80A8292BDCCDF136B0340F0DEA1AAEC0E6D6069154F42DD00FCC8AF95DFC75E267D5BFB4CEB3782EB7EE044A428F6DBF771ED8AFAB75DD262D7742BDD2E66DB1DD42D196033B491C1FC0E0D7CD2FF0008FC60BABFD8069BB977E05D071E563FBDBB3D3DB19F6AD785AAE0A14AA2ACD2979DB6F9FCEE2AEA57563E8CF08EB87C49E15D3F56650925C440C8A3A07190D8F6C83589E241FF0008CF8CB45F15C2764334ABA76A207468DCFC8C7FDD6C7E95D0786B448FC3BE1DB1D2626DEB6D1042F8C6E6EA4FE249ACDF88B64B7FF0FF005A89BAADB348BEC570C0FE95E365F8A8E1F3453A1F0395BFEDD6EC6938B70B3DCF4614566F876F5B52F0C6937EE72F73670CCC7D4B203FD6B4ABF55388F2CF85ABF67F06FD809FDE58DE5C5B38F42B237F422BB04B981E79205963696300BA0605973D323A8AE42C73E1AF89DABE93280969AD81A8D99E83CD0312A8F7E037FF00AEB37E2A7842EB57B08B5CD15A58F59D3D4906062AF2C7D4A8239C8EA3F11DEBF33CCB01079B4E955972A9BBA7D35EFE57D3C8EC849FB3BAE87A3515F2DE95F183C5FA58546BE4BC8D78DB751863FF007D0C1FD6BA287E3F6B0A079DA358487B95775FEA6AAAF09E3E2FDCB497AFF9895789F41515F3FCBF1FF5565FDD6896487D5A476FEA2B0B52F8D1E2FBF0562B8B7B253DADE119FCDB26953E13CC24FDEB2F9FF95C6EBC0FA627B886D903CF2A46A58282EC1724F41CF7AC0F88176967E01D6E57381F64741F561B47F3AF3EF857E14D4F57BA4F17F8967B8B97507EC0972E58F3D64C1E83D3F3F4AEBFC6806BFAD689E0F846FF00B65C2DD5E8033B2DA23B8E7FDE6000FA567432C8C333A785A73E769A726968ADAB5F2FCF4073F71B3BEF0B5ABD8F84745B49010F058411303D8AC6A0FF002AD6A28AFD3CE3394F1CF85A4F12E9111B2945BEAF6327DA2C2E3FB920EC7FD961C1FF00EB564F857C509AF5BCB6F7517D8F58B33E5DED93F0D1B8EE3D54F506BD02B91F15F816D7C41711EA767732699AE5BAE20D4201CE3FBAE3F8D7D8D78D9C6514F31A495ED35B3FD1F91A53A8E0CF33F887F07D7599E5D5BC3C6386F5C969AD58ED494FAA9FE16F6E87DBBF876ABE1FD5B4494C7A969D736AC0E3F791900FD0F435F4C0F137887C323C9F166833490A70353D2D0CD130F5641F3255FB3F885E12D423DD16BD6433FC32C9E591F8362BC3A38FCDB2D8FB1C4517522B67AFE6AFF8AB9A38539EA9D8F9474FD2AFF559FC8B0B39EE65FEEC31963FA74AF64F017C1691278F52F14AA8552192C01CE4FF00D3423B7FB23F1F4AF4DB9F1DF84EC622D26BDA7851DA39839FC97359A3C6BA8EBE043E0FD02EAFCBF02FAED0C16C9EF96C16FA0A75B34CD71F1F6586A2E09EEFFE0B492FCC14211D64CDCF10F886C3C2BA48B9B8196388EDEDA21F3CCFD151147E1F4A4F00F86AF2CBED9E21D7957FB7754C1910722DA21F7225FA77F7FA51E1AF011B3D4975EF115EFF006B6BB8C2485710DB0FEEC49DBFDEEBF4AEE2BD7C9726865F07293BD47BBFD17F5A99D4A8E6FC85A28A2BDD330A28A2800ACBBDF0D683A94864BFD134DBA73C969ED23727F122B528A00C7B5F09786EC64125A787F4AB770721A2B28D0FE6056C631451400514514005145140051451400514514005145140051451400514514000FFD9";
		
		byte[] dataIn = HexStringConverter.convertHexStringToByteArray(hexData);
		
		//set data length
		field.setLength(dataIn.length);
		//set data
		field.setData(dataIn);
		
		//Read data back from object
		
		//Read header
		header = field.getHeader();
		assertEquals(this.attribFlags, header.getAttributesContainer().getValue());
		assertEquals(this.streamId, header.getStreamId());
		assertEquals(this.templateId, header.getFieldId());
		assertEquals(this.fieldGuid, header.getContactFieldGuid());
		
		//Read binary data length
		assertEquals(dataIn.length, field.getLength());
		
		//Read data and compare
		byte[] dataOut = field.getData();
		assertTrue(dataOut.equals(dataIn));	
	}
	
	/**
	 * 
	 * @throws Exception
	 */
	@Test
	public void testBinaryHeaderRead() throws Exception {
		
		Connection conn = null;
		Statement st = null;
		ResultSet rs = null;
		
		dbManager.openConnection(DBType.SQLITE, db.getAbsolutePath());
		
		//fail if connection unsuccessful
		assertTrue((conn = dbManager.getConnection()) != null );  
		
		try {
			
			st = conn.createStatement();
			rs = st.executeQuery("SELECT binary_fields_header FROM contact WHERE contact_id = 1");
		
			while( rs.next() ) {
				byte[] blob = rs.getBytes(1);
				
				FieldHeader[] headers = FieldsHeaderReader.read(blob);
				for(int i = 0; i < headers.length; i++) {
					assertEquals(this.attribFlags, headers[i].getAttributesContainer().getAttributes());
					assertEquals(this.streamId, headers[i].getStreamId());
					assertEquals(this.templateId, headers[i].getFieldId());
					assertEquals(this.fieldGuid, headers[i].getContactFieldGuid());
				}
			} 
		}
		catch (SQLException sqlerr) {
			fail("Unable execute SQL statement");
		}
		catch (Exception err) {
			fail ("Unable to read store");
		}
		finally {
			rs.close();
			st.close();
		}
	}
	
	/**
	 * 
	 * @throws Exception
	 */
	@Test
	public void testBinaryHeaderWrite() throws Exception {
		
		Connection conn = null;
		Statement st = null;
		ResultSet rs = null;
		FieldHeader[] headers = null;
		
		dbManager.openConnection(DBType.SQLITE, db.getAbsolutePath());
		
		//fail if connection unsuccessful
		assertTrue((conn = dbManager.getConnection()) != null );  
		
		try {
			
			st = conn.createStatement();
			rs = st.executeQuery("SELECT binary_fields_header FROM contact WHERE contact_id = 9");
		
			while( rs.next() ) {
				
				byte[] blob = rs.getBytes(1); 
				headers = FieldsHeaderReader.read(blob);
			
				//get bytes from store persisted object
				blob = BinaryFieldsHeaderWriter.write(headers);
				
				//Create new store object from blob and validate data
				EmbeddedStore store = new EmbeddedStore(blob);
				StoreInputStream is = store.getInputStream(store.rootStream());
				int headercount = is.readCardinality();
				for(int idx = 0 ; idx < headercount; idx++ ) {
					assertEquals(this.attribFlags, is.readInt32());
					assertEquals(this.streamId, is.readInt32());
					assertEquals(this.templateId, is.readInt32());
					assertEquals(this.fieldGuid, is.readInt32());
				} 
			}
			
		}
		catch (SQLException sqlerr) {
			fail("Unable execute SQL statement");
		}
		catch (Exception err) {
			err.printStackTrace();
			fail ("Unable to read store");
		}
		finally {
			rs.close();
			st.close();
		}		
	}
	
	@Test
	public void  testBinaryFieldReadWrite() throws Exception {
		
		Connection conn = null;
		Statement st = null;
		PreparedStatement pst =null;
		ResultSet rsh = null;
		ResultSet rsf = null;
		
		byte[] blobOutHeaders = null;
		byte[] blobOutFields = null;
		byte[] blobInHeaders = null;
		byte[] blobInFields = null;
		byte[] imageData = null;
		
		
		FieldHeader[] headers  = null;
		BinaryField[] fields = null;
		
		dbManager.openConnection(DBType.SQLITE, db.getAbsolutePath());
		
		//fail if connection unsuccessful
		assertTrue((conn = dbManager.getConnection()) != null );  
		
		try {
			
			//Read JPEG image from another record
			imageData = ReadImageDataFromDb(conn);
			
			
			st = conn.createStatement();
			rsh = st.executeQuery("SELECT binary_fields_header FROM contact WHERE contact_id = 9");
		
			while( rsh.next() ) {
				
				blobOutHeaders = rsh.getBytes(1);
				
				headers = FieldsHeaderReader.read(blobOutHeaders);
				for(int i = 0; i < headers.length; i++) {
					assertEquals(this.attribFlags, headers[i].getAttributesContainer().getValue());
					assertEquals(this.streamId, headers[i].getStreamId());
					assertEquals(this.templateId, headers[i].getFieldId());
					assertEquals(this.fieldGuid, headers[i].getContactFieldGuid());
				}
				
				rsf = st.executeQuery("SELECT binary_fields FROM contact WHERE contact_id = 9");
				
				while( rsf.next() ) {
					
					blobOutFields = rsf.getBytes(1);
					
					fields = BinaryFieldsReader.read(blobOutFields, headers);
				
					for(int i = 0; i < fields.length; i++) {
						assertEquals(this.attribFlags, fields[i].getHeader().getAttributesContainer().getValue());
						assertEquals(this.streamId, fields[i].getHeader().getStreamId());
						assertEquals(this.templateId, fields[i].getHeader().getFieldId());
						assertEquals(this.fieldGuid, fields[i].getHeader().getContactFieldGuid());
					}
				}
			}
			
			//Replace image data
			fields[0].setLength(imageData.length);
			fields[0].setData(imageData);
			
			blobInFields = BinaryFieldsWriter.write(fields);
			blobInHeaders = BinaryFieldsHeaderWriter.write(headers) ;
			
			//assertTrue(Arrays.equals(blobOutHeaders, blobInHeaders));
			//assertTrue(Arrays.equals(blobOutFields, blobInFields));
			
			pst = conn.prepareStatement("UPDATE contact SET binary_fields_header = ?, binary_fields = ? WHERE contact_id = 9");
			//pst = conn.prepareStatement("UPDATE contact SET binary_fields = ? WHERE contact_id = 9");
			pst.setBytes(1, blobInHeaders);
			pst.setBytes(2, blobInFields);
			// TODO why doesn't execute work? changed to execute batch: http://news.gmane.org/gmane.comp.db.sqlite.jdbc 	
			// 28 Mar 15:56 magowiz sqlitejdbc v043 pure java : cannot commit transaction - SQL statement
			pst.executeBatch();
			
		}
		finally {
			if(rsf != null )
				rsf.close();
			if(rsh != null )
				rsh.close();
			if(st != null )
				st.close();
		}
	}
	
	private byte[] ReadImageDataFromDb(Connection conn) throws Exception {
		
		Statement st = conn.createStatement();
		ResultSet rsh = st.executeQuery("SELECT binary_fields_header FROM contact WHERE contact_id = 10");
		FieldHeader[] headers = FieldsHeaderReader.read(rsh.getBytes(1));
		ResultSet rsf = st.executeQuery("SELECT binary_fields FROM contact WHERE contact_id = 10");
		BinaryField[] fields = BinaryFieldsReader.read(rsf.getBytes(1), headers);
		
		return fields[0].getData();
	}

	@AfterClass
	public static void tearDown() throws Exception {
		dbManager.closeConnection();
	}

}
