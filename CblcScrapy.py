import requests

class Downloaders():
    EMPRESTIMOS_REGISTRADOS_URL = 'http://www.cblc.com.br/cblc/consultas/Arquivos/DBTCER9999.txt'
    POSICAO_EM_ABERTO_URL = 'http://www.cblc.com.br/cblc/consultas/Arquivos/DBTC'
    EMP_REG_PATH = 'z:/adm/dados/cblc/'
    DATA_MOVIMENTO = ''

    def remove_header_and_footer(self, arquivo):
        # Remove header e footer
        arquivo.pop(len(arquivo) - 1)
        arquivo.pop(0)

    def valida_integridade_arquivo(self, arquivo, header_padrao, qtde_linhas_pos, footer_padrao, dt_geracao_header_pos, dt_geracao_footer_pos, len_linha, verboso=False):
        # Valida header
        header_encontrado = arquivo[0][:len(header_padrao)]
        if header_encontrado != header_padrao:
            raise ValueError('Começo do header não confere com o padrão: "{}". Padrão encontrado: "{}"'.format(header_padrao, header_encontrado))
        elif verboso:
            print('Header ok.')
        
        # Valida arquivo completo
        if (arquivo[len(arquivo) -1][:2] != str(99)):
            raise ValueError('Arquivo está incompleto. Era esperado ({}) e foi encontrado ({})!'.format(str(99), arquivo[len(arquivo) -1][:2]))
        elif verboso:
            print('Arquivo completo.')

        # Valida linhas do arquivo a partir do footer
        qtde_linhas_encontrado = len(arquivo)
        last_line = qtde_linhas_encontrado - 1
        qtde_linhas_padrao = int(arquivo[last_line][qtde_linhas_pos[0]:qtde_linhas_pos[1]])
        if qtde_linhas_encontrado != qtde_linhas_padrao:
            raise ValueError('Qtde de linhas encontradas ({}) diferente do que diz no footer ({}).'.format(qtde_linhas_encontrado,qtde_linhas_padrao))
        elif verboso:
            print('Qtde de linhas ok.')

        # Valida footer
        footer_encondrado = arquivo[last_line][:len(footer_padrao)]
        if footer_encondrado != footer_padrao:
            raise ValueError('Começo do footer não confere com o padrão: "{}". Padrão encontrado: "{}"'.format(footer_padrao, footer_encondrado))
        elif verboso:
            print('Footer ok.')

        # Valida data de geração do arquivo entre o header e o footer
        data_header = arquivo[0][dt_geracao_header_pos[0]:dt_geracao_header_pos[1]]
        data_footer = arquivo[last_line][dt_geracao_footer_pos[0]:dt_geracao_footer_pos[1]]
        if data_footer != data_header:
            raise ValueError('Data do header ({}) diferente do footer ({})!'. format(data_header, data_footer))
        elif verboso:
            print('Data do header e footer ok.')

        # Valida quantidade de caracteres em todas as linhas
        cur_lin = 1
        for emp in arquivo:
            if len(emp) != len_linha:
                raise ValueError('Linha {} do arquivo está com a quantidade de caracteres ({}) diferente de {}!'.format(str(cur_lin), str(len(emp)), str(len_linha)))
            cur_lin += 1
        if verboso:
            print('Todas as linhas estão ok.')

    def valida_integridade_emprestimos_registrados(self, emprestimos, verboso=False):
        header_padrao = '00DBTCER9999BVMF    9999'
        qtde_linhas_pos = (32, 40)
        footer_padrao = '99DBTCER9999BVMF    9999'
        dt_geracao_header_pos = (24, 32)
        dt_geracao_footer_pos = (24, 32)
        len_linha = 161

        self.valida_integridade_arquivo(emprestimos, header_padrao, qtde_linhas_pos, footer_padrao, dt_geracao_header_pos, dt_geracao_footer_pos, len_linha, verboso)

    def get_arquivo(self, url, remove_CR=True):
        # Pega o arquivo da CBLC
        request = requests.get(url)
        if (request.status_code != 200):
            raise requests.RequestException('Não encontrou a página "{}". Status da requisição: "{}"'.format(url, str(request.status_code)))

        arquivo = request.text.split('\n')
        if remove_CR:
            arquivo.pop(len(arquivo) - 1)  # Remove CR

        return arquivo

    def get_emprestimos_registrados(self, verboso=False):
        if verboso:
            print('\n-----Início da extração dos empréstimos registrados!-----')

        # Pega o arquivo da CBLC
        URL = self.EMPRESTIMOS_REGISTRADOS_URL
        emprestimos = self.get_arquivo(URL, True)
        if verboso:
            print('Emprestimos registrados extraídos da CBLC.')

        # Valida o arquivo
        self.valida_integridade_emprestimos_registrados(emprestimos, verboso)
        if verboso:
            print('Arquivo dos emprestimos está íntegro.')

        # Pega a data do movimento
        self.DATA_MOVIMENTO = emprestimos[0][32:40]

        # Remove header and footer
        self.remove_header_and_footer(emprestimos)

        if verboso:
            print('Emprestimos registrados extraídos com sucesso com a data de {}!'.format(self.DATA_MOVIMENTO))
            print('-----Fim da extração dos empréstimos registrados!-----')

        return emprestimos

    def valida_integridade_posicao_em_aberto(self, posicoes, verboso=False):
        # Fonte: http://bvmf.bmfbovespa.com.br/BancoTitulosBTC/download/DBTC9999.pdf
        header_padrao = '00DBTC9999CBLC    9999'
        qtde_linhas_pos = (30, 38)
        footer_padrao = '99DBTC9999CBLC    9999'
        dt_geracao_header_pos = (22, 30)
        dt_geracao_footer_pos = (22, 30)
        len_linha = 251

        self.valida_integridade_arquivo(posicoes, header_padrao, qtde_linhas_pos, footer_padrao, dt_geracao_header_pos, dt_geracao_footer_pos, len_linha, verboso)

    def get_posicao_em_aberto(self, data, verboso=False):
        if verboso:
            print('\n-----Início da extração das posições em aberto!-----')

        # Valida a data
        if data == '' or len(data) != 8:
            raise AttributeError('Data inválida!')

        # Pega o arquivo da CBLC
        URL = self.POSICAO_EM_ABERTO_URL + data + '.dat'
        posicoes = self.get_arquivo(URL, True)

        if verboso:
            print('Posições em Aberto extraídas da CBLC.')

        # Valida o arquivo
        self.valida_integridade_posicao_em_aberto(posicoes, verboso)

        # Remove header and footer
        self.remove_header_and_footer(posicoes)

        if verboso:
            print('Posicao em aberto extraídos com sucesso com a data de {}!'.format(data))
            print('-----Fim da extração das posições em aberto!-----\n')

        return posicoes


if __name__ == '__main__':
    try:
        down = Downloaders()
        down.get_emprestimos_registrados()
        down.get_posicao_em_aberto(down.DATA_MOVIMENTO)
    except Exception as e:
        print(e)
