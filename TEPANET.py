import sys
from tkinter import filedialog
import tkinter as tk
import numpy as np
import pandas as pd

#cabeçalho
print("*"*50,'Bem vindo(a) ao programa Transformador de Relatório EPANET 2.0 LENHS',sep='\n')

#seleção de símbolo para casas decimais
try:
    lingua = input('Deseja o(s) arquivo(s) resultado com:\n(1) vírgula decimal\n(2) ponto decimal?\n\t').strip()
    if lingua == '':
        print('Fechando programa...')
        sys.exit()
    else:
        lingua = int(lingua)
except Exception as e:
    raise e('Entrada inválida, digite apenas "1" ou "2"!')
else:
    if lingua == 1:
        transforma_simbolo_decimal = ('.',',')
    elif lingua == 2:
        transforma_simbolo_decimal = (',','.')
    else:
        raise ValueError('Entrada inválida, digite apenas "1" ou "2"!')
finally:

#loop para o usuário continuar selecionando arquivos até ele cancelar a janela de seleção
    while True:
        print("Abrindo janela de seleção do arquivo...")
        root = tk.Tk()
        root.withdraw()
        filetypes = [("Arquivos de Texto", "*.txt"), ("Arquivos CSV", "*.csv")]
        root.attributes('-topmost', 1)
        arquivo_selecionado = filedialog.askopenfilename(title='Abrir Arquivo Relatório Bruto',filetypes=filetypes)
        caminho_arquivo_selecionado = arquivo_selecionado[:-(arquivo_selecionado[::-1].find('/')+1)]
        if arquivo_selecionado == '':
            print('Fechando programa...')
            sys.exit()
        print('\t' + arquivo_selecionado[(len(caminho_arquivo_selecionado)+1):])

#substitui símbolos decimais e separa o arquivo em um array bidimensional chamado final0
        final0 = []
        with open(arquivo_selecionado, 'r') as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                linha = linha.strip().replace(transforma_simbolo_decimal[0], transforma_simbolo_decimal[1])
                lista_linhas = []
                lista_linhas.append(linha)
                for componente in lista_linhas:
                    componente = componente.split(sep = " ")
                    componente = [item for item in componente if item != ""]
                    final0.append(componente)

#seleção do usuário de arquivo(s) de saída
        try:
            saida_selecionada = input('Deseja a saída em:\n(1) um arquivo relatório não tratado em CSV\n' + \
                                        '(2) três arquivos CSV separados com as tabelas do relatório\n' + \
                                            '(3) ambas as opções listadas acima\n\t').strip()
            if saida_selecionada == '':
                print('Fechando programa...')
                sys.exit()
            else:
                saida_selecionada = int(saida_selecionada)
        except Exception as e:
            raise e('Entrada inválida, digite apenas "1", "2" ou "3"!')
        else:
            bool_arquivo0 = False
            bool_arquivo123 = False
            if (saida_selecionada == 1) | (saida_selecionada == 3):
                bool_arquivo0 = True
            if (saida_selecionada == 2) | (saida_selecionada == 3):
                bool_arquivo123 = True
            if saida_selecionada not in range(1,4):
                raise ValueError('Entrada inválida, digite apenas "1", "2" ou "3"!')
        finally:

#reescreve todas as linhas numa string separada por ";"
            str_arquivo_csv = ""
            list_arquivo_csv = []
            for linha in final0:
                linha_csv = ""
                for palavra in linha:
                    linha_csv = linha_csv + palavra + ";"

                if bool_arquivo0:
                    str_arquivo_csv = str_arquivo_csv + linha_csv[:-1] + "\n"
                if bool_arquivo123:
                    list_arquivo_csv.append(linha_csv[:-1])
            str_arquivo_csv = str_arquivo_csv.strip()

