from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

def sum(a):  
    date = datetime.datetime.now()
    
        
    if a < 12:
        result = (12 - a)
        return date + relativedelta(month=result - 1)
    
    result = (a / 12)
    length = str(result)
    anos = int(length[0])
    
    if anos == 1:
        a = a - 12
    elif anos == 2:
        a = a - 24
    elif anos == 3:
        a = a - 36
    elif anos == 4:
        a = a - 48
    else:
        a = a - 60
        
    
    a = 12 - a    
    
    result = date + relativedelta(month=a, year=date.year - anos)            
    return result
    
        

a = int(input('Digite a parcela atual referente a 11/2023: '))

print(f'O periodo inicial referente a parcela {a} é igual a {sum(a)}')