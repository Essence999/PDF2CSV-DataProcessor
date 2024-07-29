# Classe para modelar o DataFrame.
class DataFrameModel():
    def __init__(self):
        self.main_table = {
            'data_pregao': [], 'operacao': [], 'titulo': [],
            'quantidade_total': [], 'total_operacao': []
        }
        self.financial_summary = {
            'taxa_liq': [], 'taxa_registro': [],
            'taxa_termo': [], 'taxa_ana': [], 'emolumentos': [],
            'corretagem': [], 'iss': [], 'irrf': [],
        }

    def get_dataframemodel(self):
        dfmodel = self.fill_model_columns()
        return dfmodel

    def fill_model_columns(self):
        temp_model = dict(self.main_table, **self.financial_summary)

        max_length_col = max(len(v) for v in temp_model.values())

        for key in temp_model:
            current_length = len(temp_model[key])
            if current_length < max_length_col:
                temp_model[key].extend(
                    [temp_model[key][0]] * (max_length_col - current_length))

        return temp_model