#salvando arquivo (0)
            pasta_selecionada = None
            if bool_arquivo0:
                initialdir = caminho_arquivo_selecionado
                pasta_selecionada = filedialog.askdirectory(title='Local para Salvar Arquivos de Saída',initialdir=initialdir)
                if pasta_selecionada == '':
                    print('Fechando programa...')
                    sys.exit()
                else:
                    arquivo_saida0 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivo_selecionado)+1):-4] + '(0).csv'
                    with open(arquivo_saida0, "w") as arquivo:
                        arquivo.write(str_arquivo_csv)
                    print('Relatório não tratado >> ' + arquivo_saida0)

#criando arrays com índices das linhas onde os dados das tabelas começam e terminam no relatório não tratado
            if bool_arquivo123:
                i_tabela_trecho_no = []
                i_tabela_resultado_no = []
                i_tabela_resultado_trecho = []
                for linha in range(0,len(list_arquivo_csv)):
                    if 'Tabela;de;Trecho;-;Nó' in list_arquivo_csv[linha]:
                        i_tabela_trecho_no.append(linha)
                    elif 'Resultados;nos;Nós' in list_arquivo_csv[linha]:
                        i_tabela_resultado_no.append(linha)
                    elif 'Resultados;nos;Trechos' in list_arquivo_csv[linha]:
                        i_tabela_resultado_trecho.append(linha)

                i_tabela_trecho_no_inicio = np.array(i_tabela_trecho_no)+5
                i_tabela_resultado_no_inicio = np.array(i_tabela_resultado_no)+5
                i_tabela_resultado_trecho_inicio = np.array(i_tabela_resultado_trecho)+5
                
                i_tabela_trecho_no_final = np.append(i_tabela_trecho_no[1:], i_tabela_resultado_no[0])-2
                i_tabela_resultado_no_final = np.append(i_tabela_resultado_no[1:], i_tabela_resultado_trecho[0])-2
                i_tabela_resultado_trecho_final = np.append(i_tabela_resultado_trecho[1:], len(list_arquivo_csv))-2

#criando data frames das 3 tabelas existentes no relatório com os títulos de cada coluna
                titulo_tabela_trecho_no = 'Trecho (ID);Início (Nó);Fim (Nó);Comprimento (m);Diâmetro (mm)'.split(sep=';')
                titulo_tabela_resultado_no = 'Nó (ID);Consumo (LPS);Carga Hidráulica (m);Pressão (m);Qualidade;Observação'.split(sep=';')
                titulo_tabela_resultado_trecho = 'Trecho (ID);Vazão (LPS);Velocidade (m/s);Perda de Carga (m/km);Estado'.split(sep=';')
                
                tabela_trecho_no0 = []
                for pagina in range(0, len(i_tabela_trecho_no)):
                    tabela_trecho_no_pagina = [list_arquivo_csv[linha] for linha in range(0,len(list_arquivo_csv)) if linha in range(i_tabela_trecho_no_inicio[pagina], i_tabela_trecho_no_final[pagina]+1)]
                    tabela_trecho_no0.extend(tabela_trecho_no_pagina)
                tabela_trecho_no = []
                for linha in tabela_trecho_no0:
                    tabela_trecho_no.append(linha.split(';'))

                tabela_resultado_no0 = []
                for pagina in range(0, len(i_tabela_resultado_no)):
                    tabela_resultado_no_pagina = [list_arquivo_csv[linha] for linha in range(0,len(list_arquivo_csv)) if linha in range(i_tabela_resultado_no_inicio[pagina], i_tabela_resultado_no_final[pagina]+1)]
                    tabela_resultado_no0.extend(tabela_resultado_no_pagina)
                tabela_resultado_no = []
                for linha in tabela_resultado_no0:
                    tabela_resultado_no.append(linha.split(';'))

                tabela_resultado_trecho0 = []
                for pagina in range(0, len(i_tabela_resultado_trecho)):
                    tabela_resultado_trecho_pagina = [list_arquivo_csv[linha] for linha in range(0,len(list_arquivo_csv)) if linha in range(i_tabela_resultado_trecho_inicio[pagina], i_tabela_resultado_trecho_final[pagina]+1)]
                    tabela_resultado_trecho0.extend(tabela_resultado_trecho_pagina)
                tabela_resultado_trecho = []
                for linha in tabela_resultado_trecho0:
                    tabela_resultado_trecho.append(linha.split(';'))
                
                tabela_trecho_no = pd.DataFrame(tabela_trecho_no, columns=titulo_tabela_trecho_no)
                tabela_resultado_no = pd.DataFrame(tabela_resultado_no, columns=titulo_tabela_resultado_no)
                tabela_resultado_trecho = pd.DataFrame(tabela_resultado_trecho, columns=titulo_tabela_resultado_trecho)

