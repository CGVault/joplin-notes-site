---
title: '6. HAVING: filtering and ordering groups'
updated: 2026-04-06 02:55:24Z
created: 2026-04-04 05:43:57Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Filtering the results after grouping has occurred

When making queries with a group by clause, we can always filter the the data coming in before the grouping happens, like filtering according to a column we haven't selected in the SELECT clause such as filtering all data before a certain date.

However, if we want to filter the data after it has been grouped, like filtering by one of the aggregates we performed, we have to use the HAVING clause. 

In this case, we want filter the number if years an employee has worked, which is something we had to calculate, so we use the HAVING clause after the group by to filter according to our COUNT calculation.

`SELECT`  
`FirstName,`  
`LastName,`  
`COUNT(Year) as EmployeeYears`  
`FROM Employee`  
`GROUP BY FIrstName, LastName`  
`HAVING COUNT(Year) > 2;`

Here is an example where we filter the data before its group, limiting it to a specific year. Then we filter the data after its grouped to limit the data according to the average salary calculation we made.

`SELECT`  
`department,`  
`AVG(salary) as AvgDepartmentSalary`  
`FROM Employee`  
`WHERE year = '2012'`  
`GROUP BY department`  
`HAVING AVG(salary) > 3000;`

# Ordering groups

ORDER BY can still be used after all the grouping has occurred, and the ORDER BY clause can order using the calculation we did in the select statement. 

This examples group's total employee salaries, and then it filters the total salaries calculated using SUM() in descending order to find the employee with the highest total salary.

`SELECT`  
`FirstName,`  
`LastName,`  
`SUM(salary) as TotalSalary`  
`FROM Employee`  
`GROUP BY FIrstName, LastName`  
`ORDER BY SUM(salary) desc;`

&nbsp;

## Overview

Additional details.
