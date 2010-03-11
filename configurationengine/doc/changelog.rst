ChangeLog 09-Feb-2009
=====================

Revision: 481
-------------
Author: teerytko
Date: 13:01:30, 09 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
-Updated api version 0.5.0

Modified : /branches/singleconfiguration/source/cone/__init__.py


Revision: 480
-------------
Author: teerytko
Date: 13:01:03, 09 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Updated documentation. 
 -Version
 -Fixed the error in install instructions.

Modified : /branches/singleconfiguration/doc/conf.py
Modified : /branches/singleconfiguration/doc/design/cone.mdl
Modified : /branches/singleconfiguration/doc/intro.rst


Revision: 479
-------------
Author: teerytko
Date: 12:38:48, 09 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
-Added a test case to access all features via default_view.
-Fixed a minor bug in adding data to the default_view (if feature is not found)

Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration.py
Modified : /branches/singleconfiguration/source/cone/public/api.py


Revision: 478
-------------
Author: teerytko
Date: 21:36:52, 08 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
All functionality in place for the single configurationbranch. 

Modified : /branches/singleconfiguration/source/cone/confml/model.py
Modified : /branches/singleconfiguration/source/cone/confml/persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/__init__.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_model.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/core/tests/exported.zip
Modified : /branches/singleconfiguration/source/cone/core/tests/imported.zip
Added : /branches/singleconfiguration/source/cone/core/tests/project
Added : /branches/singleconfiguration/source/cone/core/tests/project/.metadata
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/confml/aknfep.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/confml/messaging.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/confml/siprfsplugin.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/content/file.txt
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_001/root.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/commsdatcreator.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/drm5.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/helix.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/implml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/mediaplayer.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/mpxmusicplayer.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/confml/xmluifw.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_002/root.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml/coreapplicationuis.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/confml/implml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/implml
Added : /branches/singleconfiguration/source/cone/core/tests/project/gadget_wk32_003/root.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/root.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/BrowserSettings.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/CarbideV_default_access_point.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/CarbideV_startup.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/DefaultAccessPoint.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/FMRadioEngine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledAACTones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledBookmarks.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledContacts.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledContent.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledImages.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledMP3Tones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledMonophonicTones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledMusic.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledObjectsToPhotos.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledPolyphonicTones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledStreamingLinksGallery.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledTrueTones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledVideos.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/PreInstalledWMATones.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/accessoryserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/accesspoints.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/activeidle.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/activeidle2.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/aknfep.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/aknskins.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/application_management.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/audioequalizerutility.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/autolock.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/avkon.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/bluetoothgpspsy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/browserui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/bteng.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/calendarUI.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/callui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/camcorder.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/cbsserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/cenrep_iby_configuration.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/clockapp.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/commonengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/commonui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/connectiondialogs.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/contextframework.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/coreapplicationuis.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/ctsy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/dcl.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/defaultproxy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/devman.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/dlmgr.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/drm5.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/drmrightsmanager.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/drmsettings.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/enhancedmediaclient.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/environmentalreverbutility.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/featuremanager.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/flashlite_2_0.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/fmpresetutility.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/fotaadapter.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/fotadiskstorage.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/fotaserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/gennif.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/helix.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/httpcachemanager.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/httpfilterHttpFilterPipeliningConfig.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/httpfilteracceptheader.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/hwresourceclientfmtx.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/hwresourcesandenhancements.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/ibytest.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/icts.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/imagingconfigmanager.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/imum.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/j2me.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/javainstaller.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/javaruntime.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/landmarks.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/locationsettings.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/locationsuplfw.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/lock.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/locnotprefplugin.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/locsuplsettings.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/logs.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/mediaplayer.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/messaging.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/metadatautility.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/midp.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/mmsengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/mobilemedia.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/mtp.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/multimediasharing.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/musicplayer.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/newsticker.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/npppsy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/nsmldmsync.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/nsmlemailadapter.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/nsmlhttp.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/numbergrouping.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/omasuplconfigparam.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/operator_logo.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/operatormenu.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/pdpcontextmanager2.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/phonebook2.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/pnpms.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/poc.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/pocui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/pocuiintgr.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/policy_management.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/postcard.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/presenceengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/profilesengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/psmserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/pushmtm.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/remote_storage_fw.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/remotelock.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60appshell.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60contentlistingframework.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60filemanager.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60icalui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60imageviewer.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60impscommonui_ng.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60instant_messaging_ui_ng.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60mail.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60mediagallery2.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60ncnlist.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60provisioning.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60settingsuis.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60swinstalleruis.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60telephony.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60uiacceltk.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/s60videotelephony.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sat.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/screensaver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/screensaveranimplugin.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/scutplugin.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sendui.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sensor.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sensorframework.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sensorplugin.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/simple.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/simulationpsy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/speeddial.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/srsf.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/startup.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/stereowideningutility.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/suplpsy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/suplsettings.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/syncmlnotifier.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/sysutil.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/tfxserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/theme.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/themes.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/uiklaf.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/upnpmediaserver.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/upnpstack.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/usbengines.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/variant.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/vcommand.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/videoservices.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/voicemailbox.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/voicerecorder.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/webutils.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/widgetinstaller.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/wlanengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/wvengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/wvsettings20.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/xdmengine.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/confml/xmluifw.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/applications_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/connectivity_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/hardware_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/other_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/preinstalledcontent_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/system_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/s60_3_43_wk32/doc/userinterface_48_nav.png
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/data.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/implml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/second_view.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/confml/variant_view.confml
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/content
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/doc
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/doc/.notes
Added : /branches/singleconfiguration/source/cone/core/tests/project/variant_3_23_wk32/root.confml
Modified : /branches/singleconfiguration/source/cone/core/tests/project.zip
Modified : /branches/singleconfiguration/source/cone/core/tests/tempproject/dummy2.confml
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_export.py
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_import.py
Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_base.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_configuration.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_data.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_feature.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_layer.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_options.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_utils.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_valueset.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_views.py
Modified : /branches/singleconfiguration/source/cone/public/utils.py
Modified : /branches/singleconfiguration/source/cone/storage/filestorage.py
Modified : /branches/singleconfiguration/source/cone/storage/persistentdictionary.py
Modified : /branches/singleconfiguration/source/cone/storage/stringstorage.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/data.zip
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_fileresource.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage_layer.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage_with_configurations.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipstorage_with_configurations.py
Modified : /branches/singleconfiguration/source/cone/storage/zipstorage.py


