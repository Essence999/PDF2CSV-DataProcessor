import os
from logging import debug, info, error
from datetime import datetime
import pandas as pd


# Função para rodar o gerador de planilha CSV.
def run_csv_generator(dfmodel_list, pdf_name):
    # Gera o DataFrame a partir do modelo ou modelos e concatena-os.
    final_dataframe = DataFrameGenerator(dfmodel_list).df

    # Calcula os valores necessários para a planilha CSV e gera a planilha.
    csv_gen = CSVGenerator(final_dataframe, pdf_name)
    csv_gen.generate_csv()


# Classe para gerar o DataFrame a partir do modelo ou dos modelos.
class DataFrameGenerator():
    def __init__(self, dfmodel_list):
        self.dfmodel_list = dfmodel_list
        self.df = self.create_df()

    # Cria o DataFrame a partir do modelo.
    def create_df(self):
        try:
            debug('Concatenando os DataFrames.')
            df_list = []
            for df_model in self.dfmodel_list:
                df = pd.DataFrame(df_model)
                # Criar coluna de peso para cada nota antes de concatenar.
                self.create_weight_column(df)
                df_list.append(df)
            df = pd.concat(df_list, ignore_index=True)
            debug('DataFrames concatenados.')
        except Exception as e:
            error(f'Erro ao criar DataFrame: {e}')
        else:
            debug('DataFrame criado.')
        return df

    # Cria a coluna de peso no DataFrame para cada nota, antes de concatenar.
    def create_weight_column(self, df):
        index_tot_op = df.columns.get_loc('total_operacao')
        tot_op_sum = df['total_operacao'].sum()
        new_column = df['total_operacao'] / tot_op_sum

        df.insert(loc=index_tot_op + 1,
                  column='peso', value=new_column)

        debug('Coluna de peso adicionada ao DataFrame.')


# Classe para gerar a planilha CSV.
class CSVGenerator():
    def __init__(self, final_df, pdf_name):
        self.final_df = final_df
        self.file_path = f'planilhas geradas/{pdf_name}_{self.get_time()}.csv'

    # Gera a planilha CSV.
    def generate_csv(self):
        debug('Verificando se a pasta "planilhas geradas" existe.')
        self.create_directory()

        debug('Calculando os valores necessários para a planilha CSV.')
        self.calculate_all()

        debug('Gerando planilha CSV.')
        self.final_df.to_csv(self.file_path, index=False,
                             decimal=',', float_format='%.9f', encoding='utf-8')

        info('Planilha gerada com sucesso.')
        info(f'PATH: {self.file_path}')

    # Organiza o DataFrame com cálculos para a geração da planilha CSV.
    def calculate_all(self):
        # Faz o calculo dos impostos, multiplicando-os pelo peso.
        self.actualize_taxes()
        # Atualiza o IRRF no DataFrame com o cálculo.
        self.actualize_irrf()
        # Cria a coluna de custo médio.
        self.create_avg_column()

        debug('Valores calculados para a planilha CSV.')

    # Retorna a data e hora atual.
    def get_time(self):
        time = datetime.now()
        time = time.strftime('%d-%m-%Y_%H-%M-%S')
        return time

    # Cria a pasta "planilhas geradas" se ela não existir.
    def create_directory(self):
        if not os.path.exists('planilhas geradas'):
            os.makedirs('planilhas geradas')
            info('Pasta "planilhas geradas" criada.')
        else:
            debug('Pasta "planilhas geradas" já existe.')

    # Atualiza os impostos no DataFrame.
    def actualize_taxes(self):
        columns = self.final_df.columns.tolist()
        # Pega as colunas de taxas, menos a última.
        taxes_columns = columns[6:-1]

        for col in taxes_columns:
            self.final_df[col] = self.final_df['peso'] * self.final_df[col]

        debug('Taxas atualizadas no DataFrame.')

    # Atualiza o IRRF no DataFrame.
    def actualize_irrf(self):
        # Se a operação for de compra, o IRRF é 0.
        self.final_df.loc[self.final_df['operacao'] == 'C', 'irrf'] = 0

        # Se não houver operações de venda, não há IRRF para calcular.
        if 'V' not in self.final_df['operacao'].values:
            info('Não há operações V para calcular o IRRF.')
            return

        debug('Calculando o IRRF.')
        # Pega as operações de venda e soma os pesos.
        df_v = self.final_df[self.final_df['operacao'] == 'V']
        weight_sum = df_v['peso'].sum()

        # Calcula o IRRF para cada operação de venda.
        # IRRF = peso do título/soma dos pesos dos títulos V * IRRF total da nota
        irrf = df_v['peso'] / weight_sum * df_v['irrf']

        self.final_df.loc[self.final_df['operacao'] == 'V', 'irrf'] = irrf
        debug('IRRF calculado e atualizado no DataFrame.')

    # Cria a coluna de custo médio no DataFrame.
    def create_avg_column(self):
        # Calcula o custo médio.
        def calc_avg(row):
            columns = self.final_df.columns.tolist()
            taxes_columns = columns[6:-1]
            taxes_sum = row[taxes_columns].sum()

            # Se a operação for de compra, o custo médio é o total da
            # operação mais as taxas, dividido pela quantidade total.
            # Se a operação for de venda, o custo médio é o total da
            # operação menos as taxas, dividido pela quantidade total.

            if row['operacao'] == 'C':
                avg_cost = (row['total_operacao'] +
                            taxes_sum) / row['quantidade_total']
            else:
                avg_cost = (row['total_operacao'] -
                            taxes_sum) / row['quantidade_total']
            return round(avg_cost, 2)

        # Adiciona a coluna de custo médio ao DataFrame.
        self.final_df['custo_medio'] = self.final_df.apply(calc_avg, axis=1)
        debug('Custo médio adicionado ao DataFrame.')
