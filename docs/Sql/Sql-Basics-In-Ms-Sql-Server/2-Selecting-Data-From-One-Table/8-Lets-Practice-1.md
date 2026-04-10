
## Combination of all concepts complex example

Here is an example query using best practice coding (as far as I am concerned) combining all the concepts into a complex query.

`select`
`*`
`from Car`
`where (ProductionYear between 1999 and 2005)`
`and (brand not like 'Volkswagen')`
`and (model like 'P%' or model like 'F%')`
`and (price is not null)`
`;`

Some teachable moments observed:
NOT goes before the clause its flipping
IS isn't not required for every clause, using between should not be is between while like should not be is like
When using clauses like OR/AND inside the same comparison like in the third last line, mention the column again after OR/AND to make a second comparison. If not it usually throws a "this isn't a boolean decision" error. This may not happen with pure mathematical statements but it will happen for string filters.

Most improvements surround thinking in SQL, easy to mistake good looking syntax with what looks logical when speaking English.