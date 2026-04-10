---
title: 3. Referencing columns
updated: 2026-04-05 16:26:57Z
created: 2026-04-04 05:42:50Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Columns when using JOIN

Referencing columns in a query requires you to use TABLE.COLUMN to prevent columns of the same name being ambiguous.

No, the columns used in the ON clause do not need to be in the select clause but must still follow the format.

Maybe if you have a super small database where no tables have columns with the same name you can be lazy in the SELECT clause and just use the names of the columns on their own. Even the ON clause does not need to use the format if the column names are unique. Considering no database put into serious use is this simple, just stick to using the format, its best practice.

## Alias

You can designate an alias for tables to refer to them quicker. This can be done to columns to rename them in the results of your query.

While renaming doesn't always require a specific clause, like tables could just be Customers C, its best practice to use the AS clause such as Customers AS C. Renaming in more complex scenarios requires AS to be used, so use it for all renaming purposes.

`select c.id as CustomerID, o.id as OrderID from customers as c join orders as o on c.id = o.id where o.id IS NOT '1'; ` 

As you can see, once the table alias is made in the from clause, it can be used everywhere else too.

## Filtering JOIN queries

Rule of thumb is to join first and then filter, all columns in the WHERE clause must exist within the tables joined together.

`select * from Person join Car on Person.ID = Car.OwnerID where Person.age < 25 or Car.OwnderName = 'Max'; ` 

&nbsp;

&nbsp;