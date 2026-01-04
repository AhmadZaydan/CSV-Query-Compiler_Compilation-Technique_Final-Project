text = '''
    FROM "students.csv"
    SELECT name, score
    WHERE score >= 80 AND city = "Bandung"
    ORDER BY score DESC
    LIMIT 10
    '''

tokenEx = lex(text)
for t in tokenEx:
    print(t)