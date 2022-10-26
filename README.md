# ExtratorCadernosProcessosTST
Extrator elaborado em Python para obtenção das informações dos processos dos cadernos da última semana.

# Descrição:

Dado o link do tribunal abaixo, capture:

• Baixar os cadernos do TST da última semana

• Extrair os números de processo de cada caderno

• Gerar planilhas de saída com todos os números de processos
separados por dia da semana

o Ex. TST 13/10/2022.xlsx

• Caso um processo apareça repetido em mais de um dia, gerar
relatório de duplicatas com os respectivos processos e suas datas.

Link do tribunal: https://dejt.jt.jus.br/dejt/f/n/diariocon

# ChromeDriver

Baixar a versão compatível com o navegador utilizado (https://chromedriver.chromium.org/downloads) - baixar a mais estável e recente.

# Instrução de uso

Fazer o download do diretório, extraindo-o e executando o arquivo extrator.exe.

Os arquivos, após o término do processo, estarão em uma pasta com identificador do dia e hora da extração.

# Passos e etapas realizados neste processo

## Etapa de download dos pdfs

• Inicialização do procedimento com a abertura do browser na página do tribunal e busca pelos campos de pesquisa (aqui utilizando `Selenium` | `WebDriver` e buscando por XPATH e ClassName)

• Limpeza dos dados inseridos nos campos e inserção das datas e do tipo de documento buscado (TST)

• Mapeamento da quantidade de documentos disponíveis para download (aqui um ponto importante para uma versão futura seria controlar a quantidade páginas caso existam mais de 30 documentos disponíveis, haja visto o limite imposto pelo buscador)

• Download dos arquivos para um diretório criado previamente

## Etapa de pesquisa por termos

• Busca por uma string `r"\nProcesso Nº.*.[0-9]\n"` como comparação em todos os documentos, página a página (usando aqui `PyPDF2`)

• Armazenamento em uma lista do processo encontrado, página e caderno

## Etapa de export

• Tratamento das listas contendo os dados em forma de `DataFrame` (substituindo termos, ajuste de número de página e ordenação)

• Extração para .xlsx em um diretório próprio, separando cada arquivo por data

• Verificação dos processos duplicados em mais de um dia e export em um arquivo separado com número do processo, página e caderno

Demais comentários estão ao longo do script.

# Conversão para .exe

`cx_Freeze`

# Dificuldades e sugestões futuras

• Busquei elaborar um script simples e limpo, com o intuito de ser prático e legível, no menor tempo possível

• Para versões futuras, procuraria:

  -> Não limitar a busca à semana anterior, mas um período flexível
  
  -> Implementar a varrição em várias páginas para download
  
  -> Otimizar o tempo de processamento com multithreads
  
  -> Armazenar os dados em algum banco de dados para consulta
  
  -> Elaborar uma interface gráfica amigável e profissional
  
  -> Garantir a execução em outros OS (usando Docker)
  
  -> Inserir etapas de tratamento de erros e processar testes de verificação para melhorar a robustez


