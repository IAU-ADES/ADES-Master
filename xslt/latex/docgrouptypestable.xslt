<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">

\section{Groups}

This is the documentation for the groups.  Groups are a
convenient way of organizing rules in complicated structures,
used as components of other groups or of complex types.  Unlike
complex types, groups may appear inside other complex types or 
groups with no tag.  Because groups act a bit like types, their
names are all CamelCase with the first letter capitalized.

<xsl:apply-templates select="/ades/XSDTypes/grouptype" />



\section{Complex Types}

This is the documentation for the complex types, which may
be used directly as similarly-named elements or as components
of other complex types and groups.  Unlike a group, a complex
type is always the only thing inside a tag.  The names of
complex types, like groups and simple types, are all CamelCase
with the first letter capitalized.

<xsl:apply-templates select="/ades/XSDTypes/complextype" />


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
     'requiredAttribute' only allowed in attributes; this is not checked
 -->
<xsl:template name="processUse">
<xsl:choose> <!-- add attributes for use -->
<xsl:when test="@use='optional'"> (Optional) </xsl:when>
<xsl:when test="not(@use)"> </xsl:when>
<xsl:when test="@use='unbounded'"> (Unbounded) </xsl:when>
<xsl:when test="@use='NoSubmit'"> (NoSubmit) </xsl:when>
<xsl:when test="@use='NoSubmitDistribRequired'"> (NoSubmitDistribRequired) </xsl:when>
<xsl:when test="@use='requiredAttribute'"> (requiredAttribute) </xsl:when>
</xsl:choose> 
</xsl:template>

<xsl:template match="/ades/XSDTypes/*" >
\subsection*{<xsl:value-of select='local-name()'/>:  <xsl:value-of select='@name'/>}
\begin{tabularx}{\linewidth}{lllY}
\hline
     &amp; \textbf{<xsl:value-of select='@name'/>} &amp; &amp; \textbf{<xsl:value-of select="doc"/>} \\
     \hline
     <xsl:apply-templates select="attribute"/>  <!-- in complextype only -->
     <xsl:apply-templates select="choice|sequence|all"/> 
\hline
\\
\\
\end{tabularx}
</xsl:template>

<xsl:template match="any">
  \multicolumn{1}{c}{}&amp; <xsl:value-of select='local-name()'/> &amp; &amp;  \\ </xsl:template>

<xsl:template match="element[@ref]|group[@ref]">
  \multicolumn{1}{c}{}&amp; <xsl:value-of select='local-name()'/> &amp; <xsl:value-of select='@ref'/>  &amp; <xsl:call-template name='processUse'/> \\ </xsl:template>

<xsl:template match="element[@name]|group[@name]">
  \multicolumn{1}{c}{}&amp; type <xsl:value-of select='@type'/>  &amp; <xsl:value-of select='@name'/>   &amp; <xsl:call-template name='processUse'/> \\ </xsl:template>

<xsl:template match="attribute[@name]">
  \multicolumn{1}{c} {} &amp; \multicolumn{3}{l} {
  \begin{tabular}{|llll}
  <xsl:value-of select='local-name()'/> &amp; <xsl:value-of select='@name'/> &amp; <xsl:value-of select='@type'/> &amp; <xsl:call-template name='processUse'/>   \\
  \hline 
     <xsl:apply-templates select='*'/> 
  \hline 
  \end{tabular} } \\
  
</xsl:template>

<!-- template for sequence and all elements, which only differ
     by the xsd element name. use='unbounded' is the only special case here -->
<xsl:template match="sequence|all|choice">
  \multicolumn{1}{c} {} &amp; \multicolumn{3}{l} {
  \begin{tabular}{|llll}
  <xsl:value-of select='local-name()'/> &amp; <xsl:call-template name='processUse'/>  &amp; &amp; \\
  \hline 
     <xsl:apply-templates select='*'/> 
  \hline 
  \end{tabular} } \\
  
</xsl:template>


</xsl:stylesheet>

