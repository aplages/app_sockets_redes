import json

teste = {
    'acao': 'teste',
    'teste': 'abc def ghi'
}


teste = json.dumps(teste)+'\n'+json.dumps(teste)+'\n'

#print(teste)
print(teste.strip().split('\n'))
print('a')