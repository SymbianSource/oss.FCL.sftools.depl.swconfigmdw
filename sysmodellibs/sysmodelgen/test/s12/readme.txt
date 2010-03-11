The created SVG files do not matter - the important thing is the */model.xml files generated.

model95\model.xml and model95ini\model.xml  should contain:
	 <sysdef href=".../test/s12/System_Definition_Template.xml">
		<info href='.../test/s12/Symbian_OS_v9.5_Schedule12.xml' type='s12'/>
	</sysdef>


modelall\model.xml and modelallini\model.xml should contain:
	 <sysdef href=".../test/s12/System_Definition_Template.xml">
		<info href='.../test/s12/Symbian_OS_v9.4_Schedule12.xml' type='s12'/>
		<info href='.../test/s12/Symbian_OS_v9.5_Schedule12.xml' type='s12'/>
		<info href='.../test/s12/Symbian_OS_v9.6_Schedule12.xml' type='s12'/>
		<info href='.../test/s12/Symbian_OS_vFuture_Schedule12.xml' type='s12'/>
	</sysdef>
