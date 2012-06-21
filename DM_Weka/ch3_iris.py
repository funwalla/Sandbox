import arff

data = open('iris_data.txt', 'rb').read()
data = data.split('\r\n')
iris_data = []
for row in data:
    row = row.split(',')
    tmp = map(lambda x: float(x), row[:4])
    tmp.append(row[4])
    iris_data.append(tmp)

attr_dict = {'sepallength':0, 
             'sepalwidth':1, 
             'petallength':2, 
             'petalwidth':3, 
             'class':4}
    
SETOSA = 'Iris-setosa'
VERSICOLOR = 'Iris-versicolor'
VIRGINICA = 'Iris-virginica'

row_number = 0
for row in iris_data:
    if row[2] >= 2.45 and row[2] < 5.355 and row[3] < 1.75: 
        newclass = VERSICOLOR
        if (row[2] >= 4.95 and row[3] < 1.55) or (row[0] < 4.95 and row[1] >= 2.45):
            newclass = VIRGINICA
    elif row[2] >= 3.35:
        newclass = VIRGINICA
        if row[2] < 4.85 and row[0] < 5.95: newclass = VERSICOLOR
    else:
        newclass = SETOSA
    if row[4] != newclass: print "Check row number", row_number
    row.append(newclass)
    row_number += 1

        
        
        
        
print "breakpoint"
