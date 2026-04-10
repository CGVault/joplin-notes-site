---
title: 1. Ordering
updated: 2026-04-05 17:15:07Z
created: 2026-04-04 05:43:10Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

## Ordering results

Results without an order is useless for reporting, so after all the selecting, filtering, any aggregation, we sort the results by a specific column. The ORDER BY clause arranges all the records according to the column chosen. By default its ASC (ascending) so you do not need to type it out each time but its best practice to do so, DESC flips it to descending order. Not all SQL servers are setup the same and this is why we explicitly code in everything even if it takes longer.

`select * from employee order by salary ` 

Filter first:

`select * from Employee where Employee.Year = 2011 order by salary desc ` 

## Multi ordering

You can order by multiple columns, and in different orders. The first column will take priority with the columns used afterwards proceeding with their sorting in the order that they are written.

A good use case for this is when the primary column used for sorting, like IDs, has duplicates in a table like multiple orders from the same person. Ordering by a second column, like price of order, makes the data more useful.

If a column used for ordering does not have duplicates then no further ordering will happen. Columns later on in the ORDER BY clause cannot alter the previously sorted data created by sorting from earlier mentioned columns. If orders are already in order by ID, and each ID is unique, then no sub-ordering can happen as within each ID only one record exists.

Or if orders are sorted by ID, and price, and all the prices are unique, then you cannot order further using something else like order time. This is why columns chosen for the ORDER BY clause have to be chosen and put in order carefully to represent a specific metric,

`select * from Employee order by department asc, salary desc ` 

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;