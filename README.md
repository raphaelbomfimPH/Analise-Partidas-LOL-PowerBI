# Analise-Partidas-LOL-PowerBI
Análise de dados de partidas de League of Legends com dashboard em Power BI

📌 Sobre o Projeto
Este é um projeto End-to-End de Análise de Dados focado no cenário competitivo de League of Legends (Ranked Solo 5x5). O objetivo foi extrair dados reais de milhares de jogadores da API oficial da Riot Games, processar essas informações e criar um painel interativo no Power BI para extrair insights sobre o metajogo, eficiência de jogadores por rota e desempenho de campeões.

O dashboard não apresenta apenas métricas de vaidade, mas sim indicadores de eficiência (como conversão de Ouro em Dano) e análise de comportamento tático por rota (Lanes).

⚙️ Arquitetura e Lógica de Extração (Python ETL)
A coleta de dados foi dividida em duas etapas robustas para garantir a integridade dos dados e respeitar as restrições da API:

Coleta_Partidas.py (Mapeamento da Base de Jogadores):

Lógica: O script varre todos os Elos (do Ferro ao Desafiante) consumindo o endpoint /lol/league/v4/.

Resultado: Gera uma base sólida de jogadores mapeados por Tier e Divisão, criando um censo demográfico do servidor.

Coleta_Players.py (Extração Profunda de Partidas):

Lógica: Lê a base de jogadores e faz chamadas ao endpoint match-v5 para coletar o histórico de partidas de cada usuário.

Diferenciais Técnicos:

Controle de Rate Limit Automático: O script monitora o volume de chamadas e pausa a execução automaticamente (ex: espera 120s após 90 requisições) para evitar bloqueios (Status 429).

Save Points (Batches): Salva os dados processados e o log de progresso a cada 100 jogadores. Se a conexão cair, o script retoma de onde parou sem perda de dados.

Filtro de Contexto: Vasculha o JSON complexo da partida para isolar apenas as estatísticas do jogador alvo, descartando o "ruído" dos outros 9 participantes.

📊 Principais Insights e Lógica de Negócio (Power BI)
O dashboard foi construído para responder a perguntas reais sobre eficiência no jogo. As principais análises incluem:

Métrica Customizada: Eficiência (Dano por Ouro): Em vez de olhar apenas quem deu mais dano, foi criada uma medida em DAX [Soma de Dano] / [Soma de Ouro]. Isso revela quais jogadores convertem recursos financeiros em impacto real nas lutas.

Análise de Outliers (Gráfico de Dispersão): O cruzamento de Ouro vs. Dano segmentado por Rota (Lane) permite identificar rapidamente estilos de jogo. Fica visualmente claro o isolamento dos Suportes (baixo ouro/dano) e a escalada agressiva de Mids e ADCs, além de evidenciar jogadores que "farmaram muito, mas lutaram pouco".

Desempenho de Combate por Posição: Gráfico de colunas empilhadas que quebra o perfil de agressividade. Revela que enquanto Mids focam em Kills, Suportes e Jungles dominam em Assistências, comprovando matematicamente o papel tático de cada rota.

Popularidade vs. Sucesso: Análise dos Top 10 Campeões cruzando Pick Rate (Volume) com Win Rate (Linha de Tendência), evidenciando se os campeões mais populares são efetivamente os que mais garantem vitórias.

🛠️ Tecnologias Utilizadas
Python (Pandas, Requests, Time, OS): Extração, transformação e automação.

Riot Games API: Fonte de dados brutos (League-v4 e Match-v5).

Power BI & DAX: Modelagem tabular, criação de medidas de inteligência de negócio e Data Visualization.

🚀 Como Executar
Clone este repositório.

Insira sua chave da API da Riot (RGAPI) nos scripts Python.

Execute Coleta_Partidas.py para gerar a base de players.

Execute Coleta_Players.py para buscar o detalhamento das partidas.

Abra o arquivo .pbix no Power BI Desktop e atualize a fonte de dados para visualizar o dashboard.