#retirando linhas vazias dos data frames
                tabela_trecho_no.replace('', np.nan, inplace=True)
                tabela_resultado_no.replace('', np.nan, inplace=True)
                tabela_resultado_trecho.replace('', np.nan, inplace=True)

                tabela_trecho_no.dropna(how='all', inplace=True)
                tabela_resultado_no.dropna(how='all', inplace=True)
                tabela_resultado_trecho.dropna(how='all', inplace=True)

#salvando arquivos (1), (2) e (3)
                if pasta_selecionada is None:
                    initialdir = caminho_arquivo_selecionado
                    pasta_selecionada = filedialog.askdirectory(title='Local para Salvar Arquivos de Saída',initialdir=initialdir)
                    if pasta_selecionada == '':
                        print('Fechando programa...')
                        sys.exit()
                arquivo_saida1 = pasta_selecionada + '/' + \
                                    arquivo_selecionado[(len(caminho_arquivo_selecionado)+1):-4] + '(1).csv'
                arquivo_saida2 = pasta_selecionada + '/' + \
                                    arquivo_selecionado[(len(caminho_arquivo_selecionado)+1):-4] + '(2).csv'
                arquivo_saida3 = pasta_selecionada + '/' + \
                                    arquivo_selecionado[(len(caminho_arquivo_selecionado)+1):-4] + '(3).csv'
                tabela_trecho_no.to_csv(arquivo_saida1, index=False)
                tabela_resultado_no.to_csv(arquivo_saida2, index=False)
                tabela_resultado_trecho.to_csv(arquivo_saida3, index=False)
                print('Tabela Trecho - Nós>> ' + arquivo_saida1)
                print('Tabela Resultados dos Nós >> ' + arquivo_saida2)
                print('Tabela Resultados dos Trechos >> ' + arquivo_saida3)
                
#visualizar tabelas no terminal temporariamente
                while True:
                    tabela_desejada = input('\tVisualização Rápida: escolha uma tabela para visualizar no terminal\n' + \
                                            '\t(1) Tabela Trecho - Nós\n' + \
                                            '\t(2) Tabela Resultados dos Nós\n' + \
                                            '\t(3) Tabela Resultados dos Trechos\n' + \
                                            '\tPressione ENTER para sair da visualização rápida\n\t\t').strip()
                    if tabela_desejada == '':
                        break
                    try:
                        tabela_desejada = int(tabela_desejada)
                    except Exception as e:
                        print('\tEntrada inválida!')
                        continue
                    else:
                        if tabela_desejada not in range(1,4):
                            print('\tEntrada inválida, digite apenas "1", "2" ou "3"!')
                            continue
                        elif tabela_desejada == 1:
                            print('\t\t\tTabela Trecho - Nós', tabela_trecho_no.head(11), sep='\n')
                        elif tabela_desejada == 2:
                            print('\t\t\tTabela Resultados dos Nós', tabela_resultado_no.head(11), sep='\n')
                        elif tabela_desejada == 3:
                            print('\t\t\tTabela Resultados dos Trechos', tabela_resultado_trecho.head(11), sep='\n')
                    finally:
                        cancelar = input('\tPressione ENTER para sair da visualização rápida...')
                        if cancelar == '':
                            break

#aviso ao usuário que o arquivo selecionado será fechado
        print("Salvamento concluído, fechando arquivo...\n")