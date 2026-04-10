---
title: 7. Aliases for tables
updated: 2026-04-09 06:20:19Z
created: 2026-04-04 05:46:30Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Renaming tables for quicker reference


This has been used in every exercise so far, but referring to tables can be made easier by giving a table a new alias in the FROM clause. No, there is no need to use the AS keyword every time but it is best practice to do so. In small databases using one letter aliases works well, but in complex queries this isn't always best practice so you may need to come up with a shorter but meaningful naming scheme such us cust for customers.

Example:

`select`
        `  e.Id, e.Name, r.RoomNumber, r.Beds`
`from room as r`
`join equipment as e on e.RoomId=r.Id;`

# Aliases in SELF JOINs


Self joins are not super typical in live enterprise databases but there are some situations where two different objects we want to compare or match are stored in the same table. Such as a table called person storing children and their parents, or a employees table storing managers and their team members. Because mothers and children are both people, and managers are employees just like their team members, they are stored in the same table.

This example self joins to find everyone who also have the same RoomId as Jack. The first student table searches for jack specifically, while joining it to itself we filter the second instance of the table to find everyone but himself.

`select distinct *`
`from student a1 join student a2 on a1.RoomId=a2.RoomId`
`where a1.Name = 'Jack Pearson' and a2.Name != 'Jack Pearson';`

# Joining more than one table challenge


Joining more than two tables, and even self joining while doing that is entirely possible. Such queries need careful planning, as they can be complicated but breaking down what you need does help.

For each room with two beds where there are actually two students, we want to show one row that contains the following information:

&nbsp;   The name of the first student.
    The name of the second student.
    The room number.

Don't change any column names. Each pair of students should only be shown once. The student whose name comes first in the alphabet should be shown first.

# My solution


`select`
`s1.name,`
`s2.name,`
`r.RoomNumber`
`from room r`
`join student s1 on r.Id=s1.RoomId`
`join student s2 on r.Id=s2.RoomId`
`where r.Beds=2 and (s1.Name != s2.Name) and (s1.Name < s2.Name)`

&nbsp;

# Answer


`SELECT`
      `  S1.Name,`
      `  S2.Name,`
      `  RoomNumber`
`FROM Student S1`
`INNER JOIN Student S2`
      `  ON S1.RoomID = S2.RoomID`
`INNER JOIN Room`
      `  ON S1.RoomID = Room.ID`
`WHERE S1.Name < S2.Name`
      `  AND Beds = 2;`

&nbsp;

# Explanation


&nbsp;