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


package com.symbian.sdb.contacts.importer;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.junit.Test;

import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.contacts.helper.HexStringConverter;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.model.EmailAddress;
import com.symbian.sdb.contacts.model.PhoneNumber;
import com.symbian.sdb.contacts.template.ITemplateManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.TemplateManager;
import com.symbian.sdb.contacts.template.TemplateMapper;

public class VCardContactImporterTest extends BaseIntegrationTestCase	{

	static TemplateMapper mapper;
	static HashMap<String, Set<HashMap<String, Set<String>>>> model;
	
	ITemplateModel templateModel;
	VCardContactImporter contactImporter;
	
	public static junit.framework.Test suite() { 
		return new JUnit4TestAdapter(VCardContactImporterTest.class); 
	}

	public void onSetUp() throws Exception {
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		mapper = TemplateMapper.getInstance();

		ITemplateManager manager = new TemplateManager();
		templateModel = manager.parse("tests/config/CNTMODEL.RSS");
	}
	
	@Test
    public void testReadPhoto() {
		File myFile = new File("testdata/contacts/vcard/vcard_with_image.vcf");
		List<File> list = new ArrayList<File>();
		
		list.add(myFile);

		Set<Contact> contacts = contactImporter.importContacts(list, templateModel);
		
		for (Contact someone : contacts) {			
			Set<ContactField> someonesFields = someone.getFields();
			
			for (ContactField field : someonesFields) {			
				if (field.getTemplateFieldId() == 57) {
					String hexFromVcard = HexStringConverter.convertByteArrayToHexString(field.getBinaryValue());

					String whatItShouldBe = "ffd8ffe000104a46494600010101006000600000ffe1006e45786966000049492a0008000000010069870400010000001a000000000000000100869202003a0000002c0000000000000043524541544f523a2067642d6a7065672076312e3020287573696e6720494a47204a50454720763632292c207175616c697479203d2039350a00ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc00011080032003203012200021101031101ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00f55b6d23c456dae6b77536bc5ed2f10ad94623ddf6763f75b69e06de981f7fab60d677fc23be2dff00842ffb27fe1223fdabe7f99f69deff00eaf3feafccc6febf36ec67f87a73536816ba6dbf8f35fb8b3d7a5bdbc948f3ec99b88b9f5e8fb4fca31f701da7935cdea3abebb0ebfe265f186b5a75878622963160d08dcecd9f9542afceff002e4b83d1c02bf2835e7c28d6aee4a827292fb2badfa27e7f86c7a38fcc6a609ae55194ad16938a8dda8e8b55f8f5dd6875d77a4f88a7d6b45bb875d2b6964816f63f2f6fda187de6da383bba60fdceab9345a693e22835ad6aee6d74b5a5ea15b28fcbddf6763f75b69e06de981f7fab60d71526b3aba6a3af7fc251e21d3a1f08a793fd99730b79af3671b3684f9a4cae4be7f8c02bf283449aceae9a8ebdff0009478874e87c229e4ff665cc2de6bcd9c6cda13e6932b92f9fe300afca0d68f01983bf2464ddb4f3976fbacbe773cc96795395c63183d2cbe0d5ddb71db74d6ffe474bff0008ef8b7fe10bfec9ff008488ff006af9fe67da77bffabcff00abf331bfafcdbb19fe1e9cd68dce91e22b9d7344ba875e296966816f6331edfb430fbcdb4707774c1fb9d5726b93b4b9f116a1ad6bb6fae6b7603c2e8226d3278184ad28e3611b797cae4beefe3da57e506b7355b3d2e6f19786a6b9f11cd6f750a62dedfccddf681d8eee8bbfee927fd60f94722b9e4aa52aea94dbe9d7f07daddfed6c8f43039a4f1b889d35cb64a52ba5196ad34d592bab5b7d96b7d8eea8a28af50e138ad06ef4c9fc79afdbda6832d8de44479d7acbc4bcfa744dc7e618fbe06e3c8ae3fc47f6bd2f56f125dfc43d36caebc273cf1a6991da2e67693395f2c82194ec0e642c4648c2e41c1e9758f146abe10bfd5353f14846d04cab169f1da20695dcf202f23f84316de4723e5e3838b6361aa6b7e2ed696f3c4c9aa687ac4515c5858cf6e4c5b0e24405587eecaae3ee83bfab618629e5fcd85ab1c456bc69ca49277e5bb5d1767e9b8f3daf460e33694a4947955f9bdee5d937d7756e9b232afe65b3fed8d47c63a669f73e04bbfb3ff6245630ed95b23745e50055a3fdd862fbcaf230bc1c12fe65b3fed8d47c63a669f73e04bbfb3ff6245630ed95b23745e50055a3fdd862fbcaf230bc1c1d1b3d3f58bed43c597fabf899754d0643188ac27b6ca9c30287610563c1181b7ef9f99f69147f67eb0750d52ff5df132ea7a0eb2505a584d6d955d8c092c846d8f6118f9376f3f31e4575d1cdb09154dcaabb2936fdff00b374935a68efa5ff00a5e04f1d85846528c15a31e75f0eadb69db5defa37ddfdf269a35b8752d6751d474bd36e3c1d711c2da3adaaf94446403195c0dd18d9f7f701f3950bf2e6ba0d56f74a8bc65e1b86e3c3935c5d4abfe8f71e5edfb38ecbb470db3ef107fd58f98726b3f489358f0e78ff00c4975e22f15bde692d6fe7436fe4b6d842aef3f281f2154046133bf393f3002ad68fe28d57c5f7fa5ea7e1608ba0895a2d423bb40b2a38e486e4ff000952bb09e4fcdc703c8ad42a57aaf174fde845a8b7bd9f66fafcf6dd6e7bb932a31c4d49c1c5271926b48da4936ef28eadddfc3b37a753d028a28aeb19e7d0683e1ed4bc43e2db69f5f7bd379115bbb4908c403aeecb6558c6400a71fbbe879acdff00842347ff00856dfd99ff00092cbb3ed1bbedbe57fb59f27cbceed9fc5b73f7be7f6ad9d2f50d23fe12df14a41e17b88eeade22d7132c5bcdc81d5421e14bf5007facea79aa3ff094699ff0adbfb57fe1199fecdf6af2fecfbceddd9ff59e6e33b7f87763ef7cbd39ae3facd6a71e5a6d595deb7dd3dffcff0003d5c7e1f33ab562f0c93d20bdeb5f99c7dcdb4b6fe7b5f52dea1e13d266f12f872e4ebf708d6b1e0425837db38fbecc38cc9d1c907cc1c71469fe13d261f12f88ee46bf70ed751e0c2182fd8f8fbeac78cc7d10803cb1c7356b50d76c61f12f86ed1bc3b76d25e441a290c7b0db823852bd094eac3f807233469faed8cde25f125a2f876ed64b388b4b208f79b80072a17a02fd547f18e4e2abeb15afcb78daf6d9ed6bfdf7d7d3ccf3fea79a72df963cb6bffdbb7b7dfcff0081cfff00c211a3ff00c2b6feccff0084965d9f68ddf6df2bfdacf93e5e776cfe2db9fbdf3fb5694fa0f87b4df10f84ada0d7dec8d9c416d2d2323138ebbb2b8553212431c7ef3a0e6a0ff84a34cff856dfdabff08ccff66fb5797f67de76eecffacf3719dbfc3bb1f7be5e9cd5ed5350d23fe12df0b24fe17b892eae220d6f3345b0db03d14a0e18a7520ffabea39a9facd6a91e5a8d59d9e97ddbdffcbf13d0c061f33a5564f1292d26bddb5f9947dfdf4b6de7bdb53baa28a2bb0f2828a28a0028a28a0028a28a0028a28a00ffd9";

					Assert.assertEquals(hexFromVcard, whatItShouldBe);
				}
			}
		}
	}
	
	
	// DPDEF138364 - SDB raised exception when vcard contains empty lines under END:VCARD	
	@Test
    public void testVCardWithEmptyLines() {
		File myFile = new File("testdata/contacts/vcard/vcard_with_empty_lines.vcf");
		List<File> list = new ArrayList<File>();
		
		list.add(myFile);

		contactImporter.importContacts(list, templateModel);
	}

	
	@Test
    public void testUpdateEmptyDatabaseWithAll() {
		
		List<File> list = new ArrayList<File>();
		
		File myFile = new File("testdata//vCards//supportedSimpleTypes.vcf");
		
		list.add(myFile);
		Set<Contact> contacts = contactImporter.importContacts(list, templateModel);
		
		for (Contact someone : contacts) {
			Assert.assertEquals(someone.getFirstName(), "n2");
			Assert.assertEquals(someone.getLastName(), "n1");
			Assert.assertEquals(someone.getCompanyName(), "Symbian Ltd; Integration & Variant Tools;");			
					
			Set<ContactField> someonesFields = someone.getFields();
			
			for (ContactField field : someonesFields) {
				switch (field.getTemplateFieldId()) {
					case 0: Assert.assertEquals(field.getTextValue(), "n4"); break;
					case 1: Assert.assertEquals(field.getTextValue(), "n2"); break;
					case 2: Assert.assertEquals(field.getTextValue(), "n3"); break;
					case 3: Assert.assertEquals(field.getTextValue(), "n1"); break;
					case 4: Assert.assertEquals(field.getTextValue(), "n5"); break;
					case 15: Assert.assertEquals(field.getTextValue(), "postcode"); break;
					case 17: Assert.assertEquals(field.getTextValue(), "po box"); break;
					case 18: Assert.assertEquals(field.getTextValue(), "extended address"); break;
					case 19: Assert.assertEquals(field.getTextValue(), "street"); break;
					case 20: Assert.assertEquals(field.getTextValue(), "city"); break;
					case 21: Assert.assertEquals(field.getTextValue(), "county"); break;
					case 22: Assert.assertEquals(field.getTextValue(), "www.home.com"); break;
					case 25: Assert.assertEquals(field.getTextValue(), "Symbian Ltd; Integration & Variant Tools;"); break;
					case 26: Assert.assertEquals(field.getTextValue(), "Job Title"); break;
					case 37: Assert.assertEquals(field.getTextValue(), "www.work.com"); break;
					case 38: Assert.assertEquals(field.getTextValue(), "postcode w"); break;
					case 40: Assert.assertEquals(field.getTextValue(), "po box w"); break;
					case 41: Assert.assertEquals(field.getTextValue(), "extended address w"); break;
					case 42: Assert.assertEquals(field.getTextValue(), "street w"); break;
					case 43: Assert.assertEquals(field.getTextValue(), "city w"); break;
					case 44: Assert.assertEquals(field.getTextValue(), "county w"); break;
					case 47: Assert.assertEquals(field.getTextValue(), "2000-01-01"); break;
					case 48: Assert.assertEquals(field.getTextValue(), "This is a note"); break;
					case 70: Assert.assertEquals(field.getTextValue(), "11111; 22222"); break;
					case 14: Assert.assertEquals(field.getTextValue(), "home@somewhere.com"); break;
					case 36: Assert.assertEquals(field.getTextValue(), "work@somewhere.com"); break;
					case 5: Assert.assertEquals(field.getTextValue(), "006"); break;
					case 6: Assert.assertEquals(field.getTextValue(), "007"); break;
					case 7: Assert.assertEquals(field.getTextValue(), "008"); break;
					case 9: Assert.assertEquals(field.getTextValue(), "010"); break;
					case 10: Assert.assertEquals(field.getTextValue(), "011"); break;
					case 12: Assert.assertEquals(field.getTextValue(), "013"); break;
					case 13: Assert.assertEquals(field.getTextValue(), "014"); break;
					case 27: Assert.assertEquals(field.getTextValue(), "026"); break;
					case 28: Assert.assertEquals(field.getTextValue(), "027"); break;
					case 29: Assert.assertEquals(field.getTextValue(), "028"); break;
					case 30: Assert.assertEquals(field.getTextValue(), "029"); break;
					case 31: Assert.assertEquals(field.getTextValue(), "030"); break;
					case 32: Assert.assertEquals(field.getTextValue(), "031"); break;
					case 34: Assert.assertEquals(field.getTextValue(), "033"); break;
					case 35: Assert.assertEquals(field.getTextValue(), "034"); break;
					default: /* These are extra field that we don't really care about */ break;
				}
			}
			
			Set<PhoneNumber> phoneNumbers = someone.getPhoneNumbers();

			for (PhoneNumber field : phoneNumbers) {
				switch (field.getTemplateFieldId()) {
					case 5: Assert.assertEquals(field.getTextValue(), "006"); break;
					case 6: Assert.assertEquals(field.getTextValue(), "007"); break;
					case 7: Assert.assertEquals(field.getTextValue(), "008"); break;
					case 9: Assert.assertEquals(field.getTextValue(), "010"); break;
					case 10: Assert.assertEquals(field.getTextValue(), "011"); break;
					case 12: Assert.assertEquals(field.getTextValue(), "013"); break;
					case 13: Assert.assertEquals(field.getTextValue(), "014"); break;
					case 27: Assert.assertEquals(field.getTextValue(), "026"); break;
					case 28: Assert.assertEquals(field.getTextValue(), "027"); break;
					case 29: Assert.assertEquals(field.getTextValue(), "028"); break;
					case 30: Assert.assertEquals(field.getTextValue(), "029"); break;
					case 31: Assert.assertEquals(field.getTextValue(), "030"); break;
					case 32: Assert.assertEquals(field.getTextValue(), "031"); break;
					case 34: Assert.assertEquals(field.getTextValue(), "033"); break;
					case 35: Assert.assertEquals(field.getTextValue(), "034"); break;
					default: Assert.assertFalse(field.getTemplateFieldId() + " " + field.getTextValue(), true); break;			
				}
			}
			
			Set<EmailAddress> emailAddresses = someone.getEmails();
			
			for (EmailAddress field : emailAddresses) {
				switch (field.getTemplateFieldId()) {
					case 14: Assert.assertEquals(field.getTextValue(), "home@somewhere.com"); break;
					case 36: Assert.assertEquals(field.getTextValue(), "work@somewhere.com"); break;
					default: Assert.assertFalse(field.getTemplateFieldId() + " " + field.getTextValue(), true); break;
				}
			}
		}
	}

	/**
	 * @param contactImporter the contactImporter to set
	 */
	public void setContactImporter(VCardContactImporter contactImporter) {
		this.contactImporter = contactImporter;
	}

}
