
!
! hasSubElements is .true. if p has any
! ELEMENT_NODE children and .false. if not
!
logical function hasSubElements(p)

    use FoX_dom
    implicit none

    type(Node), pointer :: p

    type(NodeList), pointer :: children
    type(Node), pointer :: cp
    integer :: i

    hasSubElements = .false.
    children => getChildNodes(p)
    do i = 0, getLength(children) - 1
       cp => item(children, i)
      if (getNodeType(cp) == ELEMENT_NODE) then
         hasSubElements=.true.
         return
      endif
    enddo

end function hasSubElements


!
! printElements walks recursively though a node,
! printing all the elements as it goes.  If a
! node has no sub-elements, it prints the text as well
! as the tag.
!
recursive subroutine printElement(depth, p)

    use FoX_dom
    implicit none

    type(Node), pointer :: p
    integer :: depth

    interface
       logical function hasSubElements( p)
          use FoX_dom
          type(Node), pointer :: p
       end function hasSubElements
    end interface

    type(NodeList), pointer :: children
    type(Node), pointer :: cp
    integer :: i
    logical :: first
   
    character(len=200) :: commentLine
    character(len=2000) :: textLIne
    double precision :: ra
  
    character :: indent(40)
 
    indent = "                                      "

    if (hasSubElements(p)) then
      !
      ! If the node has sub-elements it does not have ades data
      ! FoX will report the text as a all the text in all the
      ! children put together, which is not what is wanted.
      !
      print *, indent(1:2*depth), getLocalName(p)
      !call extractDataContent(p, textLine)
      !print *, indent(1:2*depth) , getLocalName(p), ': ', trim(textLine)

      !
      ! now call all elements recursively
      !
      children => getChildNodes(p)
      do i = 0, getLength(children) - 1
        cp => item(children, i)
        if (getNodeType(cp) == ELEMENT_NODE) then ! recursively call subElements 
           call printElement(depth+1, cp)
        endif
      enddo
    else
      !
      ! nodes with no sub-element have data
      !
      print *, indent(1:2*depth) , getLocalName(p), ': ', getTextContent(p)
      !call extractDataContent(p, textLine)
      !print *, indent(1:2*depth) , getLocalName(p), ': ', trim(textLine)

      !
      ! now demonstrate a few extraction features
      !
      if (getLocalName(p) == 'line') then
        call extractDataContent(p, commentLine)
        print *, indent(1:2*depth), "   read as ", trim(commentLine)
      endif
      if (getLocalName(p) == 'ra') then
        call extractDataContent(p, ra)
        print *, indent(1:2*depth), "    read as double ", ra
      endif

    endif

   
end subroutine printElement


!
! main program reads and prints goodtime.xml
!
program readxml_example

  use FoX_dom
  implicit none


  type(Node), pointer :: myDoc, p
  type(NodeList), pointer :: adesList

  interface
     recursive subroutine printElement(depth, p)
        use FoX_dom
        type(Node), pointer :: p
        integer :: depth
     end subroutine printElement
  end interface

  ! Load in the document
  myDoc => parseFile("goodtime.xml")

  ! Find the ades element
  adesList => getElementsByTagName(myDoc, "ades")

  p => item(adesList, 0)
  call printElement(0, p)

  ! Clear up all allocated memory
  call destroy(myDoc)
end program readxml_example
