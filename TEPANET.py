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

    caminho_arquivos_selecionados = None
#loop para o usuário continuar selecionando arquivos até ele cancelar a janela de seleção
    while True:
        print("*"*50,"Abrindo janela de seleção dos arquivos...",sep='\n')
        root = tk.Tk()
        root.withdraw()
        filetypes = [("RPT Files", "*.rpt"), ("Arquivos CSV", "*.csv"), ("Arquivos de Texto", "*.txt"), ("All Files", "*.*")]
        root.attributes('-topmost', 1)
        initialdir = caminho_arquivos_selecionados
        arquivos_selecionados = filedialog.askopenfilenames(title='Abrir Arquivo Relatório Bruto',filetypes=filetypes,initialdir=initialdir)
        if len(arquivos_selecionados) >= 1:
            caminho_arquivos_selecionados = arquivos_selecionados[0][:-(arquivos_selecionados[0][::-1].find('/')+1)]
        else:
            print('Fechando programa...')
            sys.exit()

#seleção do usuário de arquivo(s) de saída
        try:
            saida_selecionada = input('Deseja a saída como:\n(1) arquivos relatórios não tratados em CSV\n' + \
                                        '(2) três arquivos CSV separados com as tabelas de cada relatório\n' + \
                                            '(3) ambas as opções listadas acima para cada relatório\n\t').strip()
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

#seleciona caminho dos arquivos gerados e abre cada arquivo selecionado pelo usuário para gerar
            pasta_selecionada = filedialog.askdirectory(title='Local para Salvar Arquivos de Saída',initialdir=initialdir)
            if pasta_selecionada == '':
                print('Fechando programa...')
                sys.exit()

            for arquivo_selecionado in arquivos_selecionados:
                print('\tAbrindo ' + arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):])

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
                if bool_arquivo0:
                    arquivo_saida0 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(0).csv'
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
                    arquivo_saida1 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(1).csv'
                    arquivo_saida2 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(2).csv'
                    arquivo_saida3 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(3).csv'
                    tabela_trecho_no.to_csv(arquivo_saida1, index=False)
                    tabela_resultado_no.to_csv(arquivo_saida2, index=False)
                    tabela_resultado_trecho.to_csv(arquivo_saida3, index=False)
                    print('Tabela Trecho - Nós>> ' + arquivo_saida1)
                    print('Tabela Resultados dos Nós >> ' + arquivo_saida2)
                    print('Tabela Resultados dos Trechos >> ' + arquivo_saida3)
                
#visualizar tabelas no terminal temporariamente
                    while True:
                        tabela_desejada = input(f'\tVisualização Rápida de {arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4]}:\n' + \
                                                '\t\t(1) Tabela Trecho - Nós\n' + \
                                                '\t\t(2) Tabela Resultados dos Nós\n' + \
                                                '\t\t(3) Tabela Resultados dos Trechos\n' + \
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
                print(f'\tSalvamento do(s) arquivo(s) {arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):]} concluído\n')

#aviso ao usuário que o arquivo selecionado será fechado
        print("-"*10 + "Seleção concluída!" + "-"*10 + "\n")
