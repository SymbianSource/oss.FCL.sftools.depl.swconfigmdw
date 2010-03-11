SdbTest
=======

  SdbTest works in cooperation with Java part of the framework (see Emulator class).

  Emulator launches SdbTest executable and can retrieve test result. SdbTest stores result code in: 
  
  epoc32/winscw/c/SdbTestOut.txt.

  Each native test is named. Particular test to be run when SdbTest is specified by including test 
  name as the first parameter on the command line.


Java example 
============

  From the Java side it is enough to write:

  // Discovering available emulators 

  // Emulator configs are read from XML file specified by "com.symbian.sdb.emulator.def" system property
  // See below for example file
  Emulator[] emulators = Emulator.availableEmulators()


  // Running the test and checking the result
  
  emulators[0].setOutFile("SdbTestOut.txt");
  String [] cmds = {"ExampleTest"}; 
  try{
	int result = emulators[0].runNativeTestAndWait("SdbTest.exe", cmds, SymbianStartupMode.TEXT_ONLY);
	System.out.println("OK : " + Integer.toHexString(result));
  } catch(Exception e){
	e.printStackTrace();
  }



Adding a native verification test
=================================

  1. Modify RegisterTestsL in src/Tests.cpp to register your test function
  2. Implement your test function by either:
     a) Adding your test function to src/Tests.cpp
     b) Implementing test function in a separate file and adding the new file to group/SdbTest.mmp.

  An example test named ExampleTest is included in the src/Tests.cpp.


Example Emulator definition XML file
====================================

<emulators>
  <emulator>
    <driveLetter>N</driveLetter>
    <epocroot>/9.3/</epocroot>
    <platform>WINSCW</platform>
    <variant>UDEB</variant>
    <version>SOS_9_3</version>
  </emulator>
  <emulator>
    <driveLetter>N</driveLetter>
    <epocroot>/9.4/</epocroot>
    <platform>WINSCW</platform>
    <variant>UDEB</variant>
    <version>SOS_9_4</version>
  </emulator>
  <emulator>
    <driveLetter>N</driveLetter>
    <epocroot>/9.5/</epocroot>
    <platform>WINSCW</platform>
    <variant>UDEB</variant>
    <version>SOS_9_5</version>
  </emulator>
</emulators>