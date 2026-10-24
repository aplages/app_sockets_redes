'''mensagem = '/make_group angelo_grupo [angelo,arthur,antony]'
mensagem = mensagem.split(' ')
mensagem = {mensagem[0]:mensagem[1],
            'nomes':mensagem[2]}
print(mensagem)
print((mensagem['nomes']))
'''



teste = {'a':'b',
         'c':'d'}

for t in teste:
    print(t)