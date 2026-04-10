---
title: 4. Lets practice
updated: 2026-04-05 16:45:51Z
created: 2026-04-04 05:42:58Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Complex practice


A complex example combining concepts so far:

`SELECT`
  `  m.Title,`
  `  m.ProductionYear,`
  `  d.Name,`
  `  d.BirthYear as BornIn`
`FROM Movie as m`
`JOIN Director as d`
  `  ON m.DirectorId = d.Id`
`WHERE m.ProductionYear - d.BirthYear < 40; `

Learning observations:
Renaming a column so its displayed differently in the results does not allow you to refer to that column using its alias in other areas like the WHERE clause. Tables can but columns cannot.

# An even more complex query


This goes back and includes all the concepts up until now:

`SELECT`
  `  m.Id,`
  `  m.Title,`
  `  m.ProductionYear as ProducedIn,`
  `  d.Name,`
  `  d.BirthYear as BornIn`
`FROM Movie as m`
`JOIN Director as d`
  `  ON m.DirectorId = d.Id`
`WHERE (m.Title like '%a%'and m.ProductionYear > 2000)`
  `  or (d.BirthYear between 1945 and 1995)`
  `  ; `

Learning observations:
Filters often have use cases where they are grouped, so you need to put scenario 1 all in brackets and then us OR with scenario 2 in brackets. If need be you can double bracket (()) longer scenarios you want to test for complex use cases.

&nbsp;