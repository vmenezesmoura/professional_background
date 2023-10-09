import sys
from tkinter import filedialog
import tkinter as tk
import numpy as np
import pandas as pd
import keyboard

#cabeçalho
print("*"*50,'Bem vindo(a) ao programa Transformador de Relatório EPANET 2.0 LENHS',sep='\n')

#seleção de símbolo para casas decimais
try:
    lingua = input('Deseja o(s) arquivo(s) resultado com:\n(1) vírgula decimal\n(2) ponto decimal?\n\t').strip()
    decimal_escolhido = True
    if lingua == '':
        print('Fechando programa...')
        decimal_escolhido = False
        sys.exit()
    else:
        lingua = int(lingua)
except Exception as e:
    decimal_escolhido = False
    raise e('Entrada inválida, digite apenas "1" ou "2"!')
else:
    if lingua == 1:
        transforma_simbolo_decimal = ('.',',')
    elif lingua == 2:
        transforma_simbolo_decimal = (',','.')
    else:
        decimal_escolhido = False
        raise ValueError('Entrada inválida, digite apenas "1" ou "2"!')
finally:

    caminho_arquivos_selecionados = None
#loop para o usuário continuar selecionando arquivos até ele cancelar a janela de seleção
    while decimal_escolhido:
        print("*"*50,"Abrindo janela de seleção dos arquivos...",sep='\n')
        root = tk.Tk()
        root.withdraw()
        filetypes = [("RPT Files", "*.rpt"), ("Arquivos de Texto", "*.txt")]
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
            saida_selecionada = input('Deseja a saída como:\n(1) um arquivo GERAL completo para cada relatorio em CSV\n' + \
                                        '(2) dois arquivos de TRECHOS e de NÓS para cada relatório em CSV\n' + \
                                            '(3) um arquivo GERAL completo + dois arquivos de TRECHOS e de NÓS para cada relatório em CSV\n' + \
                                            '(4) planilha GERAL completa + planiha de TRECHOS e de NÓS para cada relatório em uma pasta Excel\n\t').strip()
            if saida_selecionada == '':
                print('Fechando programa...')
                sys.exit()
            else:
                saida_selecionada = int(saida_selecionada)
        except Exception as e:
            raise e('Entrada inválida, digite apenas "1", "2", "3" ou "4"!')
        else:
            bool_arquivo0 = False
            bool_arquivo12 = False
            bool_arquivo_xlsx = False
            if (saida_selecionada == 1) | (saida_selecionada == 3):
                bool_arquivo0 = True
            if (saida_selecionada == 2) | (saida_selecionada == 3):
                bool_arquivo12 = True
            if saida_selecionada == 4:
                bool_arquivo_xlsx = True
            if saida_selecionada not in range(1,5):
                raise ValueError('Entrada inválida, digite apenas "1", "2", "3" ou "4"!')
        finally:

#seleciona caminho dos arquivos gerados e abre cada arquivo selecionado pelo usuário para gerar
            print("Abrindo janela de salvamento dos novos arquivos...")
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
                list_arquivo_csv = []
                for linha in final0:
                    linha_csv = ""
                    for palavra in linha:
                        linha_csv = linha_csv + palavra + ";"
                    list_arquivo_csv.append(linha_csv[:-1])

#criando arrays com índices das linhas onde os dados das tabelas começam e terminam no relatório não tratado
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
                
                tabela_trecho_no.reset_index(drop=True,inplace=True)
                tabela_resultado_no.reset_index(drop=True,inplace=True)
                tabela_resultado_trecho.reset_index(drop=True,inplace=True)

                tabela_trecho = tabela_trecho_no.merge(tabela_resultado_trecho, on=tabela_trecho_no.columns[0], how='left')
                tabela_no = tabela_resultado_no.copy()

