<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>

<!-- must not have newline at start of file -->

<xsl:template match="/">
\begin{longtable}
       {|>{\setlength\hsize{0.35\hsize}}Y%
        |>{\setlength\hsize{0.65\hsize}}Y|}
\multicolumn{2}{c}{\Large (continued)}\\
\multicolumn{1}{c}{Type} &amp; \multicolumn{1}{c}{Description}\\
\endhead
\multicolumn{2}{c}{\Large Simple Types with their Restrictions}\\
\multicolumn{1}{c}{Type} &amp; \multicolumn{1}{c}{Description}\\
\endfirsthead
\multicolumn{2}{l}{to be cont'd on next page}
\endfoot
\endlastfoot
\hline

<xsl:for-each select="/ades/XSDTypes/simpletype[not(url)]" >
\textbf{<xsl:value-of select='@name'/>} <xsl:apply-templates select="restriction|union|submitunion"/> &amp; <xsl:value-of select='doc'/> \\ 
\hline
</xsl:for-each>

<xsl:for-each select="/ades/XSDTypes/simpletype[url]" >
\textbf{<xsl:value-of select='@name'/>} <xsl:apply-templates select="restriction|union"/> &amp; <xsl:value-of select='doc'/> at <xsl:value-of select='url'/> \\ 
\hline
</xsl:for-each>

\end{longtable}

</xsl:template>


<!-- process restriction tags  and their sub-tag restrict-->
<xsl:template match="restrict">
      \newline --<xsl:value-of select='substring-after(@name,"xsd:")'/>: {\scriptsize\verb"<xsl:value-of select='@value'/>"} </xsl:template>


<xsl:template match="restriction">
    \footnotesize \newline base is <xsl:value-of select='@base'/>
       <xsl:apply-templates select="restrict"/>
</xsl:template>

<xsl:template match="union">
    \footnotesize \newline union of \newline <xsl:value-of select='@memberTypes'/>
       <xsl:apply-templates select="restrict"/>
</xsl:template>

<xsl:template match="submitunion">
    \footnotesize \newline ---------------------------------- \newline Submissions Only Allow: \newline ---------------------------------- \newline union of \newline <xsl:value-of select='@memberTypes'/>
       <xsl:apply-templates select="restrict"/>
</xsl:template>


</xsl:stylesheet>

