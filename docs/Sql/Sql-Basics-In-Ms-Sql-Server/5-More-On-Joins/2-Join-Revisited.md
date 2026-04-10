---
title: 2. JOIN revisited
updated: 2026-04-06 04:46:36Z
created: 2026-04-04 05:45:46Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Revising JOINs

The basic JOIN command just does an inner join, it joins all the records where the table a and table b columns match, adding on the extra information from table b onto the table a records. 

`SELECT`  
  `  *`  
`FROM Student s`  
`JOIN Room r`  
  `  ON s.RoomID=r.Id ;`

Using JOINs with specific columns:

`SELECT`  
  `  s.Name,`  
  `  r.RoomNumber`  
`FROM Student s`  
`JOIN Room r`  
  `  ON s.RoomId=r.Id ;`

# INNER JOIN

The normal JOIN clause is just the shorthand way of typing INNER JOIN, they do the exact same thing. Its best to use INNER JOIN for clarity especially in large queries. 

`SELECT`  
  `  *`  
`FROM Equipment e`  
`INNER JOIN Room r`  
  `  ON e.RoomId=r.Id ;`

# How it works

INNER JOIN only joins the records which match both columns from the two tables being joined. So if the student and room tables are connected using s.RoomId=r.Id then students not assigned to a room (the first half of the equation would be NULL) then it doesn't show up in the results. Conversely, if there is a room that is not assigned to any students (the second half of the equation would be NULL) then that room does not show up in the results.

![effdb026b7a904261d9904ad272a5f1e.png](../../../_resources/effdb026b7a904261d9904ad272a5f1e.png)

&nbsp;