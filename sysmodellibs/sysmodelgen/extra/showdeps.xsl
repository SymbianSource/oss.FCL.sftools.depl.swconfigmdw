<?xml version="1.0"?>
<xsl:stylesheet  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:s="http://www.w3.org/2000/svg">
	<xsl:import href="dependencies.xsl"/>	
	<xsl:output method="xml"/>

 <xsl:template match="s:g" mode="overlay"> 
	<xsl:variable name="id" select="@id"/>
	<xsl:variable name="found">
		<xsl:apply-templates select="document($Data,/)/*" mode="is-present">
			<xsl:with-param name="id" select="$id"/>
		</xsl:apply-templates>
	</xsl:variable> <!--  no overlay if no data file -->
	<xsl:if test="$Data!='' and $found!=''">
		<xsl:apply-templates select="." mode="my-overlay">
			<xsl:with-param name="id" select="$id"/>
		</xsl:apply-templates>
	</xsl:if>
 </xsl:template>

 <xsl:template match="/" mode="my-legend"/>
 <xsl:template match="*" mode="legend-ext-width">0</xsl:template>

  <xsl:template match="s:g[(@class='component' or @class='layer-detail' or @class='package' or @class='collection')]">
  	<xsl:copy>
  	 	<xsl:copy-of select="@*"/>
			<xsl:apply-templates select="node()"/>
 	</xsl:copy>
</xsl:template>

</xsl:stylesheet>