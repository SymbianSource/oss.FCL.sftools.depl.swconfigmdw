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

package com.symbian.sdb.util;

import java.util.HashMap;

import javax.xml.namespace.QName;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import org.apache.log4j.Logger;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/*******************************************************************************
 * xml processing utility class changes: Original implementation used static
 * method. This revision uses a concrete object and compiles queries, for
 * further use. This improves the speed of the process
 * 
 * 
 */
public class XMLBrowser {
    
    private static final Logger logger = Logger.getLogger(XMLBrowser.class);
	protected XPath xpath = null;

	protected HashMap<String, XPathExpression> expressions;

	public XMLBrowser() {
		xpath = XPathFactory.newInstance().newXPath();
		expressions = new HashMap<String, XPathExpression>();
	}

	/**
	 * This method returns the object retrieved using specified xpath
	 * expression on a node. Use 'instanceof' operator to determine if it is a Node,
	 * NodeList or a String
	 * 
	 * @param xpathString
	 * @param node
	 * @return
	 * @throws XPathExpressionException
	 */
	public Object findXPath(String xpathString, Node node, QName type) {
		Object obj = null;
		try {

			if (!expressions.containsKey(xpathString)) {
				expressions.put(xpathString, xpath.compile(xpathString));
			}

			obj = expressions.get(xpathString).evaluate(node, type);

		} catch (XPathExpressionException e) {
		    logger.debug("xpath expression incorrect: " + xpathString);
			return null;
		}
		return obj;
	}

	/**
	 * This method returns the node list as retrieved using specified xpath
	 * expression on a node
	 * 
	 * @param xpathString
	 * @param node
	 * @return
	 * @throws XPathExpressionException
	 */
	public NodeList findXPathList(String xpathString, Node node) {
		return (NodeList) findXPath(xpathString, node, XPathConstants.NODESET);
	}

	public Node findXPathNode(String xpathString, Node node) {
		return (Node) findXPath(xpathString, node, XPathConstants.NODE);
	}

	/**
	 * Returns a text value of a node or an empty string if node was not found
	 * 
	 * @param xpathString
	 * @param node
	 * @return
	 */
	public String findXPathValue(String xpathString, Node node) {
		return (String) findXPath(xpathString, node, XPathConstants.STRING);
	}

}