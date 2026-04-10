---
title: 3. LEFT JOIN
updated: 2026-04-06 05:34:55Z
created: 2026-04-04 05:45:54Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# What is a LEFT JOIN

While an INNER JOIN only results in rows where both tables have a matching value in the ON clause equation, a LEFT JOIN displays all results from the first table no matter what, plus any records from the second table that match with a record from the first table according to the ON clause equation. 

Like the INNER JOIN example, using the tables student and room with the equation s.RoomId=r.Id will result in every student being in the results even if the left side of the equation is NULL which is when a student doesn't have a room assigned. The resulting dataset will have all the students from the students table, and the students who have NULL values for their RoomId will also have NULLs for the columns from Rooms table, columns like RoomName will be NULL. Rule of thumb is if the column tested in the equation is NULL for the first table, then the columns attached from the second table will be NULL also. 

Example of what I mean:

`SELECT`  
  `  *`  
`FROM student s`  
`LEFT JOIN room r`  
  `  ON s.RoomId=r.Id`  
`order by s.RoomId;`

Results:

| Id  | Name | RoomId | Id  | RoomNumber | Beds | Floor |
| --- | --- | --- | --- | --- | --- | --- |
| 2   | Charlie Black | null | null | null | null | null |
| 4   | Mary Benett | null | null | null | null | null |
| 7   | Jacob Chapman | null | null | null | null | null |
| 8   | Charlotte Wood | 1   | 1   | 101 | 2   | 1   |
| 9   | Emily Lane | 1   | 1   | 101 | 2   | 1   |
| 12  | Noah Rose | 5   | 5   | 201 | 1   | 2   |
| 1   | Jack Pearson | 8   | 8   | 204 | 3   | 2   |
| 5   | Brian Saunders | 8   | 8   | 204 | 3   | 2   |
| 6   | Ella Watson | 8   | 8   | 204 | 3   | 2   |
| 10  | Freya Hart | 10  | 10  | 301 | 4   | 3   |
| 11  | Megan Mcdonald | 10  | 10  | 301 | 4   | 3   |
| 15  | Benjamin Slade | 10  | 10  | 301 | 4   | 3   |
| 13  | Oscar Walls | 10  | 10  | 301 | 4   | 3   |
| 14  | Luke Wild | 11  | 11  | 302 | 1   | 3   |
| 3   | Ethan Wright | 15  | 15  | 403 | 1   | 4   |

## Overview

Additional details.