Revision: 477
-------------
Author: teerytko
Date: 15:27:20, 08 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279

Added : /branches/singleconfiguration/source/cone/storage/tests/temp
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testread.txt


Revision: 476
-------------
Author: teerytko
Date: 14:40:02, 08 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Removed temp test files that were accidentally added.

Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/confml
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/content
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/doc
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/implml
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/doc
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/implml
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/prodX/doc
Deleted : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/prodX/implml


Revision: 475
-------------
Author: teerytko
Date: 14:51:35, 06 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Removed temp test files that were accidentally added.

Deleted : /branches/singleconfiguration/source/cone/storage/tests/TestProlog.zip
Modified : /branches/singleconfiguration/source/cone/storage/tests/data.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/dummytest
Deleted : /branches/singleconfiguration/source/cone/storage/tests/foo
Deleted : /branches/singleconfiguration/source/cone/storage/tests/temp
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testdelete.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testfolder
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testnewfile.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testnonrecurse.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testoverwrite.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testrecurse.zip
Deleted : /branches/singleconfiguration/source/cone/storage/tests/testtemp.zip
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipstorage_with_configurations.py
Modified : /branches/singleconfiguration/source/cone/storage/zipstorage.py


Revision: 474
-------------
Author: teerytko
Date: 14:50:57, 06 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Removed temp test files that were accidentally added.

