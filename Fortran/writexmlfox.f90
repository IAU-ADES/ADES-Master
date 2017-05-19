subroutine addDataElement(myDoc, parent, tag, val)
   !
   ! adds element tag to parent with text val
   ! This returns nothing since all data elements
   ! are terminals in ades
   !
   ! However, it needs the document to make a new
   ! element and sets the namespace to "" since FoX
   ! requires all documents to have namespaces
   !
  
   use FoX_dom
   implicit none

   type(Node), pointer :: myDoc, parent, temp
   character(len=*) :: tag
   character(len=*) :: val

   temp => createElementNS(myDoc, "", tag)
   call setTextContent(temp, val)
   temp => appendChild(parent, temp)

end subroutine addDataElement

function addElement(myDoc, parent, tag) result (el)
   !
   ! adds element tag to parent and returns the
   ! added element
   !
   ! However, it needs the document to make a new
   ! element and sets the namespace to "" since FoX
   ! requires all documents to have namespaces
   !
   use FoX_dom
   implicit none

   type(Node), pointer :: myDoc, parent, el
   character(len=*) :: tag

   type(Node), pointer :: temp

   el => createElementNS(myDoc, "", tag)
   temp => appendChild(parent, el)

end function addElement

program writexmlfox
   ! Example of how to use the FoX dom module to create a document tree in memory (and write it
   ! to a file)

   use FoX_dom
   implicit none

   interface

      subroutine addDataElement(myDoc, parent, tag, val)
         use FoX_dom
         type(Node), pointer :: myDoc, parent
         character(len=*) :: tag
         character(len=*) :: val
      end subroutine addDataElement

      function addElement(mydoc, parent, tag) result (el)
         use FoX_dom
         type(Node), pointer :: myDoc, parent, el
         character(len=*) :: tag
      end function addElement

   end interface

   type(Node), pointer :: myDoc, root, np
   type(Node), pointer :: obsBlock
   type(Node), pointer :: obsContext, subContext
   type(Node), pointer :: obsData, optical

   ! Create a new document and get a pointer to the root element, this gives you the minimum empty dom
   myDoc => createDocument(getImplementation(), "", "ades", null())
   root => getDocumentElement(myDoc)

   ! You can now do DOMish things like create new elements and append them to the document root element 
   ! dummy ends up pointing at the child-element
   obsBlock => addElement(myDoc, root, "obsBlock")
   obsContext => addElement(myDoc, obsBlock, "obsContext")

   subContext => addElement(myDoc, obsContext, "observatory")
   call addDataElement(myDoc, subContext, "mpcCode", "F51")
   call addDataElement(myDoc, subContext, "name", "Pan-STARRS 1")

   subContext => addElement(myDoc, obsContext, "submitter")
   call addDataElement(myDoc, subContext, "name", "P. Villa")
   !call addDataElement(myDoc, submitter, "institution", "Ejército Constitutionalista")
   !
   ! FoX can't handle utf-8 encodings
   !
   call addDataElement(myDoc, subContext, "institution", "Ejercito Constitutionalista")
   !
 
   subContext => addElement(myDoc, obsContext, "observers")
   call addDataElement(myDoc, subContext, "name", "P. Villa")
   call addDataElement(myDoc, subContext, "name", "F. Madera")
   
   subContext => addElement(myDoc, obsContext, "telescope")
   call addDataElement(myDoc, subContext, "aperture", "1.5")
   call addDataElement(myDoc, subContext, "design", "Reflector")
   call addDataElement(myDoc, subContext, "detector", "CCD")

   call addDataElement(myDoc, obsContext, "fundingSource", "Your favorite funding agency")

   subContext => addElement(myDoc, obsContext, "comment")
   call addDataElement(myDoc, subContext, "line", "A comment line with >stuff< in it")
   call addDataElement(myDoc, subContext, "line", "Another comment line")



   obsData => addElement(myDoc, obsBlock, "obsData")

   optical => addElement(myDoc, obsData, "optical")
   call addDataElement(myDoc, optical, "permID", "1234456")
   call addDataElement(myDoc, optical, "trkSub", "aa")
   call addDataElement(myDoc, optical, "mode", "CCD")
   call addDataElement(myDoc, optical, "stn", "F51")
   call addDataElement(myDoc, optical, "obsTime", "2016-08-29T12:32:34Z")
   call addDataElement(myDoc, optical, "ra", "10.21")
   call addDataElement(myDoc, optical, "dec", "21.21")
   call addDataElement(myDoc, optical, "astCat", "2MA")
   call addDataElement(myDoc, optical, "mag", "15.3")
   call addDataElement(myDoc, optical, "band", "w")
   call addDataElement(myDoc, optical, "notes", "klmn")
   call addDataElement(myDoc, optical, "remarks", 'A free-form "remark" <with stuff>')


   optical => addElement(myDoc, obsData, "optical")
   call addDataElement(myDoc, optical, "permID", "1334456")
   call addDataElement(myDoc, optical, "trkSub", "aa")
   call addDataElement(myDoc, optical, "mode", "CCD")
   call addDataElement(myDoc, optical, "stn", "F51")
   call addDataElement(myDoc, optical, "obsTime", "2016-08-29T12:32:34Z")
   call addDataElement(myDoc, optical, "ra", "10.21")
   call addDataElement(myDoc, optical, "dec", "21.21")
   call addDataElement(myDoc, optical, "astCat", "2MA")
   call addDataElement(myDoc, optical, "mag", "15.3")
   call addDataElement(myDoc, optical, "band", "w")
   call addDataElement(myDoc, optical, "notes", "klmn")
   call addDataElement(myDoc, optical, "remarks", "Another One")


   
   ! FoX does not like pretty-print but does this
    call setParameter(getDomConfig(myDoc), "invalid-pretty-print", .true.)

   ! Call serialize to produce the document.  Can't set encoding, which is ASCII
   ! but not written as ASCII.
   call serialize(myDoc, "written.xml")

   ! And don't forget to clean up the memory
   call destroy(myDoc)

end program writexmlfox
