---
title: 7. Lets practice
updated: 2026-04-06 03:00:57Z
created: 2026-04-04 05:44:43Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Using all the concepts in one large complex query

The following query utilities the commands, ordering and grouping we learned in one query:

`select`  
`FirstName,`  
`LastName,`  
`avg(salary) as AverageSalary,`  
`count(year) as YearsWorked`  
`from Employee`  
`group by FirstName, LastName`  
`having count(year) > 2`  
`order by avg(salary) desc;`

This finds employees that have worked 2 or more years at the company, ordered by average salary descending.

## Overview

Additional details.
