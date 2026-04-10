---
title: 3. Filtering rows
updated: 2026-04-05 06:05:34Z
created: 2026-04-04 05:40:02Z
latitude: -33.86881970
longitude: 151.20929550
altitude: 0.0000
---

# Only selecting a few rows

We can use the WHERE keyword to filter rows according to a specific condition. We use it like this `select * from student where name = jack` . The condition can be much more complex than this.

# Conditional operators

You can use the usual mathematics symbols like less than, greater than, equals, plus, minus, etc to make other conditions.  
Keywords like NOT can be used in SQL to flip results but for us the mathematics equivalent of this would be !=.

# Combining conditions and columns

You can select specific columns while using conditions to limit results further. For example we can use `select id, name from student where not name = james` to selected everyone who is not James. Using `where name != james` does the same.

You can use a WHERE clause to filter according to a column that has not been listed in the select clause. So `select id, name from student where results = 100%` still works. 

&nbsp;

&nbsp;

## Overview

Additional details.
