<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" omit-xml-delclaration="yes"/>
<xsl:template match="/">
\documentclass[12pt]{article}
\usepackage{longtable, tabularx, ltxtable, siunitx}
\newcolumntype{Y}{ >{\raggedright\arraybackslash}X }
\begin{document}

<xsl:apply-templates select="/ades/ADESPaper/*" />

\end{document}

</xsl:template>


<xsl:template match="ADESPaper/*[@name]">
\<xsl:value-of select='local-name()'/>{<xsl:value-of select='@name'/>}
<xsl:value-of select='text'/>
</xsl:template>

<xsl:template match="ADESPaper/*[not(@name)]">
\<xsl:value-of select='local-name()'/>{}
<xsl:value-of select='text'/>
</xsl:template>




</xsl:stylesheet>