Deleted : /branches/singleconfiguration/source/cone/tests/dummytest
Deleted : /branches/singleconfiguration/source/cone/tests/exported.zip
Deleted : /branches/singleconfiguration/source/cone/tests/temp
Deleted : /branches/singleconfiguration/source/cone/tests/tempproject
Deleted : /branches/singleconfiguration/source/cone/tests/tempzipoutput
Deleted : /branches/singleconfiguration/source/cone/tests/testdelete.zip
Deleted : /branches/singleconfiguration/source/cone/tests/testfolder
Deleted : /branches/singleconfiguration/source/cone/tests/testnewfile.zip
Deleted : /branches/singleconfiguration/source/cone/tests/testnonrecurse.zip
Deleted : /branches/singleconfiguration/source/cone/tests/testoverwrite.zip
Deleted : /branches/singleconfiguration/source/cone/tests/testrecurse.zip
Deleted : /branches/singleconfiguration/source/cone/tests/testtemp.zip


Revision: 473
-------------
Author: teerytko
Date: 14:42:22, 06 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Major merge efforts. Problems still with ZipStorage regression.

Modified : /branches/singleconfiguration/source/cone/confml/model.py
Modified : /branches/singleconfiguration/source/cone/confml/persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/core/__init__.py
Deleted : /branches/singleconfiguration/source/cone/core/configuration.py
Deleted : /branches/singleconfiguration/source/cone/core/layer.py
Deleted : /branches/singleconfiguration/source/cone/core/model.py
Deleted : /branches/singleconfiguration/source/cone/core/project.py
Modified : /branches/singleconfiguration/source/cone/core/tests/__init__.py
Added : /branches/singleconfiguration/source/cone/core/tests/exported.zip
Added : /branches/singleconfiguration/source/cone/core/tests/imported.zip
Added : /branches/singleconfiguration/source/cone/core/tests/temp
Added : /branches/singleconfiguration/source/cone/core/tests/temp2.zip
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/.metadata
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/dummy.confml
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/dummy2.confml
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/remove.confml
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path/to
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path/to/elsewhere
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path/to/elsewhere/r.confml
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path/to/somewhere
Added : /branches/singleconfiguration/source/cone/core/tests/tempproject/test/path/to/somewhere/r.confml
Added : /branches/singleconfiguration/source/cone/core/tests/tempzipoutput
Added : /branches/singleconfiguration/source/cone/core/tests/tempzipoutput/prodX.confml
Added : /branches/singleconfiguration/source/cone/core/tests/testtemp
Added : /branches/singleconfiguration/source/cone/core/tests/testtemp/.metadata
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration.py
Deleted : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_parse.py
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_export.py
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_import.py
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_on_filestorage.py
Modified : /branches/singleconfiguration/source/cone/core/tests/unittest_configuration_project_on_zipstorage.py
Deleted : /branches/singleconfiguration/source/cone/core/tests/unittest_layer.py
Deleted : /branches/singleconfiguration/source/cone/core/tests/unittest_project.py
Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/persistence.py
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/FooStore.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/exportoutput.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/exportsource.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/importoutput.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/importsource.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/modified.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/store.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/testproject.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/testproject1.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/testproject2.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/testprojectinc2.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/testprojectinc3.pk
Deleted : /branches/singleconfiguration/source/cone/public/tests/temp/unload.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_configuration.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/storage/filestorage.py
Modified : /branches/singleconfiguration/source/cone/storage/persistentdictionary.py
Modified : /branches/singleconfiguration/source/cone/storage/stringstorage.py
Added : /branches/singleconfiguration/source/cone/storage/tests/TestProlog.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/data/confml
Added : /branches/singleconfiguration/source/cone/storage/tests/data/content
Added : /branches/singleconfiguration/source/cone/storage/tests/data/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/data/implml
Added : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/implml
Added : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/prodX/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/data/ncp11/prodX/implml
Added : /branches/singleconfiguration/source/cone/storage/tests/data/platform/s60/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/data/regional/japan/content
Added : /branches/singleconfiguration/source/cone/storage/tests/data/regional/japan/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/data/regional/japan/implml
Modified : /branches/singleconfiguration/source/cone/storage/tests/data.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/dummytest
Added : /branches/singleconfiguration/source/cone/storage/tests/foo
Added : /branches/singleconfiguration/source/cone/storage/tests/foo/faa
Added : /branches/singleconfiguration/source/cone/storage/tests/foo/faa.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/FooStore.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportoutput.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/exportsource.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/generic.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importoutput.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/importsource.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store/test1.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store/test2.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store/test3.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/store.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/subpath
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/subpath.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testfolder.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/.metadata
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/confml/component.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/confml/component1.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/content
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/content/foobar.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/foo.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/foo/implml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/product.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/confml/component1.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/content
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/content/foobar.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/content/s60.txt
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/doc
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/implml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata/s60/root.confml
Added : /branches/singleconfiguration/source/cone/storage/tests/temp/testprojectlayersdata.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testdelete.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testfolder
Added : /branches/singleconfiguration/source/cone/storage/tests/testfolder/foo
Added : /branches/singleconfiguration/source/cone/storage/tests/testfolder/foo/foosubdir
Added : /branches/singleconfiguration/source/cone/storage/tests/testfolder/subdir
Added : /branches/singleconfiguration/source/cone/storage/tests/testnewfile.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testnonrecurse.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testoverwrite.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testrecurse.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/testtemp.zip
Added : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage_with_configurations.py
Added : /branches/singleconfiguration/source/cone/storage/tests/unittest_stringstorage.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipresource.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipstorage.py
Added : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipstorage_with_configurations.py
Modified : /branches/singleconfiguration/source/cone/storage/zipstorage.py
Added : /branches/singleconfiguration/source/cone/tests/dummytest
Added : /branches/singleconfiguration/source/cone/tests/exported.zip
Added : /branches/singleconfiguration/source/cone/tests/temp
Added : /branches/singleconfiguration/source/cone/tests/temp/FooStore.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/exportoutput.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/exportsource.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/importoutput.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/importsource.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/modified.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/store.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/testproject.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/testproject1.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/testproject2.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/testprojectinc2.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/testprojectinc3.pk
Added : /branches/singleconfiguration/source/cone/tests/temp/unload.pk
Added : /branches/singleconfiguration/source/cone/tests/tempproject
Added : /branches/singleconfiguration/source/cone/tests/tempproject/dummy.confml
Added : /branches/singleconfiguration/source/cone/tests/tempproject/remove.confml
Added : /branches/singleconfiguration/source/cone/tests/tempproject/test
Added : /branches/singleconfiguration/source/cone/tests/tempproject/test/path
Added : /branches/singleconfiguration/source/cone/tests/tempproject/test/path/to
Added : /branches/singleconfiguration/source/cone/tests/tempproject/test/path/to/somewhere
Added : /branches/singleconfiguration/source/cone/tests/tempproject/test/path/to/somewhere/r.confml
Added : /branches/singleconfiguration/source/cone/tests/tempzipoutput
Added : /branches/singleconfiguration/source/cone/tests/testdelete.zip
Added : /branches/singleconfiguration/source/cone/tests/testfolder
Added : /branches/singleconfiguration/source/cone/tests/testfolder/foo
Added : /branches/singleconfiguration/source/cone/tests/testfolder/foo/foosubdir
Added : /branches/singleconfiguration/source/cone/tests/testfolder/subdir
Added : /branches/singleconfiguration/source/cone/tests/testnewfile.zip
Added : /branches/singleconfiguration/source/cone/tests/testnonrecurse.zip
Added : /branches/singleconfiguration/source/cone/tests/testoverwrite.zip
Added : /branches/singleconfiguration/source/cone/tests/testrecurse.zip
Added : /branches/singleconfiguration/source/cone/tests/testtemp.zip


