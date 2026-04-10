---
title: 3. Eliminating duplicate records
updated: 2026-04-05 17:29:10Z
created: 2026-04-04 05:43:26Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

## Duplicates and DISTINCT

The clause DISTINCT is used to remove duplicate records for reporting purposes and is very often used to get a list of unique values in a specific column, like all the years an order was placed.

  
`select distinct YearOrder from Orders; ` 

Remember, DISTINCT removes duplicate rows. So using it across multiple columns works well if you know what the query is doing. This selects records where a customer has done at least one order on a day. The customer IDs will repeat because they are paired up with a unique date. But if a customer order twice on the same day, those records won't show up as the record will have the same customer ID and date:  
<br/>

`select distinct customerID, OrderDate from Orders; ` 

Another use case for distinct is select all the unique combinations of two columns such as all the positions in each department.

&nbsp;