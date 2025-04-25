Projeto de um motor de xadrez com algoritmo Minimax e interface gráfica em Pygame, incluindo módulo de treinamento por self-play para otimização de parâmetros.

## 🛠️ Funcionalidades:

1. Livro de aberturas
2. Algoritmo Minimax
3. Treinamento por self-play
4. Interface gráfica
  
## 💾 Instalação:

1. Clone o repositório
```bash 
https://github.com/FelipePortoDeveloper/Algoritmos-jogando-xadrez.git
cd NEAT-Aprendendo-a-Jogar-Flappy-Bird
```

2. Instale as dependencias
```bash
pip install pygame python-chess numpy
```

3. Inicie o jogo
```bash
python main.py
```

## ⚙️ Personalização:

- Profundidade de busca: altere o argumento profundidade ao instanciar XadrezIA em main.py ou no treinamento.

- Cor da IA: defina cor=chess.WHITE ou chess.BLACK ao criar XadrezIA.

- Parâmetros customizados: forneça um dicionário de parâmetros personalizados ao inicializar XadrezIA.

## 📂 Estrutura do código:

```bash
Algoritmos-jogando-xadrez/
│
├── img/                     # Arquivos de imagens
├── Perfect2017.bin          # Livro de aberturaas mais utilizado por motores de xadrez
├── graficos.py              # Script que lida com a parte gráfica do jogo
├── ia.py                    # Script que lida com a decisão de jogada da IA
├── jogo.py                  # Script que lida com a parte de regras do jogo
├── main.py                  # Script principal para rodar o jogo
├── melhor_individuo.json    # Arquivo json que armazena os pesos da melhor IA
├── posicoes_ideais_b.json   # Arquivo de posições ideais para as peças pretas
├── posicoes_ideais_w.json   # Arquivo de posições ideais para as peças brancas 
└── README.md                # Documentação do projeto
```

## 📬 Contato

Se tiver dúvidas ou sugestões:

Autor: Felipe Porto

E-mail: felipeportodeveloper5@gmail.com

GitHub: [FelipePortoDeveloper](https://github.com/FelipePortoDeveloper)

  