Revision: 472
-------------
Author: teerytko
Date: 09:00:23, 06 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279

Fixed a very crucial bug in usage of __getattr__, which normally called __getattribute__. This caused that the __getattr__ of the callee, was newer executed. Change of direct __getatribute__ to getattr(obj, name) fixed the problem.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/persistence.py
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Added : /branches/singleconfiguration/source/cone/public/tests/temp/FooStore.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/exportoutput.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/exportsource.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/importoutput.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/importsource.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/modified.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/store.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/testproject.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/testproject1.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/testproject2.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/testprojectinc2.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/testprojectinc3.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp/unload.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_configuration.py
Deleted : /branches/singleconfiguration/source/cone/public/tests/unittest_configurationlayer.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_layer.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/public/utils.py


Revision: 470
-------------
Author: teerytko
Date: 17:20:19, 05 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
- Working persistentconfml.py and test (hierarchical loads/dumps).
- Added ConfmlMeta,ConfmlDesc.

Modified : /branches/singleconfiguration/source/cone/confml/model.py
Modified : /branches/singleconfiguration/source/cone/confml/persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/__init__.py
Added : /branches/singleconfiguration/source/cone/confml/tests/unittest_model.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_persistentconfml.py


Revision: 469
-------------
Author: teerytko
Date: 07:49:54, 05 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279

