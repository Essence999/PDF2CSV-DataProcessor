# PDF2CSV-DataProcessor
Ferramenta para extração e processamento de dados de notas de corretagem, realizando cálculos específicos e gerando planilhas em formato CSV. Utiliza as bibliotecas Pandas e PyMuPDF.

O arquivo exec.bat inicia o main.py.
Documentação com as descrições e detalhes sobre o funcionamento do sistema

# Arquivo main.py:
Arquivo principal que deve ser executado. Chama todas as funções e módulos do programa para que funcione em ordem e corretamente.

# Pasta modules:
- config_logging: Configura um logger que registra mensagens do sistema, essencial para detectar problemas e monitorar o fluxo de execução. As mensagens mais simples aparecem para o usuário no console, enquanto as mensagens completas aparecem no app.log.
- pdf_acess: Abre uma interface para selecionar o arquivo PDF a ser processado.
- data_miner: Extrai o texto dos dados do PDF selecionado, remove cabeçalhos e rodapés, e organiza suas páginas em partes delimitadas pelos quadros finais.
- data_processor: Processa* e estrutura os dados extraídos de acordo com o modelo de DataFrame.
- dfmodel: Garante que o data_processor preencherá os dados estruturados em um modelo base com as colunas* para o DataFrame.
- csv_generator: Recebe um ou mais modelos de DataFrame e cria um DataFrame único. Realiza os cálculos* solicitados, adiciona as colunas peso e custo_medio e então gera um arquivo CSV.

# *Colunas: data_pregao, operacao, titulo, quantidade_total, total_operacao, taxa_liq, taxa_registro, taxa_termo, taxa_ana, emolumentos, corretagem, iss, irrf.

# *Cálculos:
- Coluna peso = total operação / soma das operações totais
- Cada coluna das taxas (menos IRRF) = taxas * peso
- Atualiza as colunas de IRRF apenas para as operações V = peso do título / soma dos pesos dos títulos V * IRRF total da nota
- Custo médio = Se a operação for de compra, o custo médio é o total da operação mais as taxas, dividido pela quantidade total: (total_operação + taxas) / quantidade_total. Se a operação for de venda, o custo médio é a soma do total da operação menos as taxas, dividido pela quantidade total: (total_operação - taxas) / quantidade total. IRRF não incluso.

# *Regras do processamento de dados para cada parte (delimitada por quadros finais):
1. Pega a data pregão da primeira página e remove os títulos das colunas.
2. Reúne todas as tabelas em um único local, sem textos que interferem na estruturação.
3. Retira os sumários das tabelas, mirando em todas as linhas que seguem o padrão "Quantidade Total: 'número inteiro' Preço Médio: 'número decimal'".
5. Substitui os sumários por um END-POINT, que delimita todas as tabelas de cada título.
6. Adiciona os valores da coluna "C/V", seguindo o padrão de pegar o primeiro C ou V de cada tabela.
7. Multiplica quantidade total por preço médio, resultando em total_operacao.
8. Procede em separar os dados da última página com o quadro final.
9. Remove a tabela "Resumo dos Negócios", do início até o fim das Observações, restando apenas o "Resumo Financeiro".
10. Adquire todos os números decimais da tabela, que devem possuir um padrão imutável, e remove os números irrelevantes.
11. Por fim, adiciona os valores solicitados (taxa liq, taxa registro, taxa termo, taxa ana, emolumentos, corretagem, iss, irrf) e finaliza a estruturação dos dados.

Os arquivos gerados são salvos na pasta "planilhas geradas" com a formatação de nome: {nome_do_PDF_selecionado}_dia-mês-ano_horas-minutos-segundos.csv.

