---
title: 4. RIGHT JOIN
updated: 2026-04-06 06:02:39Z
created: 2026-04-04 05:46:00Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
## ---

# What is a RIGHT JOIN

While an INNER JOIN only results in rows where both tables have a matching value in the ON clause equation, a RIGHT JOIN displays all results from the second table no matter what, plus any records from the first table that match with a record from the second table according to the ON clause equation.

Like the INNER JOIN example, using the tables student and room with the equation s.RoomId=r.Id will result in every room being in the results even if the right side of the equation has a value not found on the left side, which is when a room doesn't have any students assigned to it. The resulting dataset will have all the rooms from the rooms table, and the rooms with a RoomId not found in the student table will also have NULLs for the columns from students table, columns like StudentName will be NULL. Rule of thumb is if the value of the column from the second table is not found somewhere in the corresponding column in the first table, then the attached columns from the first table will be NULL also.

Most people just stick to LEFT JOINs and flip the tables around. The order matters a lot. A LEFT JOIN B is the same as B RIGHT JOIN A. LEFT JOIN is used to join two tables almost 100% of the time. RIGHT JOIN only really matters when we have a complex use case requiring us to join more than two tables, and even then everybody just flips the tables around and uses LEFT JOIN. 

## Example:

## `Select`
      `  *`  
`FROM student s`  
`RIGHT JOIN room r`  
      `  ON s.RoomId=r.Id`  
## `  order by s.RoomId;`

## Results:

| Id  | Name | RoomId | Id  | RoomNumber | Beds | Floor |
| --- | --- | --- | --- | --- | --- | --- |
| null | null | null | 2   | 102 | 2   | 1   |
| null | null | null | 3   | 103 | 3   | 1   |
| null | null | null | 4   | 104 | 3   | 1   |
| null | null | null | 6   | 202 | 2   | 2   |
| null | null | null | 7   | 203 | 3   | 2   |
| null | null | null | 9   | 205 | 4   | 2   |
| null | null | null | 12  | 303 | 2   | 3   |
| null | null | null | 13  | 401 | 3   | 4   |
| null | null | null | 14  | 402 | 1   | 4   |
| 8   | Charlotte Wood | 1   | 1   | 101 | 2   | 1   |
| 9   | Emily Lane | 1   | 1   | 101 | 2   | 1   |
| 12  | Noah Rose | 5   | 5   | 201 | 1   | 2   |
| 1   | Jack Pearson | 8   | 8   | 204 | 3   | 2   |
| 5   | Brian Saunders | 8   | 8   | 204 | 3   | 2   |
| 6   | Ella Watson | 8   | 8   | 204 | 3   | 2   |
| 10  | Freya Hart | 10  | 10  | 301 | 4   | 3   |
| 11  | Megan Mcdonald | 10  | 10  | 301 | 4   | 3   |
| 13  | Oscar Walls | 10  | 10  | 301 | 4   | 3   |
| 15  | Benjamin Slade | 10  | 10  | 301 | 4   | 3   |
| 14  | Luke Wild | 11  | 11  | 302 | 1   | 3   |
| 3   | Ethan Wright | 15  | 15  | 403 | 1   | 4   |