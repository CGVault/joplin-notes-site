---
title: 6. OUTER JOIN
updated: 2026-04-06 06:34:29Z
created: 2026-04-04 05:46:15Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# OUTER

Outer join is just the official term we use for joins which include both records which do and records which don't match up across the ON clause equation. LEFT OUTER JOIN, RIGHT OUTER JOIN, FULL OUTER JOIN are the official names. You do not need to use the word outer when making joins in SQL but if you want to be fancy, or you are writing code with extensive documentation for new users that need to start using your code, then using the full names can help.

Example for returning all kettles regardless if assigned to a room or not:

`SELECT`
  `  *`
`FROM room r`
`RIGHT OUTER JOIN equipment e`
  `  ON e.RoomId=r.Id`
`WHERE e.Name='kettle';`

&nbsp;