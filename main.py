from modules.config_logging import setup_logging
from modules.pdf_acess import select_pdf_file
from modules.data_miner import run_data_miner
from modules.data_processor import run_data_processor
from modules.csv_generator import run_csv_generator

# Configura as mensagens do logger.
logger = setup_logging()


# Função principal para rodar o sistema.
def run_main():
    # Selecionar o arquivo PDF.
    pdf_path = select_pdf_file()

    # Minerar os dados do PDF e retorna uma lista com as partes do PDF.
    pdf_data_list = run_data_miner(pdf_path)

    dfmodel_list = []
    # Processar e estruturar os dados do PDF por partes.
    logger.info('O PDF possui %s nota(s).', len(pdf_data_list))
    for num, pdf_data in enumerate(pdf_data_list):
        logger.debug('Processando a nota %s do PDF.', num + 1)
        dfmodel = run_data_processor(pdf_data)
        dfmodel_list.append(dfmodel)
    logger.info('Dados processados e estruturados com sucesso.')

    # Gerar o arquivo CSV.
    pdf_name = pdf_path.split('/')[-1].split('.')[0]
    run_csv_generator(dfmodel_list, pdf_name)


if __name__ == '__main__':
    run_main()
