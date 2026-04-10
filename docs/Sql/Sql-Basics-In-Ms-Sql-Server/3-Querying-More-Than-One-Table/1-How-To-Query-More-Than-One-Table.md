
## Joining tables the simplest way

The easiest way is to mention both tables in the FROM clause.
`select * from Movie, Director;`

This is the most useless way to join tables, no one uses this method. This simple FROM clause method is the same as using CROSS JOIN because SQL does not know what you want from the data so it just makes every combination between the rows in both tables.
`select * from Movie cross join Director;`

## JOINs using the WHERE clause

Again, another simple but no one uses it method is using the WHERE clause to do what a JOIN and ON clause would do. Not standard but good to know if someone uses this method in their code. This is equivalent to the clause JOIN so its an inner join.

`select * from movie, director where movie.director_ID = directors.ID`

&nbsp;

&nbsp;