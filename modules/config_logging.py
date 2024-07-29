from logging import basicConfig, getLogger, DEBUG, INFO, FileHandler, StreamHandler, Formatter
import sys


def setup_logging():
    logger = getLogger(__name__)

    file_handler = FileHandler('app.log', 'w', encoding='utf-8')
    file_handler.setLevel(DEBUG)
    formarter_file_handler = Formatter(
        '[%(levelname)s] - %(asctime)s - %(message)s')
    file_handler.setFormatter(formarter_file_handler)

    stream_handler = StreamHandler()
    stream_handler.setLevel(INFO)

    basicConfig(level=DEBUG,
                format='[%(levelname)s] - %(asctime)s - %(message)s',
                datefmt='%H:%M:%S', encoding='utf-8',
                handlers=[file_handler, stream_handler])


# Configura o hook de exceção para registrar exceções não capturadas.

    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        logger.critical("Ocorreu um erro inesperado", exc_info=(
            exc_type, exc_value, exc_traceback))

    # Substitui o hook de exceção padrão
    sys.excepthook = log_unhandled_exception

    return logger
