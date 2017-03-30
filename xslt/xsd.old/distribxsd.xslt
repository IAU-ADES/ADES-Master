<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:xsd="http://www.w3.org/2001/XMLSchema">

<xsl:output method="xml" indent="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">

  <xsl:element name="xsd:schema">

    <xsl:for-each select="/ades/XSDTypes/*" >
    <xsl:choose>
    <xsl:when test="name(.)='simpletype'">                           <!-- simpletype with restrictions -->
    <xsl:element name="xsd:simpleType">
        <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
        <xsl:apply-templates select="union"/>
        <xsl:apply-templates select="restriction"/>
    </xsl:element>
    </xsl:when>
    <xsl:when test="name(.)='complextype'">                    <!-- complex type may be all or sequence -->
    <xsl:element name="xsd:complexType">
         <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
         <xsl:apply-templates select="all|sequence|choice"/> 
    </xsl:element>
    </xsl:when>
    <xsl:when test="name(.)='grouptype'">                      <!-- group is all or choice or sequence -->
    <xsl:element name="xsd:group">
         <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
         <xsl:apply-templates select="choice|sequence|all"/> 
    </xsl:element>
    </xsl:when>
    </xsl:choose>
    </xsl:for-each> <!-- end of XSDTypes -->
  
    <!-- now process the elements -->
    <xsl:apply-templates select="/ades/XSDElementTypes/element"/>


  </xsl:element> 

</xsl:template>


<!-- process restriction elements and their sub-element restrict-->
<xsl:template match="restrict">
  <xsl:element name="{@name}">
    <xsl:attribute name="value"><xsl:value-of select="@value"/></xsl:attribute>
  </xsl:element>
</xsl:template>

<xsl:template match="restriction">
    <xsl:element name="xsd:restriction">
       <xsl:attribute name="base"><xsl:value-of select="@base"/></xsl:attribute>
       <xsl:apply-templates select="restrict"/>
    </xsl:element>
</xsl:template>

<xsl:template match="union">
    <xsl:element name="xsd:union">
       <xsl:attribute name="memberTypes"><xsl:value-of select="@memberTypes"/></xsl:attribute>
    </xsl:element>
</xsl:template>


<!-- process element or group elements into element or group declarations
     Pay attention to whether this is using "ref" or "name, type" since 
     it is allowed to mix them.  

     call templates first since many things are common
 -->

<!-- 
     Named template to process 'use' attribute, which may not present.

     Note the 'distribOnly*' values may be deselected
     already in the match of the caller if no element is to be written
  
     'NoSubmitDistribRequired' is missing in submit, required in distrib, and 
     optional in general.
     'NoSubmit' is missing in submit, required in distrib, and 
     optional in general.
 -->
<xsl:template name="processUse">
  <xsl:choose> <!-- add attributes for @use -->
     <xsl:when test="@use='NoSubmitDistribRequired'">
     </xsl:when>
     <xsl:when test="@use='NoSubmit'">
        <xsl:attribute name="minOccurs">0</xsl:attribute>
     </xsl:when>
     <xsl:when test="@use='optional'">
        <xsl:attribute name="minOccurs">0</xsl:attribute>
     </xsl:when>
     <xsl:when test="@use='unbounded'">
        <xsl:attribute name="maxOccurs">unbounded</xsl:attribute>
     </xsl:when>
  </xsl:choose>
</xsl:template>

<!-- for submission validation, omit distribOnly fields -->

<!-- <xsl:template match="element[@ref]|group[@ref]"> -->
<xsl:template match="*[self::element or self::group][@ref]">
  <xsl:element name="xsd:{local-name()}">
     <xsl:attribute name="ref"><xsl:value-of select="@ref"/></xsl:attribute>
     <xsl:call-template name="processUse"/>
  </xsl:element> 
</xsl:template>

<!-- <xsl:template match="element[@name]|group[@name]"> --> <!-- must have type too -->
<xsl:template match="*[self::element or self::group][@name][@type][not(@use='NoSubmitDistribRequired')][not(@use='NoSubmit')]"> <!-- must have both name and type -->
  <xsl:element name="xsd:{local-name()}">
     <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
     <xsl:attribute name="type"><xsl:value-of select="@type"/></xsl:attribute>
     <xsl:call-template name="processUse"/>
  </xsl:element> 
</xsl:template>

<!-- template for sequence and all elements, which only differ
     by the xsd element name. use='unbounded' is the only special case here -->
<xsl:template match="sequence|all|choice">
  <xsl:element name="xsd:{local-name()}">
    <xsl:if test="@use='unbounded'">
      <xsl:attribute name="maxOccurs">unbounded</xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="*"/>
  </xsl:element>
</xsl:template>


</xsl:stylesheet>

