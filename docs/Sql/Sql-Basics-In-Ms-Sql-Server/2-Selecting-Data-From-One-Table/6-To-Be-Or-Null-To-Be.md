---
title: 6. To be or NULL to be
updated: 2026-04-05 14:44:37Z
created: 2026-04-04 05:40:27Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# NULL values


Filtering for NULL values is useful for finding missing information and disregarding records that have incomplete columns/fields. NULL is a void, it is not 0 or an empty string or date, it is a column/field that has not been filled in at all.

In SQL, because NULL doesn't equal 0, records with a 0, like a price for example, won't show up in  the results. NULL is special and will always be excluded from the results unless there is a condition searching for it.
<br/>Furthermore, NULL in T-SQL interestingly doesn't equal itself. NULL = NULL is false.

Filtering NULLs uses the clause IS, NOT, NULL, to get NULL values we can use IS NULL. The clauses IS, NOT and NULL are separate clauses but are used together in this instance. IS can be used for IS IN, NOT flips other results too, etc.

`select * from student where result IS NOT NULL` finds all the students that have results. Using IS NULL will find records where the results column hasn't been filled in.