import requests
import datetime
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup

# Constantes to bandejão:
# Limites de tempo para cada refeição (com folga):
limiteinfcaf = datetime.time(6,00,00)
limitesupcaf = datetime.time(10,00,00)
limiteinfalm = datetime.time(11,00,00)
limitesupalm = datetime.time(16,00,00)
limiteinfjan = datetime.time(17,00,00)
limitesupjan = datetime.time(21,00,00)

username = input('Username: ')
password = input('Senha: ')

# Dados de login
loginData = {'codpes' : username,
             'senusu' : password}

# Para outros sites da uspdigital, basta alterar o 'rucard' para 'jupiterweb', etc.
urlRUCard = 'https://uspdigital.usp.br/rucard/autenticar'
# Página do Extrato do bandejon
urlExtrato = 'https://uspdigital.usp.br/rucard/extratoListar'

# Cookies
jar = requests.cookies.RequestsCookieJar()

headers = {'Referer' : urlRUCard,
           'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/201001',
           'Host' : 'uspdigital.usp.br',
           'Connection' : 'keep-alive'}


req = requests.post(urlRUCard, data = loginData, cookies = jar)
print(req.status_code)
print(req.cookies)
print(req.headers)
jar = req.cookies
extrato = requests.get(urlExtrato, cookies = jar)
soup = BeautifulSoup(extrato.text, 'html.parser')

# Classe para refeições e recargas. Contém data-tempo, dinheiro movimentado, tipo de evento, e saldo no momento
class Evento:
    def __init__(self, datetime, dinheiro, tipo, saldo):
        self.datetime = datetime
        self.dinheiro = dinheiro
        self.tipo = tipo
        self.saldo = saldo
    def __repr__(self):
        return('Hora: ' + self.datetime.ctime() +
               ';\n Dinheiro: ' + str(self.dinheiro) +
               ';\n Tipo: ' + str(self.tipo) +
               ';\n Saldo: ' + str(self.saldo) + '.\n')

# Lista de Eventos. A ser preenchida:
eventos = []

for tr in soup.find_all('tr')[3:-1]:
    # Transformando da string modificada do BeautifulSoup para uma string (lista de) normal.
    tdsraw = tr.find_all('td')
    tds = []
    for td in tdsraw:
        tds.append(repr(td.string))

    # Datetime para o tempo do evento. O formato da tabela é "'DD/MM/YYYY HH:MM:SS'"
    time = tds[0]
    dt = datetime.datetime(int(time[7:11]), int(time[4:6]), int(time[1:3]), int(time[12:14]), int(time[15:17]), int(time[18:20]))

    # dinheiro em valor absoluto. Ganhará sinal após o tipo ser encontardo
    dinheiro = float(tds[2][1:-1])

    if tds[1][1:-1] == 'DEBITO':
        #Sabemos que é refeição
        dinheiro *= -1
        if  limiteinfcaf < dt.time() and dt.time() < limitesupcaf:
            tipo = 'caf'
        elif limiteinfalm < dt.time() and dt.time() < limitesupalm:
            tipo = 'alm'
        elif limiteinfjan < dt.time() and dt.time() < limitesupjan:
            tipo = 'jan'
        else:
            tipo = None
    elif tds[1][1:-1] == 'CREDITO':
        tipo = 'pag'

    saldo = float(tds[3][4:-1].replace(',','.'))

    evento = Evento(dt, dinheiro, tipo, saldo)
    eventos.append(evento)

# Plot do gráfico de frequência ao bandejão por tempo:

tempos = []
for evento in eventos:
    if evento.dinheiro < 0:
        temporaw = evento.datetime
        # Aqui, o tempo é em horas depois da meia noite
        tempo = temporaw.hour + temporaw.minute/60 + temporaw.second/3600
        tempos.append(tempo)

fig = plt.figure(figsize=(10,3))
ax = fig.add_subplot(111)

ax.hist(tempos, bins=80, range=(7,20))

ax.set_xlabel('Hora')
ax.set_ylabel('Frequência')
ax.set_title('Refeições no Bandejão')

fig.tight_layout()
plt.show()
