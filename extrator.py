# import de bibliotecas necessárias
from selenium import webdriver
import sys
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd 
import time 
from datetime import datetime
from datetime import date
from datetime import timedelta
import fnmatch
import PyPDF2
import re
import glob

#criação do diretório para alocação dos documentos
current_path=os.path.dirname(os.path.abspath(__file__))
current_dir_name = current_path + "\\" + datetime.\
    today().strftime('%Y-%m-%d_%H-%M-%S')
os.mkdir(current_dir_name)

#opções do browser (set de diretório e permissão para múltiplos downloads)
chrome_options = webdriver.ChromeOptions()
prefs = {'profile.default_content_setting_values.automatic_downloads': 1,
"download.default_directory" : current_dir_name}
chrome_options.add_experimental_option("prefs", prefs)

#criação da classe que irá executar o processo
class ExtractData():

    #construtor
    def __init__(self):
        self.erro_final = 'ERRO_DESCONHECIDO_001'

    #função para download dos documentos
    def DownloadFiles():
        print("Iniciando download dos arquivos")
        print("Diretório: ",current_dir_name)
        #iniciando o browser
        driver = webdriver.Chrome(options = \
            chrome_options,executable_path=current_path+'/chromedriver')
        driver.get("https://dejt.jt.jus.br/dejt/f/n/diariocon")

        #cálculo das datas para inserção nos filtros
        last_week = datetime.today() - timedelta(days=8)
        last_week_date = last_week.strftime("%d/%m/%Y")

        #tempo de espera
        time.sleep(10)
        #buscando o elemento de filtro (data inicial)
        element_data_ini=WebDriverWait(driver, 10).\
            until(EC.element_to_be_clickable((By.XPATH, \
                "//*[@id='corpo:formulario:dataIni']")))
        element_data_ini.clear() #limpando argumentos já existentes
        element_data_ini.send_keys(last_week_date) #inserindo valores
        #buscando o elemento de filtro (data final)
        element_data_fim=WebDriverWait(driver, 10).\
            until(EC.element_to_be_clickable((By.XPATH, \
                "//*[@id='corpo:formulario:dataFim']")))
        element_data_fim.clear() #limpando argumentos já existentes
        element_data_fim.send_keys(datetime.today().\
            strftime("%d/%m/%Y")) #inserindo valores
        #selecionando o tipo de documento (no caso, TST)
        element_orgao=WebDriverWait(driver, 10).\
            until(EC.element_to_be_clickable((By.XPATH, \
                "//*[@id='corpo:formulario:tribunal']")))
        element_orgao.click()
        #enviando string de comparação para seleção
        element_orgao.send_keys("T")
        element_orgao.click()
        #clicando no botão para pesquisar
        element_search=WebDriverWait(driver, 10).\
            until(EC.element_to_be_clickable((By.XPATH,\
                 "//*[@id='corpo:formulario:botaoAcaoPesquisar']")))
        element_search.click()
        time.sleep(10)
        download_size=len(driver.find_elements(\
            By.CLASS_NAME, "linhapar"))\
            +len(driver.find_elements(By.CLASS_NAME, "linhaimpar"))
        print("Total de documentos: ",download_size)
        check_begin_download = datetime.now()
        for i in range(0,download_size):
            driver.execute_script(\
                "document.getElementsByClassName('bt af_commandButton')\
                    ["+str(i)+"].click()")
            #definindo um tempo de espera entre cliques para download
            time.sleep(2)
        #contando o número de arquivos já baixados
        pdf_files_count = len(fnmatch.filter(os.listdir(\
            current_dir_name), '*.pdf'))
        #loop para contagem de arquivos pdf já baixados com o intuito de
        #fechar o navegador assim que o processo estiver concluído
        check_time = datetime.now()
        #colocando um filtro de tempo caso haja algum erro e o número de 
        #documentos baixados seja diferente do número de documentos disponíveis
        #para download
        delta_time_download = (check_time-check_begin_download).total_seconds()
        while (pdf_files_count<download_size and delta_time_download//60<10):
            time.sleep(5)
            pdf_files_count = len(fnmatch.filter(os.listdir(\
                current_dir_name), '*.pdf'))
            check_time = datetime.now()
            delta_time_download = (check_time-check_begin_download).total_seconds()
        else:
            driver.quit()

    #função para encontrar os números dos processos dentro dos cadernos
    def FindInstances():
        #definindo o diretório de busca
        file_list = glob.glob(current_dir_name+"\\"+"*.pdf")
        failed_pages = []
        
        #definindo string de comparação
        #aqui usando o padrão de quebra de linha antes e depois
        #contendo string Processo Nº e fim de string com um inteiro
        #entre 0 e 9
        String = r"\nProcesso Nº.*.[0-9]\n"
        cont=0
        occurences = []
        #varrendo os arquivos .pdf no diretório
        for j in file_list:
            cont+=1
            print("Abrindo documento: \n"+str(j)+"\n")
            #progresso de processo
            print("Progresso: {:.0%}".format((cont/len(file_list))))
            print("\n -----")
            obj = PyPDF2.PdfFileReader(j)
            #calculando número de páginas
            NumPages = obj.getNumPages()
            failed_pages = []
            #extraindo por página de documento as ocorrências
            for i in range(0, NumPages):
                PageObj = obj.getPage(i)
                try:
                    Text = PageObj.extractText()
                except:
                    Text = ''
                    failed_pages.append(i)
                    pass
                #utilizando findall para encontrar todas as ocorrências da string
                #de comparação na página
                ResSearch = re.findall(String, Text)
                if ResSearch!=None:
                    for k in range(0,len(ResSearch)):
                        #inserindo os valores de número de processo
                        #página e número do caderno em uma lista
                        occurences.append(str(ResSearch[k])+","+\
                            str(i)+","+j.split("__")[-1].\
                                split(".")[0].split(" ")[0])
        #retornando para uso na função de export
        return occurences

    #função para exportar os dados em arquivos .xlsx
    def ExportXLSX(array_occurences):
        #gerando uma cópia da matriz
        array_occurences_copy=array_occurences.copy()
        #aplicando split em vírgula para separar as colunas de interesse
        array_occurences_ = [line.split(",") for line in array_occurences_copy]
        columns = ["Processo", "Página", "Caderno"]
        #criando o DataFrame com as colunas Processo, Página e Caderno
        df = pd.DataFrame(data=array_occurences_, columns=columns)
        #substituindo caracteres e deixando somente os números dos processos
        df.replace({'\n': '','Processo Nº ':''}, regex=True, inplace=True)
        #ajustando o número da página onde há a ocorrência do processo
        df['Página'] = df['Página'].astype(int)
        df['Página']= df['Página']+1
        #extraindo datas (cadernos) únicas para nomes dos arquivos
        unique_dates = df['Caderno'].unique()
        #criação do diretório de exportação dos arquivos .xlsx
        xlsx_dir_name =  current_dir_name+"\\xlsx_files"
        os.mkdir(xlsx_dir_name)
        #exportando cada conjunto de processos em um arquivo com a data
        for i in range(0,len(unique_dates)):
            df_export = df[df['Caderno']==unique_dates[i]]
            df_export = df_export[['Processo','Página']]
            df_export.to_excel(xlsx_dir_name+"\\"+"TST "+unique_dates[i]+".xlsx",
            sheet_name='Dados',index=False)
        #calculando agora os processos que aparecem em mais de um dia
        #selecionando as duplicadas de processos inicialmente
        df_duplicated = df[df.duplicated(subset=['Processo'], keep=False)]
        #ordenando por Processo, depois Caderno, Depois Página
        df_duplicated=df_duplicated.sort_values(by=['Processo', 'Caderno', 'Página'])
        #encontrando os números de processos únicos
        duplicated_processos = df_duplicated['Processo'].unique()
        df_duplicated_output=pd.DataFrame(columns=columns)
        #varrendo cada processo e verificando se o mesmo ocorre em mais de um dia
        #caso sim, colocar estas linhas em um DataFrame
        for i in range(0,len(duplicated_processos)):
            df_aux = df_duplicated[df_duplicated['Processo']==duplicated_processos[i]]
            if len(df_aux['Caderno'].unique())>1:
                df_duplicated_output=pd.concat([df_duplicated_output,df_aux])
        #exportando o DataFrame de processos duplicados
        df_duplicated_output.to_excel(xlsx_dir_name+"\\"+"Duplicados"+".xlsx",
            sheet_name='Dados',index=False)

#processo
print("Início da extração: ",datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
begin_time_stamp = datetime.now()
ExtractData.DownloadFiles()
print("Início do processamento: ",datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
array_occurences=ExtractData.FindInstances()
ExtractData.ExportXLSX(array_occurences)
print("Fim do processamento: ",datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
end_time_stamp = datetime.now()
delta_time = (end_time_stamp-begin_time_stamp).total_seconds()
print("Tempo decorrido: {:.0f} minuto(s) e {:.0f} segundos.".\
    format(delta_time//60,delta_time%60))