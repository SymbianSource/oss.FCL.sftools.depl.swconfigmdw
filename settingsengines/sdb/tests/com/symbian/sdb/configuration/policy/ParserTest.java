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

package com.symbian.sdb.configuration.policy;

import java.io.File;
import java.io.IOException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import junit.framework.TestCase;

import org.w3c.dom.Document;
import org.xml.sax.SAXException;

import com.symbian.sdb.configuration.ConfigurationParser;
import com.symbian.sdb.configuration.DocumentVersion;
import com.symbian.sdb.configuration.policy.type.AlwaysType;
import com.symbian.sdb.configuration.policy.type.IDType;
import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;



public class ParserTest extends TestCase {	
	
	private File fTestXmlFile = new File("tests//config//XML//sec.xml");
	private SecuritySettings fSecSettings;
	
	public void setUp(){
	
		try {
			DocumentBuilder lBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
			Document lDocument = lBuilder.parse(fTestXmlFile);
			ConfigurationParser parser = new ConfigurationParser(DBType.SQLITE, DocumentVersion.V10);
			fSecSettings = parser.parseSecurityOptions(lDocument);
		} catch (ParserConfigurationException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		} catch (SAXException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		} catch (IOException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		} catch (SDBExecutionException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		}
	}
	

	
	/**
	 * This method checks that the correct number of policies are present 
	 * in the parsed xml file. The reason for seperating out and checking
	 * each time at a deeper level is an attempt to remove the dependancy
	 * of our tests success on an external resource ie. the xml file
	 * this way a change in the xml file wont result in all tests
	 * failing
	 *
	 */
	public void testCorrectNumberPolicies(){			
		assertTrue(fSecSettings.getPolicies().size() == 4);		
	}
	
	/**
	 * Tests the attributes are correctly set
	 *
	 */
	public void testAttributes(){
		
		for(Policy lPolicy : fSecSettings.getPolicies()){
			
			if(lPolicy.getClass().getName().endsWith("PolicyID") && ((PolicyID)lPolicy).fType.equals(IDType.VID)){
				assertTrue(((PolicyID)lPolicy).fPolicyType.equals(PolicyType.SCHEMA));
				assertTrue(((PolicyID)lPolicy).fId.equals("4660"));
			}
			else if(lPolicy.getClass().getName().endsWith("PolicyID") && ((PolicyID)lPolicy).fType.equals(IDType.SID)){
				assertTrue(((PolicyID)lPolicy).fPolicyType.equals(PolicyType.WRITE));
				assertTrue(((PolicyID)lPolicy).fId.equals("120"));
			}
			else if(lPolicy.getClass().getName().endsWith("PolicySet")){
				assertTrue(((PolicySet)lPolicy).fPolicyType.equals(PolicyType.READ));
			}
			else if(lPolicy.getClass().getName().endsWith("PolicyAlways")){
				assertTrue(((PolicyAlways)lPolicy).fAlwaysType.equals(AlwaysType.PASS));
				assertTrue(((PolicyAlways)lPolicy).fPolicyType.equals(PolicyType.DEFAULT));
			}
		}
	}
	
	
	/**
	 * Tests the correct number of capabilities are set
	 * 
	 */
	public void testCapabilities(){
		for(Policy lPolicy : fSecSettings.getPolicies()){
			
			if(lPolicy.getClass().getName().equals("PolicySet")){
				assertTrue(((PolicySet)lPolicy).getCapabilities().size()==5);
			}			
		}
	}
	
	
	public void testWrongPolicies(){
		
		try {
			DocumentBuilder lBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
			Document lDocument = lBuilder.parse("tests//config//XML//bad1.xml");
            ConfigurationParser parser = new ConfigurationParser(DBType.SQLITE, DocumentVersion.V10);
            fSecSettings = parser.parseSecurityOptions(lDocument);
			fail("Expected Exception not thrown.");
		} 
		catch (ParserConfigurationException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		} 
		catch (SAXException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
		catch (IOException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		} 
		catch (SDBExecutionException ex) {
			//succeed
		}
		
	}
	
	
	public void tearDown(){
		
	}
}
