---
title: 5. Grouping
updated: 2026-04-06 02:35:52Z
created: 2026-04-04 05:43:51Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Using GROUP BY to get meaningful statistics

As mentioned on the aggregation page, GROUP BY is required for us to use aggregate functions in a meaningful way.

This example counts all the employees per department.

`select department, count(FirstName) as DepartmentEmployees`  
`from Employee where Year = '2013'`  
`group by department`

This finds the MIN and MAX salary of each department, multiple functions can be used before a group by.

`select`  
`department,`  
`MIN(salary) as MinDepartmentSalary,`  
`MAX(salary) as MaxDepartmentSalary`  
`from Employee where year = '2014'`  
`group by department`

Average salary per department

`select`  
`department,`  
`AVG(salary) as AvgDepartmentSalary`  
`from Employee where year = '2015'`  
`group by department`

## Grouping by more than one column

You can also group by more than one column if you want to group by a more specific scenario, such as customers and their orders. Remember, using group by requires you to only select the columns used in the group by clause, selecting additional columns for information won't work here even if SQL let you do it, as the extra information will be collapsed under the grouped columns anyway. 

This fins average salaries of employees, but as you can see all the non columns in the select statement that are not some sort of aggregate command, must be mentioned in the group by clause while the aggregate commands which make new columns don't have to be mentioned in the group by clause.

`SELECT`  
`FirstName,`  
`LastName,`  
`AVG(salary) as AvgSalary`  
`FROM Employee`  
`GROUP BY FirstName, LastName;`

&nbsp;