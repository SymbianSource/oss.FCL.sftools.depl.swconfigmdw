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

package LogItem;

use FindBin;
use lib $FindBin::Bin;
use DepConstants;

#-------------------------------------------------------------------------------------------------
# Subroutine:   new
# Purpose:      Constructor
# Input:        None (extracted from command line args)
# Output:       A reference to itself
#-------------------------------------------------------------------------------------------------
sub new()
	{
	my $package = shift;
	my $self = {};         			# Create reference to object
	bless $self,  $package;    		# Associate a reference with class name
	my %parameters = @_;
	$self->{iMessage} 	= $parameters{'msg'} ? $parameters{'msg'} : "";
	$self->{iCode} 		= $parameters{'code'} ? $parameters{'code'} : 0;
	$self->{iModule} 	= $parameters{'module'} ? $parameters{'module'} : 0;
	$self->{iSeverity} 	= $parameters{'severity'} ? $parameters{'severity'} : 3; # default is INFO
	$self->{iDepth}		= $parameters{'depth'} ? $parameters{'depth'} : 0;
	
	$self->{iCode} = &DepConstants::ModuleErrorCodes($self->{iModule}, $self->{iSeverity}) if $self->{iCode} == 0;
	
	$self->{iDate} 		= scalar(localtime);
    return $self;
	}

sub Message()
	{
	my $self = shift;
	$self->{iMessage} = $_[0] if $_[0];
	return $self->{iMessage};
	}

sub Module()
	{
	my $self = shift;
	$self->{iModule} = $_[0] if $_[0];
	return $self->{iModule};
	}

sub Severity()
	{
	my $self = shift;
	$self->{iSeverity} = $_[0] if $_[0];
	return $self->{iSeverity};
	}

sub Depth()
	{
	my $self = shift;
	$self->{iDepth} = $_[0] if $_[0];
	return $self->{iDepth};
	}

sub Date()
	{
	my $self = shift;
	$self->{iDate} = $_[0] if $_[0];
	return $self->{iDate};
	}

sub Code()
	{
	my $self = shift;
	$self->{iCode} = $_[0] if $_[0];
	return $self->{iCode};
	}

sub LogText()
	{
	my $self = shift;
	return $self->SeverityText()."(".$self->{iCode}.") [".$self->{iDate}."]: "." " x $self->{iDepth}.$self->{iMessage}."\n";
	}

sub SeverityText()
	{
	my $self = shift;
	return "  ERROR" if $self->Severity() == DepConstants::ERROR;
	return "WARNING" if $self->Severity() == DepConstants::WARNING;
	return "   INFO";
	}

1;
