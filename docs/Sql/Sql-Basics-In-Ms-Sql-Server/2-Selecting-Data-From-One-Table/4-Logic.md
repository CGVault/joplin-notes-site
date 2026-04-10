
## Logical operators

OR - records that fulfill one or more of the conditions will pass the filter
AND - records passing both conditions will pass the filter
BETWEEN - records falling between two numbers pass the filter, this is the clause equivalent of doing => AND <=. `where results between 90 and 100`
NOT - flips the filter so the results become opposite of what the filter passes. `where results not between 90 and 100`
<br/>

## Complex conditioning

Combining conditions can be complex, messy, and hard to create from scratch. Its better to use brackets () to group conditions, and then stack them using AND/OR depending on your use case.

Example:
`select results from student where (mark > 70 AND mark < 99) AND (rank not between 80 and 100) OR (subject = 'Math' OR subject = 'Science')`

&nbsp;

&nbsp;