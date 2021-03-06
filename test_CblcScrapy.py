import unittest
import requests
import os
from CblcScrapy import Downloaders


class CblcTestCase(unittest.TestCase):
    down = Downloaders()
    def test_emprestimos_registrados_connection(self):
        req = requests.get(self.down.EMPRESTIMOS_REGISTRADOS_URL)
        self.assertEqual(req.status_code, 200)

    def teste_remove_header_footer(self):
        arquivo = ['a', 'b', 'c', 'd']
        arquivo_correto = ['b', 'c']
        self.down.remove_header_and_footer(arquivo)
        self.assertEqual(arquivo, arquivo_correto)

    def teste_get_arquivo_errado(self):
        URL = self.down.EMPRESTIMOS_REGISTRADOS_URL + 'lixo'
        try:
            self.down.get_arquivo(URL)
        except requests.RequestException:
            pass


class CblcTestEmprestimosRegistrados(unittest.TestCase):
    down = Downloaders()
    loc = 'tests/emprestimos_registrados/'

    def get_file(self, rel_path):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        f = open(os.path.join(fileDir, rel_path), 'r')
        arq = f.read().split('\n')
        f.close()
        return arq

    def teste_header_errado(self):
        empresimos = self.get_file(self.loc + 'arq_header_errado.txt')
        with self.assertRaisesRegex(ValueError, 'header') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)

    def teste_footer_errado(self):
        empresimos = self.get_file(self.loc + 'arq_footer_errado.txt')
        with self.assertRaisesRegex(ValueError, 'footer') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)
    
    def teste_datas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_datas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'Data') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)

    def teste_qtde_linhas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_qtde_linhas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'Qtde de linhas') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)

    def teste_linhas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_linhas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'quantidade de caracteres') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)

    def teste_arquivo_correto(self):
        empresimos = self.get_file(self.loc + 'arq_correto.txt')
        self.down.valida_integridade_emprestimos_registrados(empresimos)

    def teste_arquivo_incompleto(self):
        empresimos = self.get_file(self.loc + 'arq_incompleto.txt')
        with self.assertRaisesRegex(ValueError, 'incompleto') as context:
            self.down.valida_integridade_emprestimos_registrados(empresimos)


class CblcTestPosicaoEmAberto(unittest.TestCase):
    down = Downloaders()
    loc = 'tests/posicao_em_aberto/'

    def get_file(self, rel_path):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        f = open(os.path.join(fileDir, rel_path), 'r')
        arq = f.read().split('\n')
        f.close()
        return arq

    def teste_header_errado(self):
        empresimos = self.get_file(self.loc + 'arq_header_errado.txt')
        with self.assertRaisesRegex(ValueError, 'header') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)

    def teste_footer_errado(self):
        empresimos = self.get_file(self.loc + 'arq_footer_errado.txt')
        with self.assertRaisesRegex(ValueError, 'footer') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)
    
    def teste_datas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_datas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'Data') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)

    def teste_qtde_linhas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_qtde_linhas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'Qtde de linhas') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)

    def teste_linhas_erradas(self):
        empresimos = self.get_file(self.loc + 'arq_linhas_erradas.txt')
        with self.assertRaisesRegex(ValueError, 'quantidade de caracteres') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)

    def teste_arquivo_correto(self):
        empresimos = self.get_file(self.loc + 'arq_correto.txt')
        self.down.valida_integridade_posicao_em_aberto(empresimos)

    def teste_arquivo_incompleto(self):
        empresimos = self.get_file(self.loc + 'arq_incompleto.txt')
        with self.assertRaisesRegex(ValueError, 'incompleto') as context:
            self.down.valida_integridade_posicao_em_aberto(empresimos)


if __name__ == '__main__':
    unittest.main()