#compilando as três tabelas em uma tabela geral maior
                tabela_relatorio_completo = tabela_trecho_no.copy()
                consumo = [tabela_resultado_no.columns[0],tabela_resultado_no.columns[1]]
                carga_hidraulica = [tabela_resultado_no.columns[0],tabela_resultado_no.columns[2]]
                pressao = [tabela_resultado_no.columns[0],tabela_resultado_no.columns[3]]
                tabela_resultado_trecho_sem_estado = tabela_resultado_trecho.columns[tabela_resultado_trecho.shape[1]-1]

                consumo = tabela_resultado_no[consumo].copy()
                carga_hidraulica = tabela_resultado_no[carga_hidraulica].copy()
                pressao = tabela_resultado_no[pressao].copy()
                tabela_resultado_trecho_sem_estado = tabela_resultado_trecho.drop(tabela_resultado_trecho_sem_estado,axis=1)

                consumo_inicio = consumo.copy().rename(columns={consumo.columns[0]: tabela_relatorio_completo.columns[1]})
                carga_hidraulica_inicio = carga_hidraulica.copy().rename(columns={carga_hidraulica.columns[0]: tabela_relatorio_completo.columns[1]})
                pressao_inicio = pressao.copy().rename(columns={pressao.columns[0]: tabela_relatorio_completo.columns[1]})
                consumo_fim = consumo.copy().rename(columns={consumo.columns[0]: tabela_relatorio_completo.columns[2]})
                carga_hidraulica_fim = carga_hidraulica.copy().rename(columns={carga_hidraulica.columns[0]: tabela_relatorio_completo.columns[2]})
                pressao_fim = pressao.copy().rename(columns={pressao.columns[0]: tabela_relatorio_completo.columns[2]})
                
                tabela_relatorio_completo = tabela_relatorio_completo.merge(consumo_inicio, on=consumo_inicio.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Consumo Início ' + consumo_inicio.columns[1][-5:]},inplace=True)
                tabela_relatorio_completo = tabela_relatorio_completo.merge(consumo_fim, on=consumo_fim.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Consumo Fim ' + consumo_fim.columns[1][-5:]},inplace=True)
                tabela_relatorio_completo = tabela_relatorio_completo.merge(carga_hidraulica_inicio, on=carga_hidraulica_inicio.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Carga Hidráulica Início (m)'},inplace=True)
                tabela_relatorio_completo = tabela_relatorio_completo.merge(carga_hidraulica_fim, on=carga_hidraulica_fim.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Carga Hidráulica Fim (m)'},inplace=True)
                tabela_relatorio_completo = tabela_relatorio_completo.merge(pressao_inicio, on=pressao_inicio.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Pressão Início (m)'},inplace=True)
                tabela_relatorio_completo = tabela_relatorio_completo.merge(pressao_fim, on=pressao_fim.columns[0], how='left')
                tabela_relatorio_completo.rename(columns={tabela_relatorio_completo.columns[-1]: 'Pressão Fim (m)'},inplace=True)

                tabela_relatorio_completo = tabela_relatorio_completo.merge(tabela_resultado_trecho_sem_estado, on=tabela_resultado_trecho_sem_estado.columns[0], how='left')

#string de opções na visualização rápida
                str_opcoes_visualizacao_rapida = ''
                list_opcoes_visualizacao_rapida = []

#salvando arquivo (0)
                if bool_arquivo0:
                    arquivo_saida0 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(0).csv'
                    tabela_relatorio_completo.to_csv(arquivo_saida0, index=False, sep=';')
                    print('Relatório geral completo >> ' + arquivo_saida0)
                    str_opcoes_visualizacao_rapida = str_opcoes_visualizacao_rapida + '\t\t(0) Relatório geral completo\n'
                    list_opcoes_visualizacao_rapida.append(0)

#salvando arquivos (1) e (2)
                if bool_arquivo12:
                    arquivo_saida1 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(1).csv'
                    arquivo_saida2 = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '(2).csv'
                    tabela_trecho.to_csv(arquivo_saida1, index=False, sep=';')
                    tabela_no.to_csv(arquivo_saida2, index=False, sep=';')
                    print('Tabela Resultados dos Trechos >> ' + arquivo_saida1)
                    print('Tabela Resultados dos Nós >> ' + arquivo_saida2)
                    str_opcoes_visualizacao_rapida = str_opcoes_visualizacao_rapida + '\t\t(1) Tabela Resultados dos Trechos\n\t\t(2) Tabela Resultados dos Nós\n'
                    list_opcoes_visualizacao_rapida.extend([1,2])

#salvando arquivo xlsx
                if bool_arquivo_xlsx:
                    arquivo_saida_xlsx = pasta_selecionada + '/' + \
                                        arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4] + '.xlsx'
                    excel_writer = pd.ExcelWriter(arquivo_saida_xlsx, engine='xlsxwriter')
                    tabela_relatorio_completo.to_excel(excel_writer, sheet_name='Relatório Completo', index=False)
                    tabela_trecho.to_excel(excel_writer, sheet_name='Relatório - Trechos', index=False)
                    tabela_no.to_excel(excel_writer, sheet_name='Relatório - Nós', index=False)
                    excel_writer._save()

#visualizar tabelas no terminal temporariamente
                def continuar_visualizacao_rapida():
                    tecla = keyboard.read_event()
                    if tecla.event_type == keyboard.KEY_DOWN and tecla.name == 'esc':
                        print(f'\tSalvamento do(s) arquivo(s) {arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):]} concluído\n')
                        return (False, tecla.name)
                    else:
                        return (True, tecla.name)

                while True:
                    print(f'\tVisualização Rápida de {arquivo_selecionado[(len(caminho_arquivos_selecionados)+1):-4]}:\n' + \
                                        str_opcoes_visualizacao_rapida + \
                                        '\tPressione ESC para sair da visualização rápida')
                    continuar, tecla = continuar_visualizacao_rapida()
                    if not continuar:
                        break
                    else:
                        print('\t\t' + tecla)
                    try:
                        tabela_desejada = int(tecla)
                    except Exception as e:
                        print('\tEntrada inválida!')
                        continue
                    else:
                        if tabela_desejada not in list_opcoes_visualizacao_rapida:
                            print(f'\tEntrada inválida, digite um valor entre {list_opcoes_visualizacao_rapida}!')
                            continue
                        elif tabela_desejada == 0:
                            print('\t\t\tRelatório geral completo', tabela_relatorio_completo.head(11), \
                                    '\nColunas do relatório geral completo:', \
                                    pd.Series(tabela_relatorio_completo.columns.tolist()), sep='\n')
                        elif tabela_desejada == 1:
                            print('\t\t\tTabela Resultados dos Trechos', tabela_trecho.head(11), sep='\n')
                        elif tabela_desejada == 2:
                            print('\t\t\tTabela Resultados dos Nós', tabela_no.head(11), sep='\n')
                    finally:
                        print('\tPressione qualquer tecla para continuar na visualização rápida (ESC para sair)')
                        continuar, tecla = continuar_visualizacao_rapida()
                    if continuar:
                        continue
                    else:
                        break

#aviso ao usuário que o arquivo selecionado será fechado
        print("-"*10 + "Seleção concluída!" + "-"*10 + "\n")

