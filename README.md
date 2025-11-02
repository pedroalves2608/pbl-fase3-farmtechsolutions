Fase 3 – FarmTech Solutions
Objetivo

Carregar os dados da Fase 2 em um banco de dados Oracle usando o SQL Developer e executar consultas para validação.
Passo a passo resumido
Baixar e extrair o Oracle SQL Developer.
Criar nova conexão
Usuário: RM567029
Host: oracle.fiap.com.br
Porta: 1521
SID: ORCL

Testar conexão até obter Status: Sucesso.

Importar o arquivo <caminho_para_seu_csv>

Botão direito em Tabelas (Filtrado)
Importar Dados
Definir nome da tabela: sensores
Confirmar mapeamento e finalizar.
Validar com consulta SQL

SELECT * FROM sensores;

Verificar linhas e colunas retornadas.

Prints das etapas no Oracle SQL Developer

Figura 1 – Conexão bem sucedida

Figura 2 – Importação concluída com sucesso

Figura 3 – Consulta SELECT executada


Comando SQL e resultado
SELECT * FROM sensores


Descrição do resultado

Colunas esperadas: <umidade>, <temperatura>, <pH>, <N>, <P>, <K>, <chuva>

Linhas retornadas: 66

Amostra observada

<umidade> variou entre 0 e 94.8

<pH> dentro da faixa 5.67 a 7.01

<chuva> com valores categóricos 0 ou 1

Observação
Os prints acima evidenciam a conexão, a importação e a consulta com dados carregados corretamente.

Estrutura do repositório
fase3/
├── README.md
├── codigo/
│   └── <codigo/conversor_dados.cpp>
│   └── <codigo/sensores.py>
├── dados/
│   └── <seu_csv_da_fase2.csv>
└── prints/
    ├── conexao_oracle.png
    ├── importacao_sucesso.png
    └── consulta_select.png

Créditos do grupo

Nome: <Seu Nome> RM <RMxxxx>

Integrantes: <Nome 2>, <Nome 3>, <Nome 4>, <Nome 5> (se houver)

## 🎥 Vídeo Demonstrativo
Assista à demonstração do projeto (até 5 minutos) no link abaixo:

🔗 [Vídeo no YouTube - Não listado](https://youtube.com/seu-link-aqui)
