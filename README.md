# CSV Query Compiler - Compilation Technique Final Project

Group 1:
- Ahmad Zaydan
- Edward Liandi
- Kenneth

## How to use
- Run main.py
- Type in your Query
- Press Enter

## Query Description
- FROM --> us to access the csv file
- SELECT --> select the column
- WHERE --> the conditions. (Ex: age <= 18)
- LIMIT --> Limit the printed list
- AND
- OR
- ASC --> Ascending order
- DESC --> Descending order
- OFFSET --> Skips a number of rows before returning results.
- DISTINCT: Removes duplicate rows
- AS : set alias to a column
- AND, OR, NOT : Logic
- IN : Checks membership in a set of values.
- BETWEEN : Tests whether a value lies within a range.
- LIKE : find string based on patterns
- IS NULL : Check missing value
- IS NOT NULL:  Check non-missing value
- ORDER BY: Sorts the result set by a specified column.
- SORTBY : Same like ORDER BY, DSL alternative
  
## Example Usage
FROM "HARGA RUMAH JAKSEL.csv"  
SELECT HARGA, LT  
WHERE HARGA <= 10000000000 AND LT <= 1000  
ORDER BY HARGA DESC  
LIMIT 10  
