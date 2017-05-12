import requests
import shutil
import struct

temp_path = 'C:/example/'
dest_path = 'Z:\Temp\\'  # Change to Z:\Adm\Dados\CblcPos\\


def move_to_folder(filename):
    print("Mandou mover!")
    shutil.copy(temp_path + filename + '.temp', dest_path + filename)


def parse_temp(filename):
    # The first two bytes identify the registry kind
    kind_mask = '2s'

    # Each registry kind has its own struct mask, which will be used to parse
    # byte objects by width. This approach makes it easy to change fields if needed.
    registry_masks = [
        '2s6s4s8s4s8s8s120s',  # 00 = header
        '2s20s30s10s11s20s7s7s7s7s7s7s25s',  # 01 = one day
        '2s20s30s10s11s20s7s7s53s',  # 02 = three days
        '2s20s30s10s11s20s7s7s53s',  # 03 = fiften days
        '2s6s4s8s4s8s9s119s'  # 99 = trailer
    ]
    # Pre-create the structs and then use them on specific functions to
    # improve performance.
    kind_struct = struct.Struct(kind_mask)

    registry_00 = struct.Struct(registry_masks[0])
    registry_01 = struct.Struct(registry_masks[1])
    registry_02 = struct.Struct(registry_masks[2])
    registry_03 = struct.Struct(registry_masks[3])
    registry_99 = struct.Struct(registry_masks[4])


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

"""
class PosicoesSpider():
    name = "cblc_pos"
    start_urls = [
        'http://bvmf.bmfbovespa.com.br/BancoTitulosBTC/PosicoesEmAberto.aspx/?idioma=pt-br'
    ]

    def parse_and_import(filename, data_movimento):
        print("Mandou importar!")

    def parse(self, response):
        # Fix to only fetch weekdays.
        date = datetime.date.today()-datetime.timedelta(3)
        self.log('Fetching data for: %s' % date.strftime('%d/%m/%Y'))

        host = 'bvmf.bmfbovespa.com.br'
        post = '/BancoTitulosBTC/PosicoesEmAberto.aspx?idioma=pt-br'
        params = {
            'ctl00$contentPlaceHolderConteudo$acoes$btnBuscarArquivos': 'Buscar',
        }

        self.log("Params populated: %s" % params)

        # Filename: DBTC20170322.dat
        filename = date.strftime('%Y%m%d') + '.dat'
        with open(temp_path + filename + ".temp", 'wb') as f:
            r = requests.post('http://' + host + post, data=params)

            # 250 bytes + linebreak + CR (from the official documentation)
            reg_size = 252

            # Total response size in bytes
            size = int(r.headers['Content-Length'])
            total_lines = int(size / reg_size)

            if not r.ok:
                self.log('Nao foi possivel requisitar o arquivo')

            for block in r.iter_content(252):
                f.write(block)
                # self.log('Data block written to file')

        with open(temp_path + filename + '.temp', 'rb') as f:
            first_line = next(f).decode()
            f.seek(-252, 2)
            last_line = next(f).decode()
            self.log("\nFL: %s\nLL: %s" % (first_line, last_line))

        # Se a primeira linha é um HEADER e a última um TRAILER
        if(first_line[:2] == "00" and last_line[:2] == "99"):
            data_criacao = first_line[22:30]
            data_movimento = first_line[30:38]
            qtd_registros = int(last_line[30:39].strip())

            if(qtd_registros == total_lines):
                print("Arquivo baixado corretamente")
                move_to_folder(filename)

        else:
            self.log("Download de arquivo inválido")

"""