
/*
 * 
 * Portions Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
 * 
 * Copyright:    Copyright (c) 2000 Kent Beck and Erich Gamma
 *
 *   Permission to reproduce and create derivative works from the Software 
 *   ("Software Derivative Works") is hereby granted to you under the copyrights
 *   of Kent Beck and Erich Gamma. Kent Beck and Erich Gamma also grant you 
 *   the right to distribute the Software and Software Derivative Works.
 *
 *   Kent Beck and Erich Gamma licenses the Software to you on an "AS IS" basis,
 *   without warranty of any kind. Kent Beck and Erich Gamma HEREBY
 *   EXPRESSLY DISCLAIMS ALL WARRANTIES OR CONDITIONS, EITHER EXPRESS OR
 *   IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OR 
 *   CONDITIONS OF MERCHANTABILITY, NON INFRINGEMENT AND FITNESS FOR A 
 *   PARTICULAR PURPOSE. You are solely responsible for determining the 
 *   appropriateness of using the Software and assume all risks associated with
 *   the use and distribution of this Software, including but not limited to 
 *   the risks of program errors, damage to or loss of data, programs or 
 *   equipment, and unavailability or interruption of operations. KENT BECK AND
 *   ERICH GAMMA WILL NOT BE LIABLE FOR ANY DIRECT DAMAGES OR FOR ANY SPECIAL, 
 *   INCIDENTAL, OR INDIRECT DAMAGES OR FOR ANY ECONOMIC CONSEQUENTIAL DAMAGES 
 *   (INCLUDING LOST PROFITS OR SAVINGS), EVEN IF KENT BECK AND ERICH GAMMA HAD
 *   BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. Kent Beck and Erich Gamma 
 *   will not be liable for the loss of, or damage to, your records or data, or
 *   any damages claimed by you based on a third party claim.
 *
 *   You agree to distribute the Software and any Software Derivatives under a
 *   license agreement that: 1) is sufficient to notify all licensees of the
 *   Software and Software Derivatives that Kent Beck and Erich Gamma assumes
 *   no liability for any claim that may arise regarding the Software or
 *   Software Derivatives, and 2) that disclaims all warranties, both express
 *   and implied, from Kent Beck and Erich Gamma regarding the Software and
 *   Software Derivatives. (If you include this Agreement with any distribution
 *   of the Software and Software Derivatives you will have met this
 *   requirement). You agree that you will not delete any copyright notices in
 *   the Software.
 *
 *   This Agreement is the exclusive statement of your rights in the Software
 *   as provided by Kent Beck and Erich Gamma. Except for the licenses
 *   granted to you in the second paragraph above, no other licenses are granted
 *   hereunder, by estoppel, implication or otherwise.
 *
 * @author Kent Beck
 * @author Erich Gamma
 */

// JUnitX framework is a JUint extesion to test private and protected class and 
// orginally distributed under above license.


package com.symbian.sdb.mode.flow.ced;

import junitx.framework.TestAccessException;

public class TestProxy
extends junitx.framework.TestProxy
{
  public Object newInstance (Object[] anArgList)
  throws TestAccessException
  {
    try
    {
      return getProxiedClass ().getConstructor (anArgList).newInstance (anArgList);
    }
    catch (Exception e)
    {
      throw new TestAccessException ("could not instantiate " + getTestedClassName (), e);
    }
  }


  public Object newInstanceWithKey (String aConstructorKey, Object[] anArgList)
  throws TestAccessException
  {
    try
    {
      return getProxiedClass ().getConstructor (aConstructorKey).newInstance (anArgList);
    }
    catch (Exception e)
    {
      throw new TestAccessException ("could not instantiate " + getTestedClassName (), e);
    }
  }
}
