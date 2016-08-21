<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">
\begin{longtable}
       {|l|l|Y|}
\multicolumn{3}{l}{\Large (continued)}\\
\endhead
\multicolumn{3}{c}{\Large Elements and their Descriptions}\\
\endfirsthead
\multicolumn{3}{l}{to be cont'd on next page}
\endfoot
\endlastfoot
\hline

<xsl:apply-templates select="/ades/XSDElementTypes"/>


\end{longtable}

</xsl:template>

<xsl:template match="element"> <!-- must have name, type and doc -->
\textbf{<xsl:value-of select='@name'/>} &amp; <xsl:value-of select='@type'/> &amp; <xsl:value-of select='@doc'/> \\
\hline </xsl:template>

<xsl:template match="XSDElementTypes"> 
\multicolumn{3}{|c|}{\large <xsl:value-of select="@purpose"/>}\\
\multicolumn{1}{|c}{Name}&amp; \multicolumn{1}{c}{Type} &amp; \multicolumn{1}{c|}{Description}\\
\hline
<xsl:apply-templates select="element"/> \hline </xsl:template>


</xsl:stylesheet>

