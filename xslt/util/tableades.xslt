<?xml version="1.0" encoding="UTF-8"?> <xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">

<xsl:apply-templates select="/ades/XSDElementTypes/element"/>
<xsl:apply-templates select="/ades/PSVObservationFields/psv"/>


</xsl:template>


<xsl:template match="/ades/PSVObservationFields/psv"> <!-- must have name, type and doc -->
psv tagtype <xsl:value-of select='@tagtype'/> name <xsl:value-of select='@name'/> width <xsl:value-of select='@width'/> just <xsl:value-of select='@justification'/> dpos <xsl:value-of select='@dpos'/>
</xsl:template>


<xsl:template name="processUse">
<xsl:choose> <!-- add attributes for use -->
<xsl:when test="@use='optional' or @use='NoSubmitDistribRequired' or @use='NoSubmit' or @use='unbounded'"> use <xsl:value-of select="@use"/></xsl:when>
<xsl:when test="not(@use)"> use required</xsl:when>
</xsl:choose>
</xsl:template>




<xsl:template match="/ades/XSDElementTypes/element[@name]"> <!-- must have name, type and doc -->
top <xsl:value-of select='@name'/>
<xsl:apply-templates select='//complextype[@name=current()/@type]'/>
close <xsl:value-of select='@name'/> 
</xsl:template>

<xsl:template match="element"> <!-- must have name, type and doc -->
    element <xsl:value-of select='@name'/> <xsl:call-template name='processUse'/>
</xsl:template>

<!-- <xsl:template match="element[@ref]"> -->
<xsl:template match="element[@ref]">
    element <xsl:value-of select="@ref"/> <xsl:call-template name='processUse'/>
</xsl:template>

<!-- <xsl:template match="group[@ref]"> -->
<xsl:template match="group[@ref]">
  open group <xsl:value-of select="@ref"/> <xsl:call-template name='processUse'/>
  <xsl:apply-templates select='//grouptype[@name=current()/@ref]'/>
  close group <xsl:value-of select="@ref"/>
</xsl:template>

<!-- template for sequence and all elements, which only differ
     by the xsd element name. use='unbounded' is the only special case here -->
<xsl:template match="sequence|all|choice">
  open <xsl:value-of select='local-name()'/> <xsl:call-template name='processUse'/>
  <xsl:apply-templates select='*'/>
  close <xsl:value-of select='local-name()'/> 
</xsl:template>

<!-- ignore doc children for this list -->
<xsl:template match="doc">
</xsl:template>

<xsl:template match="complextype">
  complex type name is <xsl:value-of select='@name'/> 
  <xsl:apply-templates select='*'/>
  end complex type <xsl:value-of select='@name'/>
</xsl:template>

<xsl:template match="grouptype">
  <xsl:apply-templates select='*'/>
</xsl:template>


</xsl:stylesheet>

