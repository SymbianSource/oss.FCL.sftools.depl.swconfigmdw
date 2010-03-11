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

package com.symbian.sdb.contacts.model.common;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.symbian.sdb.contacts.sqlite.GenericUtils;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.store.NativeByteArrayInputStream;
import com.symbian.store.NativeByteArrayOutputStream;

public class PreferencesSortOrder {
	public static enum SortOrderType {
		EAsc, EDesc;
		
		
	}

	public static class SortOrderEntry {
		SortOrderType sortOrderType;
		int uid;
		public SortOrderEntry( int uid, SortOrderType sortOrderType){
			this.sortOrderType = sortOrderType;
			this.uid = uid;
		}
		public SortOrderType getSortOrderType() {
			return sortOrderType;
		}
		public void setSortOrderType(SortOrderType sortOrderType) {
			this.sortOrderType = sortOrderType;
		}
		public int getUid() {
			return uid;
		}
		public void setUid(int uid) {
			this.uid = uid;
		}
	}
	
	public static List<SortOrderEntry> createSortOrderEntries(byte[] sortOrderBlob) throws SDBExecutionException {
		if ( sortOrderBlob == null ) {
			return new ArrayList<SortOrderEntry>();
		}
		List<SortOrderEntry> sortOrderEntries = new ArrayList<SortOrderEntry>();
		
		NativeByteArrayInputStream in = null;
		try {
			in = new NativeByteArrayInputStream(sortOrderBlob);
		
			int count = in.readInt32();
			for (int i = 0; i < count; i++) {
				int uid = in.readInt32();
				int ord = in.readInt32();
				SortOrderType sot = (ord==0)?SortOrderType.EAsc:SortOrderType.EDesc;
				SortOrderEntry ent = new SortOrderEntry(uid, sot);
				sortOrderEntries.add(ent);
			}
		} catch (IOException e) {
			// Could be a runtime exception
			throw new SDBExecutionException("Problem creating sort order entries", e);
		} finally {
			GenericUtils.closeQuietly(in);
		}
		
		return sortOrderEntries;
	}

	public static byte[] createSortOrderBlob(List<SortOrderEntry> sortOrderEntries) throws SDBExecutionException {
		byte[] result;
		
		NativeByteArrayOutputStream out = null;
		
		try{
			out = new NativeByteArrayOutputStream();
		
			int count = sortOrderEntries.size();
			out.writeInt32(count);
			for (SortOrderEntry ent : sortOrderEntries) {
				out.writeInt32(ent.getUid());
				out.writeInt32(ent.getSortOrderType().ordinal());
			}
			result = out.toByteArray();
		} catch (IOException e) {
			// Could be a runtime exception
			throw new SDBExecutionException("Problem writing sort order blob", e);
		} finally {
			GenericUtils.closeQuietly(out);
		}
		return result;
	}
	
	
}
