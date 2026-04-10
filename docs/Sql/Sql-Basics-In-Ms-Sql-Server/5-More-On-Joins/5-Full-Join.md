---
title: 5. FULL JOIN
updated: 2026-04-06 06:29:21Z
created: 2026-04-04 05:46:08Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# What does a FULL JOIN do

A FULL JOIN, essentially takes the results from a LEFT JOIN, and the results of a RIGHT JOIN and stacks the two outcomes into one table. The result ends up being everything from the first table, everything from the second table, all the records which fulfill an inner join, plus the records that do not fully fulfill an inner join. 

This query:

`SELECT`  
  `  s.Name,`  
  `  r.RoomNumber`  
`FROM student s`  
`FULL JOIN room r`  
  `  ON s.RoomId=r.Id`  
  `  order by s.RoomId;`

Gives us this:

| Name | RoomNumber |
| --- | --- |
| Charlie Black | null |
| Mary Benett | null |
| Jacob Chapman | null |
| null | 102 |
| null | 103 |
| null | 104 |
| null | 202 |
| null | 203 |
| null | 205 |
| null | 303 |
| null | 401 |
| null | 402 |
| Charlotte Wood | 101 |
| Emily Lane | 101 |
| Noah Rose | 201 |
| Jack Pearson | 204 |
| Brian Saunders | 204 |
| Ella Watson | 204 |
| Freya Hart | 301 |
| Megan Mcdonald | 301 |
| Benjamin Slade | 301 |
| Oscar Walls | 301 |
| Luke Wild | 302 |
| Ethan Wright | 403 |

&nbsp;

&nbsp;

## Overview

Additional details.
