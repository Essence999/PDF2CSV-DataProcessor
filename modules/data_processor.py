from modules.dfmodel import DataFrameModel
from logging import debug
import re


def run_data_processor(pdf_text):
    debug('Iniciando processamento e estruturação dos dados do PDF.')

    data_processor = PDFDataProcessor(pdf_text)

    df_model = data_processor.process_data()
    debug('Fim do processamento')

    return df_model


# Classe para processar e estruturar o texto extraído do PDF.
class PDFDataProcessor(DataFrameModel):
    def __init__(self, unstructured_data):
        super().__init__()
        self.unstructured_data = unstructured_data
        self.processed_data_text = []

    # Processa os dados, chamando todas as funções necessárias.
    def process_data(self):
        self.set_table_datatime()
        summaries = self.get_all_summaries()
        self.add_summary_data(summaries)
        self.replace_summaries_with_endpoints()
        self.get_all_cv()
        self.set_total_operation()
        self.process_last_page()

        df_model = self.get_dataframemodel()
        return df_model

    # Pega a data do pregão.
    def set_table_datatime(self):
        temp_list = self.unstructured_data[0].split('\n')
        i = temp_list.index('Data pregão')
        datatime = temp_list[i + 1]
        self.main_table['data_pregao'].append(datatime)

        debug(f'Data do pregão: {datatime}')

        self.remove_header()

    # Remove o texto até as colunas da tabela das primeiras páginas.
    def remove_header(self):
        temp_list = []
        last_page = self.unstructured_data[-1]

        for text in self.unstructured_data[:-1]:
            index_word = text.lower().find("d/c")
            text = text[index_word + 4:]
            temp_list.append(text)

        pages = '\n'.join(temp_list)
        self.processed_data_text.append(pages)
        self.processed_data_text.append(last_page)

        debug('Textos removidos.')

    # Pega os sumários de cada título.
    def get_all_summaries(self):
        summaries = []
        data_list = self.processed_data_text[0].split('\n')
        for index in range(len(data_list) - 1, -1, -1):
            if re.search(
                    r'Quantidade Total:\s*([\d\.]+)\s*Preço Médio:\s*([\d,]+)',
                    data_list[index]
            ):
                summaries.append(data_list.pop(index))
        debug('Sumários extraídos.')

        return summaries[::-1]

    # Pega os sumários de cada título e adiciona no DataFrame.
    def add_summary_data(self, summaries):
        # Regex para capturar os grupos de informações
        pattern = r'^(.*?)\s+Quantidade Total:\s*([\d\.]+)\s*Preço Médio:\s*([\d,]+)$'

        def separate_summary(summary):
            match = re.match(pattern, summary)
            if match:
                title = match.group(1).strip()
                tot_qt = int(match.group(2).replace('.', ''))
                avg = float(match.group(3).replace('.', '').replace(',', '.'))
            return [title, tot_qt, avg]

        summaries = [separate_summary(summary) for summary in summaries]

        for summary in summaries:
            self.main_table['titulo'].append(summary[0])
            self.main_table['quantidade_total'].append(summary[1])
            # Coloca o valor do preço médio para depois calcular o total da operação.
            self.main_table['total_operacao'].append(summary[2])

        debug('Títulos e quantidades totais adicionados ao DataFrame.')
        return summaries

    # Substitui os sumários pelos endpoints.
    def replace_summaries_with_endpoints(self):
        data_list = self.processed_data_text[0].split('\n')

        for index, item in enumerate(data_list):
            if re.search(r'Quantidade Total:\s*([\d\.]+)\s*Preço Médio:\s*([\d,]+)', item):
                data_list[index] = 'END-POINT'

        self.processed_data_text[0] = '\n'.join(data_list)
        debug('Sumários substituídos por END-POINT.')

    # Separa os dados por endpoint e pega os valores de C e V.
    def get_all_cv(self):
        data_text = self.processed_data_text[0]
        data_list = data_text.split('END-POINT\n')
        data_list = [data.split('\n') for data in data_list]
        data_list = [data[:-1] for data in data_list]

        for data in data_list:
            c_v = False
            for item in data:
                # Se achar C ou V, adiciona no DataFrame.
                if c_v is False:
                    if item[0] in {'C', 'V'}:
                        if item in {'C', 'V'} or item.startswith(('C ', 'V ')):
                            self.main_table['operacao'].append(item[0])
                            c_v = True
                            break

        debug('Valores de C/V extraídos.')

    # Multiplica quantidade total pelo preço médio e adiciona no DataFrameModel.
    def set_total_operation(self):
        for i, avg in enumerate(self.main_table['total_operacao']):
            total_op = self.main_table['quantidade_total'][i] * avg
            self.main_table['total_operacao'][i] = total_op

        debug('Valores totais das operações calculados.')

    # Funções abaixo vão processar a última página do PDF.
    def process_last_page(self):
        last_page = self.processed_data_text[1]
        index = last_page.find('Valor das operações')
        # Remove a tabela resumo dos negócios.
        last_page = last_page[index + 20:]
        # Remove de Observações até o final.
        index = last_page.find('\n(*) Observações')
        last_page = last_page[:index]
        last_page = last_page.split('\n')

        number_list = []

        # Pega os valores da última página, da tabela Resumo Financeiro.
        for item in last_page:
            if item.find(',') != -1:
                number_list.append(item)

        # Remove os valores que não são necessários.
        number_list = number_list[1:11]
        number_list.pop(6)
        number_list.pop(2)

        for key, number in zip(self.financial_summary.keys(), number_list):
            self.financial_summary[key].append(
                float(number.replace('.', '').replace(',', '.')))

        debug('Dados da última página processados.')
