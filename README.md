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
- ORDER BY --> Order the printed list
- LIMIT --> Limit the printed list
- AND
- OR
- ASC --> Ascending order
- DESC --> Descending order

## Example Usage
FROM "HARGA RUMAH JAKSEL.csv"  
SELECT HARGA, LT  
WHERE HARGA <= 10000000000 AND LT <= 1000  
ORDER BY HARGA DESC  
LIMIT 10  
