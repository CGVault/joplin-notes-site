
## Using all the concepts in one large complex query

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