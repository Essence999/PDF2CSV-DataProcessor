import sys
import pymupdf
from logging import debug, error, info


# Função para chamar o minerador de dados do PDF.
def run_data_miner(pdf_path):
    data_miner = DataMiner(pdf_path)
    pdf_unstructured_data_list = data_miner.extract_data()
    return pdf_unstructured_data_list


# Classe para minerar dados do PDF.
class DataMiner():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_text = []
        self.pdf_data = []
        self.pdf_list = []

    # Inicia o processo de mineração de dados.
    def extract_data(self):
        debug("Iniciando extração de dados do PDF.")
        self.pdf_text = self.get_pdf_text()
        debug("Texto inicial extraído do PDF.")
        self.remove_header_footer()
        debug("Cabeçalho e rodapé removidos.")

        debug("Verificando em quantas partes o PDF deverá ser dividido.")
        self.divide_pdf()
        debug(f"O PDF será dividido em {len(self.pdf_list)}.")

        info("Extração de dados do PDF finalizada.")
        return self.pdf_list

    # Extrai o texto do PDF.
    def get_pdf_text(self):
        doc = pymupdf.open(self.pdf_path)

        if doc.page_count < 1:
            error("O arquivo PDF não tem páginas.")
            sys.exit(1)

        temp_pdf_text = []
        for page_num, page in enumerate(doc):
            text = page.get_text()

            temp_pdf_text.append(text)
            debug(f"Página {page_num + 1} processada.")

        return temp_pdf_text

    # Remove o cabeçalho e rodapé de todas páginas do PDF.
    def remove_header_footer(self):
        for page_num, page_text in enumerate(self.pdf_text):
            # Pega apenas o que está entre o cabeçalho e o rodapé.
            if page_text.find('Data pregão') != -1:
                page_text = page_text[page_text.find('Data pregão'):]
            if page_text.find('Resumo dos Negócios') != -1:
                page_text = page_text[page_text.find('Resumo dos Negócios'):]

            page_text = page_text.split(
                '\nXP INVESTIMENTOS CORRETORA DE CÂMBIO, TÍTULOS E VALORES MOBILIÁRIOS S.A.')
            page_text = page_text[0]
            # Divide o texto em linhas, e pega apenas o que não é espaço.
            page_text_split = page_text.split('\n')
            page_text_split = [line for line in page_text_split if line != ' ']
            # Junta as linhas em uma só.
            page_text = '\n'.join(page_text_split)

            debug(f"H/F da página {page_num + 1} removidos.")
            self.pdf_data.append(page_text)

    # Divide o PDF em partes, baseado em qunatos Resumos dos Negócios existem.
    def divide_pdf(self):
        pdf_data = self.pdf_data
        temp_pdf_list = []

        # Itera sobre o texto do PDF.
        for page_text in pdf_data:
            temp_pdf_list.append(page_text)
            if page_text.startswith('Resumo dos Negócios'):
                # Se achar o Resumo dos Negócios, adiciona a lista de PDFs.
                self.pdf_list.append(temp_pdf_list)
                # E reseta a lista temporária.
                temp_pdf_list = []
