<stylesheet version="1.0" xmlns="http://www.w3.org/1999/XSL/Transform" 	xmlns:set="http://exslt.org/sets">
<output method="text"/>
<key name="name" match="component|collection|package|layer" use="@id"/>

<template match="/*" priority="-1">
ERROR: Invalid root element: <value-of select="name()"/>
</template>

<template match="*" priority="-5">
ERROR: Invalid element: <value-of select="name()"/>
</template>



<template match="component/Build"/> <!-- for depmodel -->

<template match="@*" priority="-5">
NOTE: unexpected attribute "<value-of select="name()"/>" on &lt;<value-of select="name(..)"/>&gt;</template>


<template match="text()">
<if test="normalize-space(.)!=''">
ERROR: unexepected text: <value-of select="."/></if>
</template>


<template match="/SystemDefinition">
<if test="not(systemModel/@name)">
Note: missing System Model name</if>
<for-each select="systemModel//*[@id]">
	<if test="count(key('name',@id)) &gt; 1">
ERROR: duplicate name for <value-of select="name()"/> "<value-of select="@id"/>" (<value-of select="count(key('name',@id))"/>)	<apply-templates mode="location" select=".."/></if>
</for-each>
<apply-templates select="@schema | node()"/>
<call-template name="extra-atts"/>
<call-template name="extra-atts"><with-param name="item">collection</with-param></call-template>
<call-template name="extra-atts"><with-param name="item">package</with-param></call-template>
<call-template name="extra-atts"><with-param name="item">layer</with-param></call-template>
<variable name="levels">
	<for-each select="set:distinct(//@level)">
	   <value-of select="concat(.,' ')"/>
   </for-each>
  </variable>
<if test="$levels!=''">
Note: Level names used: <value-of select="normalize-space($levels)"/></if>
</template>

<template name="extra-atts"><param name="item">component</param>
<variable name="atts">
	<for-each select="//*[name()=$item]/@*"><variable name="n" select="name()"/>
	<if test="not(following::*[name()=$item]/@*[name()=$n])">
	   <apply-templates mode="extra" select="."/></if>
	</for-each>
</variable>
<if test="$atts!=''">
Note: Extra <value-of select="$item"/> attributes: <value-of select="normalize-space($atts)"/></if>
</template>

<template match="@*" mode="extra">
	   <value-of select="concat(name(), ' ')"/>
</template>


<template match="collection/@level | package/@level | package/@span | layer/@span| layer/@levels | package/@levels | @name | @id | @before |component/@filter |component/@contract |component/@deprecated |component/@class |component/@introduced |component/@purpose|component/@target" mode="extra"/>


<template match="/SystemDefinition/@schema">
<choose>
	<when test="starts-with(.,'3.')"/>
<otherwise>
ERROR: unsupported syntax: <value-of select="."/></otherwise>
</choose>
</template>



<template match="@level">
WARNING: invalid attribute "<value-of select="name()"/>" on &lt;<value-of select="name(..)"/>&gt;</template>
	
<template match="systemModel/layer|layer/package|package/package| package/collection| collection/component |
	SystemDefinition/layer| SystemDefinition/package| SystemDefinition/collection| SystemDefinition/component">
	<apply-templates select="@*|node()"/>
</template>


<template match="layer|package|collection|component" priority="-3">
ERROR: &lt;<value-of select="name()"/> name="<value-of select="@id"/>"&gt; cannot be a child of &lt;<value-of select="name(..)"/>&gt;</template>



<template match="package/@level">
<if test="not(contains(concat(' ',normalize-space(../../@levels), ' '),concat(' ',normalize-space(.), ' ')))">
ERROR: Invalid level name "<value-of select="."/>" on <value-of select="name(..)"/> "<value-of select="../@id"/>" (<value-of select="../../@levels"/>)</if>
</template>

<template match="collection/@level">
<choose>
	<when test="ancestor::package/@levels">
		<if test="not(contains(concat(' ',normalize-space(ancestor::package/@levels), ' '),concat(' ',normalize-space(.), ' ')))">
ERROR: Invalid level name "<value-of select="."/>" on <value-of select="name(..)"/> "<value-of select="../@id"/>" (<value-of select="../../@levels"/>)</if>
	</when>
	<otherwise>
		<if test="not(contains(concat(' ',normalize-space(ancestor::layer/@levels), ' '),concat(' ',normalize-space(.), ' ')))">
ERROR: Invalid level name "<value-of select="."/>" on <value-of select="name(..)"/> "<value-of select="../@id"/>" (<value-of select="../../@levels"/>)</if>
	</otherwise>
</choose>
</template>



<template match="component/@plugin">
	<if test=".!='Y' and .!='N'">
WARNING: invalid <value-of select="name()"/> value "<value-of select="."/>" on &lt;<value-of select="name(..)"/> name="<value-of select="../@id"/>"&gt;</if>
</template>


<template match="logicalset|logicalsubset|module|SystemBuild">
ERROR: using 1.x syntax element: &lt;<value-of select="name()"/>&gt;</template>

<template match="unit/@name | unit/@unitID">
<if test="not(starts-with(/SystemDefinition/@schema,'1.'))">
WARNING: using 1.x syntax attribute: &lt;<value-of select="concat(name(..),' ',name())"/>="<value-of select="."/>"&gt;</if>
</template>

<template match="@name | layer/@levels |package/@levels | component/@class | component/@filter | component/@introduced  | component/@deprecated | component/@contract"> <!-- validate elsewhere -->
	<if test=".=''">
ERROR: attribute "<value-of select="name()"/>" on &lt;<value-of select="name(..)"/>&gt; must not be empty</if>
</template>

<template match="systemModel|meta">
	<apply-templates select="@*|node()"/>
</template>

<template match="meta/*"/> <!-- anything's valid-->

<template match="meta/@href | meta/@rel | meta/@type"/>

<template match="unit[starts-with(/SystemDefinition/@schema,'1.')]/@contract"/>


<template match="unit/@mrp | unit/@bldFile">
<choose>
<when test="starts-with(/SystemDefinition/@schema,'1.')">
	<if test="contains(.,'/')">
WARINING: path separator must be "\" for <value-of select="name()"/>="<value-of select="."/>"</if>
</when>
<otherwise>
	<if test="contains(.,'\')">
WARINING: path separator must be "/" for <value-of select="name()"/>="<value-of select="."/>"</if>
</otherwise>
</choose>
</template>


<template match="unit/@version | unit/@priority | unit/@filter | unit/@root"/> <!-- handle later-->
<template match="package/@* | prebuilt/@*"/> <!-- handle later-->

<template match="unit|component/package|prebuilt">
	<if test="*">
WARNING: &lt;<value-of select="name()"/>&gt; must be empty.</if>

<if test="not(starts-with(/SystemDefinition/@schema,'1.'))">
<if test="count(../unit | ../package | ../prebuilt) != 1 and count(../*[@filter or @version]) != count(../*)">
WARNING: multiple units must have "version" or "filter" attributes (<value-of select="../@id"/>)</if>
<if test="self::prebuilt or self::package">
ERROR: using 1.x syntax element: &lt;<value-of select="name()"/>&gt;</if>
</if>
<apply-templates select="@*"/>
</template>

<template mode="location" match="*">
<for-each select="ancestor::*[(self::layer or self::package or self::collection) and @name]">[<value-of select="substring(name(),1,1)"/>] <value-of select="@id"/>
	<if test="position()=1"> / </if>
</for-each>
</template>
</stylesheet>