First version that supports the idea of somewhat incremental confml parsing (with warnings).

Modified : /branches/singleconfiguration/source/cone/confml/persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/public/persistence.py
Modified : /branches/singleconfiguration/source/cone/public/tests/Import.pk
Added : /branches/singleconfiguration/source/cone/public/tests/temp
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_persistence.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_public_api.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py


Revision: 468
-------------
Author: teerytko
Date: 16:42:50, 03 February, 2009
Message:
ASSIGNED - # 1279: ConE: Support for confml data reader/writer 
http://configurationtools.nmp.nokia.com/configurationtool/ticket/1279
Added first version of persistentconfml module, that can dump/load Configuration objects.

Added : /branches/singleconfiguration/source/cone/confml/persistentconfml.py
Modified : /branches/singleconfiguration/source/cone/confml/tests/unittest_implml.py
Added : /branches/singleconfiguration/source/cone/confml/tests/unittest_persistentconfml.py


Revision: 467
-------------
Author: teerytko
Date: 16:41:16, 03 February, 2009
Message:
Fixed errors after refactoring persistence modules for common module specific dumps/loads functionality.

Modified : /branches/singleconfiguration/source/cone/storage/filestorage.py
Modified : /branches/singleconfiguration/source/cone/storage/persistentdictionary.py
Modified : /branches/singleconfiguration/source/cone/storage/stringstorage.py


Revision: 466
-------------
Author: teerytko
Date: 16:41:02, 03 February, 2009
Message:
Fixed errors after refactoring persistence modules for common module specific dumps/loads functionality.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/Import.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py


Revision: 455
-------------
Author: teerytko
Date: 13:49:44, 02 February, 2009
Message:
Refactored the filestorage to support same functionality as stringstorage.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_utils.py
Modified : /branches/singleconfiguration/source/cone/public/utils.py
Modified : /branches/singleconfiguration/source/cone/storage/common.py
Modified : /branches/singleconfiguration/source/cone/storage/filestorage.py
Modified : /branches/singleconfiguration/source/cone/storage/stringstorage.py


