import sys
from tkinter import filedialog
from logging import warning, info


# Função para selecionar o arquivo PDF.
def select_pdf_file():
    try:
        info("Selecione um arquivo PDF.")
        pdf_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")])
        info("PATH: %s", pdf_path)

        if pdf_path == "":
            raise FileNotFoundError("Nenhum arquivo foi selecionado.")
    except FileNotFoundError as e:
        warning(e)
        sys.exit(1)
    else:
        info("Arquivo selecionado com sucesso.")
        return pdf_path


if __name__ == '__main__':
    select_pdf_file()
