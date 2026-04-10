---
title: 4. Aggregation
updated: 2026-04-05 23:14:04Z
created: 2026-04-04 05:43:40Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Computing basic statistics


We can use specific window functions, or commands, to achieve specific statistics in SQL. These commands are more complex than just being simple clauses.

COUNT() - used to count the total number of whatever column is specified

`select count(*) as EmployeeNumber from Employee `
This counts all the rows in a table, not very useful but you get the idea, its used in the select clause and should be renamed to something meaningful.

`select count(role) as RoleCount from teachers `
Using specific columns in count(), allows you to count all the records where that column is filled in. It will not count NULLs.

`select count(distinct customerID) as DISTCustomer from order`
DISTINCT should be used within the aggregate if you want that specific calculation to be only include the unique values.

Those examples represent the possible syntax to use but a common use of count() would look like this:
`select id, name, count(OrderNumber) as OrderCount from orders; `

That would make a new column and after each order, there would be a count for how many orders that person has done. This will not filter the results down to unique values, so every single order will have the same number in the OrderCount column for the same ID.

To use aggregates properly in SQL, and for them to be more meaningful, we have to use the GROUP BY clause which is mentioned later on. You actually require a GROUP BY clause for these to even run in the first place unless you are just selecting the aggregate column.

All columns which are not aggregates (the ones not using counts and commands like that) need to be added to the GROUP BY section, which makes aggregating useful but more annoying as you can't just use \* to pull in every column, you need to mention them all specifically.

# Others


Apart from count we also have:

MIN() - find the minimum value in the column

MAX() - find the maximum value in the column

SUM() - adds all the values in the column

AVG() - finds the average of all the values in a column

Note: in real life these commands won't usually be used on the entire column, it will be used for use cases such as the average salary by department for example, this is where the GROUP BY clause comes into play. It basically says "use this command on each of these groups", such as grouping by department name will use the average command on the salary column and give an average for each departments separately.

&nbsp;