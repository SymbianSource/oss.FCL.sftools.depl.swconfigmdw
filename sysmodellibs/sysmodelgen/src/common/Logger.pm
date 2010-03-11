# Copyright (c) 2004-2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description:
#

package Logger;

use FindBin;
use lib $FindBin::Bin;

use DepConstants;
use LogItem;

# Global statics:

# This is expected to be set by the client code using $Logger::LOGFILE
# If it's not defined, the logging is done to stdout
$LOGFILE = "";

$SEVERITY = DepConstants::ERROR;

# Forward declarations:
sub Log($$$$);
sub LogFatal($$$);
sub LogError($$$);
sub LogWarning($$$);
sub LogInfo($$$);
sub LogRaw($);

#-------------------------------------------------------------------------------------------------
# Subroutine:   Log
# Purpose:      Logs to the screen
# Input:        Messsage, Module Code, Severity
# Output:       None
#-------------------------------------------------------------------------------------------------
sub Log($$$$)
	{
	my $message = $_[0];
	my $callingModule = $_[1];
	my $severity = $_[2] ? $_[2] : DepConstants::INFO;
	my $depth = $_[3] ? $_[3] : 0;
	
	# log this only if its severity level is less than or equal to the user-defined level:
	#  -w1: errors only (default)
	#  -w2: warnings as well as errors
	#  -w3: info messages, warnings and errors.
	return if $severity > $SEVERITY;
	
	my $code = &DepConstants::ModuleErrorCodes($callingModule, $severity);
	my $logItem = new LogItem(msg => $message, code => $code, severity => $severity, depth => $depth);
	&WriteToFile($logItem->LogText());
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogFatal
# Purpose:      Logs to the screen
# Input:        Message Module Code
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogFatal($$$)
	{
	my $message = $_[0];
	my $callingModule = $_[1];
	my $depth = $_[2] ? $_[2] : 0;
	my $exitCode = $_[3] ? $_[3] : DepConstants::KFailure;
	&Log("Fatal! ".$message, $callingModule, DepConstants::ERROR, $depth);
	exit $exitCode;
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogError
# Purpose:      Logs to the screen
# Input:        Message Module Code
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogError($$$)
	{
	my $message = $_[0];
	my $callingModule = $_[1];
	my $depth = $_[2] ? $_[2] : 0;
	&Log($message, $callingModule, DepConstants::ERROR, $depth);
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogWarning
# Purpose:      Logs to the screen
# Input:        Message Module Code
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogWarning($$$)
	{
	# first check the severity level:
	return if $SEVERITY < DepConstants::WARNING;
	
	my $message = $_[0];
	my $callingModule = $_[1];
	my $depth = $_[2] ? $_[2] : 0;
	&Log($message, $callingModule, DepConstants::WARNING, $depth);
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogInfo
# Purpose:      Logs to the screen
# Input:        Message Module Code
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogInfo($$$)
	{
	# first check the severity level:
	return if $SEVERITY < DepConstants::INFO;
	
	my $message = $_[0];
	my $callingModule = $_[1];
	my $depth = $_[2] ? $_[2] : 0;
	&Log($message, $callingModule, DepConstants::INFO, $depth);
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogRaw
# Purpose:      Logs a piece of raw text to the screen
# Input:        Messsage string
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogRaw($)
	{
	# only log raw text if the warning level is on info - i.e. the most verbose:
	return if $SEVERITY < DepConstants::INFO;
	&WriteToFile($_[0]);
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   LogList
# Purpose:      Logs a list of log items
# Input:        array of logs starting with ERROR, WARNING or Note
# Output:       None
#-------------------------------------------------------------------------------------------------
sub LogList
	{
	foreach $log (@_) 
		{
		$log.="\n";
		if($log=~s/^ERROR:\s*//)
			{
			&LogError($log,DepConstants::KUnknownModuleError,1);
			}
		elsif($log=~s/^WARNING:\s*//)
			{
			&LogWarning($log,DepConstants::KUnknownModuleError,1);
			}
		elsif($log=~s/^Note:\s*//)
			{
			&LogInfo($log,DepConstants::KUnknownModuleError,1);
			}
		else
			{
			&LogRaw($log);
			}
		}
	}

#-------------------------------------------------------------------------------------------------
# Subroutine:   WriteToFile
# Purpose:      
# Input:        A message string
# Output:       None
#-------------------------------------------------------------------------------------------------
sub WriteToFile()
	{
	my $message = shift;
	if ($LOGFILE ne "")
		{
		open(LOGFILE, ">> $LOGFILE") or die "Can't open the log file '$LOGFILE': $!";
		print LOGFILE $message;
		}
	else
		{
		print $message; # print to stdout
		}
	}

1;
