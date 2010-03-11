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

import java.util.Iterator;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

public class NodeWrapper implements Iterable<Node>{

	private NodeList fNodeList;
	
	public NodeWrapper(NodeList aNodeList){
		fNodeList = aNodeList;
	}
	
	public Iterator<Node> iterator() {
		return new NodeListIterator(fNodeList);
	}
	
	public int getSize() {
	    return fNodeList.getLength();
	}
	
	private class NodeListIterator implements Iterator<Node>{
	    
		NodeList fList;
		int fInternalCount=0;
		
		public NodeListIterator(NodeList aNodeList){
			fList = aNodeList;
		}

		public boolean hasNext() {
			
			return fList.getLength()>fInternalCount;
		}

		public Node next() {
			return fList.item(fInternalCount++);
		}

		public void remove() {
			throw new UnsupportedOperationException("Cannot remove from a NodeList");
		}
		
	}
	
}
