---
title: 5. Text patterns
updated: 2026-04-05 16:19:54Z
created: 2026-04-04 05:40:17Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Conditions using strings

Conditions created with the where clause can also filter according to strings. Examples include

Equating to a specific string
`select * from student where name = 'max'`

Equating to unicode strings (special characters using N)
`select * from student where absent = N'✅'`

Wildcard filters using the LIKE clause such as using:
% - zero or more (infinitely) unknown characters
`select * from student where name like 'A%'` (could also be '%A% for any name with an A in it ("A" also counts) or %A for ending in A.

_ - one unknown character
`select * from student where name like 'M_x' or '_ax' or 'Ma_'`

&nbsp;

NOTE: You do not need to use unicode strings for each and every query, but its a good habit to do so. Best practice mostly if data has a likely possibility of special characters like emojis or icons for representing columns using ticks and crosses.