Revision: 454
-------------
Author: teerytko
Date: 12:01:15, 02 February, 2009
Message:
-Added support for Data elements under Configuration.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/Import.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_base.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_configuration.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_container.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_data.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_feature.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py
Deleted : /branches/singleconfiguration/source/cone/public/tests/unittest_resource.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/storage/__init__.py
Modified : /branches/singleconfiguration/source/cone/storage/persistentdictionary.py
Modified : /branches/singleconfiguration/source/cone/storage/stringstorage.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/__init__.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_metadata.py
Added : /branches/singleconfiguration/source/cone/storage/tests/unittest_resource.py(Copy from path: /branches/singleconfiguration/source/cone/public/tests/unittest_resource.py, Revision, 448


Revision: 453
-------------
Author: teerytko
Date: 10:10:37, 30 January, 2009
Message:
-Added support for folders.
-Added support for Storage agnostic open

Modified : /branches/singleconfiguration/source/cone/public/api.py
Deleted : /branches/singleconfiguration/source/cone/public/persistentdictionary.py
Deleted : /branches/singleconfiguration/source/cone/public/stringstorage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Added : /branches/singleconfiguration/source/cone/storage/common.py
Modified : /branches/singleconfiguration/source/cone/storage/filestorage.py
Replacing : /branches/singleconfiguration/source/cone/storage/metadata.py
Added : /branches/singleconfiguration/source/cone/storage/persistentdictionary.py(Copy from path: /branches/singleconfiguration/source/cone/public/persistentdictionary.py, Revision, 448
Added : /branches/singleconfiguration/source/cone/storage/stringstorage.py(Copy from path: /branches/singleconfiguration/source/cone/public/stringstorage.py, Revision, 449
Modified : /branches/singleconfiguration/source/cone/storage/tests/__init__.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/data/.metadata
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage.py
Added : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage_layer.py
Replacing : /branches/singleconfiguration/source/cone/storage/tests/unittest_metadata.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_zipstorage.py
Modified : /branches/singleconfiguration/source/cone/storage/zipstorage.py


Revision: 449
-------------
Author: teerytko
Date: 17:21:57, 29 January, 2009
Message:
Created a Layer object.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/persistence.py
Modified : /branches/singleconfiguration/source/cone/public/plugin.py
Modified : /branches/singleconfiguration/source/cone/public/stringstorage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/Import.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_container.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_feature.py
Added : /branches/singleconfiguration/source/cone/public/tests/unittest_layer.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_public_api.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_utils.py
Modified : /branches/singleconfiguration/source/cone/public/utils.py


Revision: 446
-------------
Author: teerytko
Date: 10:44:16, 23 January, 2009
Message:
Added install from source section

Modified : /branches/singleconfiguration/doc/intro.rst


Revision: 445
-------------
Author: teerytko
Date: 11:52:21, 22 January, 2009
Message:
Refactored the public API to a single Configuration storage.

Modified : /branches/singleconfiguration/source/cone/public/api.py
Modified : /branches/singleconfiguration/source/cone/public/container.py
Modified : /branches/singleconfiguration/source/cone/public/persistence.py
Added : /branches/singleconfiguration/source/cone/public/persistentdictionary.py
Added : /branches/singleconfiguration/source/cone/public/stringstorage.py(Copy from path: /branches/singleconfiguration/source/cone/public/tests/stringstorage.py, Revision, 425
Added : /branches/singleconfiguration/source/cone/public/tests/Import.pk
Modified : /branches/singleconfiguration/source/cone/public/tests/__init__.py
Deleted : /branches/singleconfiguration/source/cone/public/tests/stringstorage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_configuration.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_container.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_persistence.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_project.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_public_api.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_resource.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_storage.py
Modified : /branches/singleconfiguration/source/cone/public/tests/unittest_views.py
Added : /branches/singleconfiguration/source/cone/storage/configurationpersistence.py
Modified : /branches/singleconfiguration/source/cone/storage/tests/unittest_filestorage_to_filestorage.py


Revision: 429
-------------
Author: teerytko
Date: 17:04:13, 09 January, 2009
Message:
added makefile mechanism for building cone.

Added : /branches/singleconfiguration/document
Added : /branches/singleconfiguration/install
Modified : /branches/singleconfiguration/makefile
Added : /branches/singleconfiguration/source/makefile
Added : /branches/singleconfiguration/source/plugins/ConeCliPlugin/makefile
Added : /branches/singleconfiguration/source/plugins/ConeContentPlugin/makefile
Added : /branches/singleconfiguration/source/plugins/ConeCustomConfmlPlugin/makefile
Added : /branches/singleconfiguration/test

