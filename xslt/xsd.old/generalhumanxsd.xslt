<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">&lt;?xml version="1.0"?&gt;
&lt;xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"&gt;

&lt;!-- Here are the type definitions translated from the master xml
      
    The master xml file has a restricted vocabulary.  You can help 
    by expanding it :->

    xsd:simpleType is a restriction generally via enum or regex or length 

    xsd:complexType comes for complexlisttype in the master XML, and is
       either a xsd:sequence or xsd:all list of elements or groups. 

       It currently uses "name" and "type" instead of "ref" to other elements
--&gt;

<xsl:for-each select="/ades/XSDTypes/*" >
<xsl:choose>
<xsl:when test="name(.)='simpletype'">                           <!-- simpletype with restrictions -->
&lt;xsd:simpleType name="<xsl:value-of select='@name'/>"&gt;
    <xsl:apply-templates select="doc"/> 
    <xsl:apply-templates select="union"/>
    <xsl:apply-templates select="restriction"/>
&lt;/xsd:simpleType&gt;
</xsl:when>
<xsl:when test="name(.)='complextype'">                    <!-- complex type may be all or sequence -->
&lt;xsd:complexType name="<xsl:value-of select='@name'/>"&gt;
     <xsl:apply-templates select="doc"/> 
     <xsl:apply-templates select="all|sequence|choice"/> 
&lt;/xsd:complexType&gt;
</xsl:when>
<xsl:when test="name(.)='grouptype'">                      <!-- group is all or choice or sequence -->
&lt;xsd:group name="<xsl:value-of select='@name'/>"&gt;
     <xsl:apply-templates select="doc"/> 
     <xsl:apply-templates select="choice|sequence|all"/> 
&lt;/xsd:group&gt;
</xsl:when>
</xsl:choose>
</xsl:for-each>




&lt;!-- Here are the elements, which all are defined with names
      
     All elements are of the form
     &lt;xsd:element name="&lt;name&gt;" type="&lt;type&gt;"/&gt;
     and so have a simple transformation from the master xml
--&gt;

<xsl:for-each select="/ades/XSDElementTypes" > 

&lt;!-- <xsl:value-of select="doc"/> --&gt;
<xsl:apply-templates select="element"/> </xsl:for-each>


&lt;/xsd:schema&gt;

</xsl:template>

<!-- process doc elements into annotation -->

<xsl:template match="doc">
    &lt;xsd:annotation&gt;
      &lt;xsd:documentation&gt; 
        <xsl:value-of select="node()"/> 
      &lt;/xsd:documentation&gt;
    &lt;/xsd:annotation&gt;
</xsl:template>

<!-- process restriction elements and their sub-element restrict-->
<xsl:template match="restrict"> 
      &lt;<xsl:value-of select='@name'/> value="<xsl:value-of select='@value'/>"/&gt; </xsl:template>

<xsl:template match="restriction"> 
    &lt;xsd:restriction base="<xsl:value-of select='@base'/>"&gt;
       <xsl:apply-templates select="restrict"/>
    &lt;/xsd:restriction&gt; 
</xsl:template>

<xsl:template match="union"> 
    &lt;xsd:union memberTypes="<xsl:value-of select='@memberTypes'/>"/&gt;
</xsl:template>

<!-- process element or group elements into element or group declarations
     Pay attention to whether this is using "ref" or "name, type" since 
     it is allowed to mix them.  
 -->
<!-- 
     Named template to process 'use' attribute, which may not present.

     Note the 'distribOnly*' values may be deselected
     already in the match of the caller if no element is to be written
  
     'NoSubmitDistribRequired' is missing in submit, required in distrib, and 
     optional in general.
     'NoSubmit' is missing in submit, optional in distrib, and 
     optional in general.
 -->
<xsl:template name="processUse"> <xsl:param name="var"/>
<xsl:choose> <!-- add attributes for use -->
<xsl:when test="@use='optional' or @use='NoSubmitDistribRequired' or @use='NoSubmit'">  
          &lt;xsd:<xsl:value-of select="$var"/> minOccurs="0"/&gt;</xsl:when>
<xsl:when test="not(@use)">  
          &lt;xsd:<xsl:value-of select="$var"/>/&gt;</xsl:when>
<xsl:when test="@use='unbounded'">  
          &lt;xsd:<xsl:value-of select="$var"/> maxOccurs="unbounded"/&gt;</xsl:when>
</xsl:choose> 
</xsl:template>


<xsl:template match="element[@ref]|group[@ref]">
<xsl:variable name="var" select="concat(local-name(),' ref=&quot;', @ref, '&quot;')"/> 
<xsl:call-template name='processUse'> 
   <xsl:with-param name='var' select="$var"/>
</xsl:call-template>
<xsl:if test="@doc"> &lt;!-- <xsl:value-of select="@doc"/> --&gt; </xsl:if>
</xsl:template>

<xsl:template match="element[@name]|group[@name]"> <!-- must have type too -->
<xsl:variable name="var" select="concat(local-name(),' name=&quot;', @name, '&quot; type=&quot;', @type, '&quot;')"/>
<xsl:call-template name='processUse'> 
   <xsl:with-param name='var' select="$var"/>
</xsl:call-template>
<xsl:if test="@doc"> &lt;!-- <xsl:value-of select="@doc"/> --&gt; </xsl:if>
</xsl:template>

<!-- template for sequence and all elements, which only differ
     by the xsd element name. use='unbounded' is the only special case here -->
<xsl:template match="sequence|all|choice">
<xsl:choose>
<xsl:when test="@use='unbounded'">
  &lt;xsd:<xsl:value-of select='local-name()'/> maxOccurs="unbounded"&gt;</xsl:when>
<xsl:otherwise>
  &lt;xsd:<xsl:value-of select='local-name()'/>&gt;</xsl:otherwise>
</xsl:choose> <xsl:apply-templates select='*'/> 
  &lt;/xsd:<xsl:value-of select='local-name()'/>&gt;</xsl:template>


</xsl:stylesheet>

