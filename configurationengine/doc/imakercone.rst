iMaker-ConE integration
=======================

	iMaker tool is able to create images from CPF file. This mechanism is used for example in Carbide.v 
	where iMaker plugin (Eclipse plugin) is calling iMaker to create flash images for modified CPF file.
	The following picture shows how the calling hierarchy goes.
	
	.. image:: images/imaker_cone.jpg
	
#.	Carbide.v's iMaker plugin instantiates call to iMaker where CPF and configuration inside the CPF is given as parameter.
	Also other information like report template and report output filename is given. Imaker plugin is responsible of providing
	progress information to Carbide.v user so that he/she knows that generation is progressing.
#. 	iMaker calls ConE to generate makefile that contains image creation configuration for this CPF.
#.	ConE returns makefile to iMaker
#. 	iMaker calls itself using the makefile. Default target in the makefile is create_selected and in Carbide.v use cases it
	contains ROFS3 and UDA targets.	
#.	iMaker calls ConE to generate content for ROFS3 (parameter --impl-tag=target:rofs3) and gives output directory as parameter.	
#.	ConE filters implementations as defined by iMaker and calls each plugin separately to create output files to output folder. 	
#.	Data is generated to output folder.
#.	iMaker creates ROFS3 image from that data using normal iMaker variant build step.
#.	iMaker calls ConE to generate content for UDA (parameter --impl-tag=target:uda) and gives output directory as parameter.	
#.	ConE filters implementations as defined by iMaker and calls each plugin separately to create output files to output folder. 	
#.	Data is generated to output folder.
#.	iMaker creates UDA image from that data using normal iMaker variant build step.
#.	iMaker performs data package copy step which basically uses predefined dcp, vpl and signature files and copies flash images
	based on variant configuration to one folder with certain filenames. This way there is no need to resign the package anymore.
	Downside of this approach is that data package definition and information cannot be changed but in case of operator variant
	verification it is not that critical. Of course same data package cannot be used in production.
#.	Data package and generation reports are located in places that Carbide.v specified in the first call.

