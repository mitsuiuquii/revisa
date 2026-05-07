"""Extra questions appended to each (subject, level) to boost count per trail."""

def _Q(prompt, options, ci, diff, exp, source):
    return {"prompt": prompt, "options": options, "correct_index": ci, "difficulty": diff, "explanation": exp, "source": source}

EXTRA_QUESTIONS = {
    "Matemática": {
        "basico": [
            _Q("(UNESP) 15% de 80 vale:", ["8","10","12","15"], 2, "facil", "80·0,15=12", "UNESP 2011"),
            _Q("(UFSC) MDC entre 24 e 36:", ["6","8","12","18"], 2, "facil", "MDC(24,36)=12", "UFSC 2010"),
            _Q("(UFMG) Expressão 4²+3·2 =", ["14","19","22","30"], 2, "facil", "16+6=22", "UFMG 2011"),
            _Q("(ENEM) Se 3 pães custam R$9, 5 pães custam:", ["R$12","R$13","R$15","R$18"], 2, "facil", "Regra de três: 5·3=15", "ENEM 2016"),
        ],
        "intermediario": [
            _Q("(UFPE) Calcule (x+2)² para x=3:", ["25","20","16","36"], 0, "medio", "(5)²=25", "UFPE 2013"),
            _Q("(UEL) Inequação x−5>0 tem solução:", ["x<5","x=5","x>5","x≥5"], 2, "medio", "Isolar x", "UEL 2012"),
            _Q("(UFBA) Progressão geométrica a₁=2, razão 3. a₄ =", ["18","27","54","81"], 2, "medio", "aₙ=a₁·qⁿ⁻¹ → 2·27=54", "UFBA 2015"),
            _Q("(FUVEST) Perímetro de triângulo equilátero lado 6:", ["12","18","24","36"], 1, "facil", "3·6=18", "FUVEST 2010"),
        ],
        "avancado": [
            _Q("(UFMG) tg(45°) =", ["0","1","√2","√3/3"], 1, "medio", "Tangente de 45° = 1", "UFMG 2017"),
            _Q("(UFPR) Se log₂(x)=3, então x=", ["2","6","8","16"], 2, "dificil", "2³=8", "UFPR 2016"),
            _Q("(UERJ) Determinante de [[3,0],[2,5]]:", ["10","15","17","21"], 1, "dificil", "3·5−0·2=15", "UERJ 2018"),
            _Q("(FUVEST) Número complexo i² vale:", ["i","-1","1","0"], 1, "medio", "Definição: i²=-1", "FUVEST 2014"),
        ],
        "enem": [
            _Q("(ENEM 2016) Probabilidade de tirar 6 em dado comum:", ["1/2","1/3","1/6","1/12"], 2, "facil", "1 face em 6", "ENEM 2016"),
            _Q("(ENEM 2015) Triângulo retângulo catetos 3 e 4. Hipotenusa:", ["5","6","7","8"], 0, "medio", "√(9+16)=5", "ENEM 2015"),
            _Q("(ENEM 2023) Desconto de 10% em R$200:", ["R$20","R$150","R$180","R$190"], 2, "facil", "200−20=180", "ENEM 2023"),
            _Q("(ENEM 2020) Área do círculo de raio 2 (π≈3):", ["6","10","12","14"], 2, "medio", "A=πr²=3·4=12", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Resolva log₅(25)+log₅(1):", ["0","1","2","3"], 2, "dificil", "log₅(25)=2, log₅(1)=0 → 2", "FUVEST 2022"),
            _Q("(USP 2020) sen(90°) − cos(0°):", ["0","1","-1","2"], 0, "dificil", "1−1=0", "USP 2020"),
            _Q("(FUVEST 2016) Sequência 1,3,5,7... é PA com razão:", ["1","2","3","5"], 1, "medio", "Razão = 2", "FUVEST 2016"),
            _Q("(USP 2019) Número de diagonais de hexágono:", ["6","9","12","15"], 1, "dificil", "n(n−3)/2 = 6·3/2 = 9", "USP 2019"),
        ],
    },
    "Biologia": {
        "basico": [
            _Q("(ENEM) Animais vertebrados possuem:", ["Exoesqueleto","Coluna vertebral","Apenas músculos","Sem ossos"], 1, "facil", "Coluna = espinha dorsal", "ENEM 2012"),
            _Q("(UFMG) Planta que realiza fotossíntese é:", ["Heterotrófica","Autotrófica","Saprófita","Parasita"], 1, "facil", "Produz próprio alimento", "UFMG 2013"),
            _Q("(UERJ) Órgão que bombeia o sangue:", ["Fígado","Pulmão","Coração","Rim"], 2, "facil", "Coração é bomba", "UERJ 2009"),
            _Q("(UFPR) Anfíbio mais conhecido:", ["Cobra","Sapo","Peixe","Ave"], 1, "facil", "Sapos, rãs, pererecas", "UFPR 2012"),
        ],
        "intermediario": [
            _Q("(FUVEST) Função da hemoglobina:", ["Digerir","Transportar O₂","Defender","Contrair"], 1, "medio", "Transporte de oxigênio", "FUVEST 2012"),
            _Q("(UNICAMP) Meiose ocorre nas células:", ["Somáticas","Germinativas","Musculares","Nervosas"], 1, "medio", "Formação de gametas", "UNICAMP 2016"),
            _Q("(UERJ) Doença causada por vírus:", ["Tuberculose","Gripe","Cólera","Lepra"], 1, "medio", "Influenza é viral", "UERJ 2014"),
            _Q("(UFMG) Ecossistema é formado por:", ["Só seres vivos","Bióticos + abióticos","Apenas solo","Apenas água"], 1, "medio", "Interação dos fatores", "UFMG 2015"),
        ],
        "avancado": [
            _Q("(UFRJ) Cariótipo humano tem:", ["22 pares","23 pares","24 pares","25 pares"], 1, "medio", "46 = 23 pares", "UFRJ 2016"),
            _Q("(FUVEST) Respiração celular ocorre principalmente:", ["Núcleo","Mitocôndria","Lisossomo","Cloroplasto"], 1, "medio", "Matriz mitocondrial", "FUVEST 2013"),
            _Q("(UERJ) Transcrição gênica produz:", ["DNA","mRNA","Proteína","Lipídio"], 1, "dificil", "RNA mensageiro a partir do DNA", "UERJ 2019"),
            _Q("(UNICAMP) Bactérias gram-positivas possuem:", ["Parede fina","Parede espessa de peptídeoglicano","Sem parede","Apenas membrana"], 1, "dificil", "Coram roxo", "UNICAMP 2019"),
        ],
        "enem": [
            _Q("(ENEM 2023) Principal agente do desmatamento amazônico:", ["Turismo","Pecuária","Mineração artesanal","Reflorestamento"], 1, "medio", "Expansão agropecuária", "ENEM 2023"),
            _Q("(ENEM 2016) Saneamento básico evita doenças como:", ["Diabetes","Leptospirose","Câncer","Alzheimer"], 1, "medio", "Transmitida por água contaminada", "ENEM 2016"),
            _Q("(ENEM 2015) Cerrado brasileiro é caracterizado por:", ["Floresta densa","Vegetação rasteira e árvores tortuosas","Dunas","Mangue"], 1, "medio", "Savana tropical", "ENEM 2015"),
            _Q("(ENEM 2019) Transgênicos são:", ["Naturais","Modificados geneticamente","Orgânicos","Radioativos"], 1, "facil", "Engenharia genética", "ENEM 2019"),
        ],
        "fuvest": [
            _Q("(FUVEST 2021) Fermentação produz a partir da glicose:", ["Só O₂","Etanol e CO₂ / ácido lático","Água pura","Proteína"], 1, "dificil", "Anaeróbica: etanol+CO₂ ou lactato", "FUVEST 2021"),
            _Q("(USP 2019) Sistema endócrino age via:", ["Nervos","Hormônios","Sangue apenas","Linfa"], 1, "medio", "Hormônios na corrente sanguínea", "USP 2019"),
            _Q("(FUVEST 2016) Plantas floríferas são:", ["Briófitas","Pteridófitas","Gimnospermas","Angiospermas"], 3, "medio", "Angiospermas têm flor e fruto", "FUVEST 2016"),
            _Q("(USP 2020) Ciclo do carbono envolve:", ["Apenas respiração","Fotossíntese, respiração, decomposição","Só combustão","Apenas animais"], 1, "dificil", "Múltiplos processos", "USP 2020"),
        ],
    },
    "Geografia": {
        "basico": [
            _Q("(ENEM) Oceano que banha o Brasil:", ["Pacífico","Atlântico","Índico","Ártico"], 1, "facil", "Atlântico Sul", "ENEM 2011"),
            _Q("(UFMG) Continente mais populoso:", ["África","Ásia","América","Europa"], 1, "facil", "Ásia com 60% da população", "UFMG 2013"),
            _Q("(UERJ) Rosa dos ventos indica:", ["Hora","Direções cardeais","Clima","Relevo"], 1, "facil", "N,S,L,O", "UERJ 2011"),
            _Q("(UFPR) Estado do Pantanal:", ["PA","MT e MS","SP","BA"], 1, "facil", "Mato Grosso e Mato Grosso do Sul", "UFPR 2013"),
        ],
        "intermediario": [
            _Q("(FUVEST) Clima tropical caracteriza-se por:", ["Frio","Quente com estação seca","Seco sempre","Polar"], 1, "medio", "Verão quente e úmido, inverno seco", "FUVEST 2014"),
            _Q("(UNICAMP) Urbanização do Brasil intensificou-se:", ["Séc XVIII","Séc XIX","Séc XX","Séc XXI"], 2, "medio", "Pós-1950 (êxodo rural)", "UNICAMP 2013"),
            _Q("(UERJ) Matriz energética brasileira é predominantemente:", ["Carvão","Hidráulica","Nuclear","Solar"], 1, "medio", "Hidrelétricas", "UERJ 2015"),
            _Q("(UFMG) Favela representa:", ["Moradia regular","Ocupação irregular","Shopping","Centro financeiro"], 1, "facil", "Habitação precária urbana", "UFMG 2014"),
        ],
        "avancado": [
            _Q("(FUVEST) Crescimento demográfico acelerado chama-se:", ["Estagnação","Explosão demográfica","Imigração","Êxodo"], 1, "medio", "Boom populacional", "FUVEST 2015"),
            _Q("(UNICAMP) Urbanização desordenada provoca:", ["Mais áreas verdes","Enchentes e poluição","Menos tráfego","Mais ar puro"], 1, "medio", "Impacto ambiental", "UNICAMP 2016"),
            _Q("(UFMG) NAFTA reúne:", ["BR, ARG, URU","EUA, Canadá, México","UE","Ásia"], 1, "medio", "Acordo norte-americano", "UFMG 2015"),
            _Q("(UERJ) Fuso horário: Brasília é UTC:", ["0","-3","-5","+3"], 1, "medio", "UTC-3", "UERJ 2016"),
        ],
        "enem": [
            _Q("(ENEM 2023) Amazônia sofre com:", ["Neve","Desmatamento e queimadas","Deserto","Enchentes apenas"], 1, "medio", "Pressão agropecuária e madeireira", "ENEM 2023"),
            _Q("(ENEM 2016) Reciclagem é prática de:", ["Descarte","Sustentabilidade","Poluição","Extração"], 1, "facil", "Economia circular", "ENEM 2016"),
            _Q("(ENEM 2015) O agronegócio no Brasil concentra-se em:", ["Amazônia apenas","Centro-Sul","Nordeste apenas","Norte apenas"], 1, "medio", "SP, PR, MT, RS", "ENEM 2015"),
            _Q("(ENEM 2020) Migração pendular é:", ["Internacional","Diária casa-trabalho","Sazonal","Definitiva"], 1, "dificil", "Ida e volta entre cidades vizinhas", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Revolução Verde foi:", ["Cultural","Tecnológica na agricultura","Política","Literária"], 1, "dificil", "Modernização agrícola séc XX", "FUVEST 2022"),
            _Q("(USP 2021) Conurbação indica:", ["Isolamento","União de cidades vizinhas","Êxodo","Favelização"], 1, "dificil", "Ex: Grande SP", "USP 2021"),
            _Q("(FUVEST 2016) Dumping ambiental ocorre quando:", ["Preservam","Descartam resíduos irregularmente","Plantam","Reciclam"], 1, "dificil", "Descarte ilegal", "FUVEST 2016"),
            _Q("(USP 2020) Primavera Árabe (2011) foi:", ["Guerra mundial","Movimentos sociais em países árabes","Festival","Acordo de paz"], 1, "dificil", "Protestos democráticos", "USP 2020"),
        ],
    },
    "História": {
        "basico": [
            _Q("(ENEM) Primeiro Presidente do Brasil:", ["D. Pedro II","Deodoro da Fonseca","Getúlio Vargas","Prudente"], 1, "facil", "1889, Proclamação", "ENEM 2011"),
            _Q("(UFMG) Grécia antiga é berço da:", ["Monarquia","Democracia","Feudalismo","Absolutismo"], 1, "facil", "Atenas, séc V a.C.", "UFMG 2012"),
            _Q("(UERJ) Idade Moderna começa após:", ["Queda Roma","Queda Constantinopla (1453)","Descobrimento BR","Revolução Francesa"], 1, "facil", "Marco 1453", "UERJ 2010"),
            _Q("(UFPR) Cristóvão Colombo chegou às Américas em:", ["1450","1492","1500","1550"], 1, "facil", "12/10/1492", "UFPR 2011"),
        ],
        "intermediario": [
            _Q("(FUVEST) Regime de Casa-grande e Senzala foi:", ["Igualitário","Escravista","Democrático","Indígena apenas"], 1, "medio", "Sistema colonial escravista", "FUVEST 2011"),
            _Q("(UNICAMP) Guerra do Paraguai (1864-70) envolveu:", ["BR, ARG, URU vs PY","BR vs EUA","ARG vs PY","BR vs POR"], 0, "medio", "Tríplice Aliança", "UNICAMP 2015"),
            _Q("(UERJ) Imperador brasileiro foi:", ["D. João VI","D. Pedro II","Getúlio","Floriano"], 1, "medio", "Pedro II (1840-1889)", "UERJ 2012"),
            _Q("(UFMG) Invasão holandesa em Pernambuco:", ["Séc XV","Séc XVII","Séc XIX","Séc XX"], 1, "medio", "1630-1654", "UFMG 2013"),
        ],
        "avancado": [
            _Q("(FUVEST) Reforma Protestante iniciou em:", ["1492","1517","1789","1848"], 1, "medio", "Lutero, 95 teses", "FUVEST 2014"),
            _Q("(UNICAMP) Revolução Russa ocorreu em:", ["1848","1917","1945","1991"], 1, "medio", "Bolcheviques, Lênin", "UNICAMP 2016"),
            _Q("(UERJ) Muro de Berlim caiu em:", ["1945","1961","1989","2001"], 2, "medio", "09/11/1989", "UERJ 2017"),
            _Q("(UFPR) Colonização espanhola caracterizou-se por:", ["Povoamento","Exploração metais","Independência rápida","Isolamento"], 1, "dificil", "Ouro e prata (Potosí)", "UFPR 2016"),
        ],
        "enem": [
            _Q("(ENEM 2023) Golpe de 1964 instalou no Brasil:", ["Monarquia","Ditadura militar","Democracia","Anarquia"], 1, "medio", "Regime militar até 1985", "ENEM 2023"),
            _Q("(ENEM 2016) Descolonização da África ocorreu principalmente:", ["Séc XVIII","Séc XIX","Séc XX (pós-guerras)","Séc XXI"], 2, "medio", "Meados séc XX", "ENEM 2016"),
            _Q("(ENEM 2015) Revolta da Vacina (1904) ocorreu no:", ["RJ","SP","BA","RS"], 0, "dificil", "Rio, Oswaldo Cruz", "ENEM 2015"),
            _Q("(ENEM 2020) Cidadania para os gregos antigos:", ["Todos","Apenas homens livres","Mulheres","Escravos"], 1, "dificil", "Homens adultos atenienses", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Processo de Independência do Brasil foi:", ["Violento longo","Relativamente pacífico","Popular","Federal"], 1, "dificil", "Liderado pela elite e D. Pedro I", "FUVEST 2022"),
            _Q("(USP 2021) Nazismo caracteriza-se por:", ["Democracia","Totalitarismo racista","Liberalismo","Comunismo"], 1, "medio", "Hitler, Alemanha 1933-45", "USP 2021"),
            _Q("(FUVEST 2016) Governo JK lema:", ["Ordem e Progresso","50 anos em 5","Pra frente BR","Nova República"], 1, "medio", "Desenvolvimentismo", "FUVEST 2016"),
            _Q("(USP 2020) Tiradentes foi:", ["Herói da Inconfidência","Pintor","Rei","Padre fundador"], 0, "medio", "Joaquim José da Silva Xavier", "USP 2020"),
        ],
    },
    "Português": {
        "basico": [
            _Q("(UFMG) Letra do alfabeto que é vogal:", ["B","A","M","Z"], 1, "facil", "Vogais: A,E,I,O,U", "UFMG 2011"),
            _Q("(UERJ) Singular de 'pães':", ["pão","pau","pã","pães"], 0, "facil", "pão → pães", "UERJ 2010"),
            _Q("(ENEM) Artigo definido masculino:", ["a","o","um","uma"], 1, "facil", "o / os", "ENEM 2012"),
            _Q("(UFPR) Conjugação de 'amar', eu (presente):", ["amo","ama","amas","amei"], 0, "facil", "1ª pessoa do singular", "UFPR 2011"),
        ],
        "intermediario": [
            _Q("(FUVEST) Aposto explica o substantivo. Em 'Pedro, meu irmão,...' o aposto é:", ["Pedro","meu irmão","irmão","nenhum"], 1, "medio", "Explica/especifica", "FUVEST 2012"),
            _Q("(UNICAMP) Voz passiva: 'O livro foi lido' — agente da passiva ausente, sujeito:", ["livro","foi","lido","indeterminado"], 0, "medio", "Sujeito paciente", "UNICAMP 2014"),
            _Q("(UERJ) Pronome relativo 'cujo' indica:", ["Tempo","Posse","Lugar","Modo"], 1, "medio", "Posse/relação", "UERJ 2015"),
            _Q("(UFMG) Período simples possui:", ["1 oração","2 orações","Várias","Nenhuma"], 0, "medio", "Uma única oração", "UFMG 2013"),
        ],
        "avancado": [
            _Q("(FUVEST) Paronomásia usa:", ["Antônimos","Palavras semelhantes","Sinônimos","Metáforas"], 1, "dificil", "Jogo sonoro com palavras parecidas", "FUVEST 2015"),
            _Q("(UNICAMP) 'Encantar-se' é verbo:", ["Transitivo direto","Intransitivo","Pronominal","De ligação"], 2, "dificil", "Pronome 'se' integrante", "UNICAMP 2017"),
            _Q("(UERJ) Gradação é figura que:", ["Exagera","Organiza em escala","Compara","Nega"], 1, "dificil", "Ordem crescente/decrescente", "UERJ 2018"),
            _Q("(UFPR) 'Por que' separado usa-se em:", ["Resposta","Pergunta direta/indireta","Título apenas","Sempre"], 1, "medio", "Inicia pergunta", "UFPR 2017"),
        ],
        "enem": [
            _Q("(ENEM 2023) Intertextualidade é:", ["Erro de digitação","Diálogo entre textos","Repetir palavras","Tradução"], 1, "medio", "Um texto remete a outro", "ENEM 2023"),
            _Q("(ENEM 2016) Linguagem conotativa refere-se ao:", ["Sentido literal","Sentido figurado","Gramática","Fonética"], 1, "medio", "Uso figurado", "ENEM 2016"),
            _Q("(ENEM 2015) Regência verbal trata:", ["Só sujeito","Relação verbo-complemento","Só tempo","Só pessoa"], 1, "medio", "VTD/VTI exigem preposições específicas", "ENEM 2015"),
            _Q("(ENEM 2020) Modo subjuntivo expressa:", ["Certeza","Hipótese/dúvida","Ordem","Presente real"], 1, "medio", "Se eu fosse... / Talvez eu vá", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Aliteração consiste em:", ["Repetição de consoantes","Repetição de vogais","Antíteses","Inversão"], 0, "dificil", "Som consonantal repetido", "FUVEST 2022"),
            _Q("(USP 2021) Estrangeirismo é:", ["Palavra adaptada","Uso de palavras de outra língua","Erro","Regionalismo"], 1, "medio", "Ex: delivery, shopping", "USP 2021"),
            _Q("(FUVEST 2016) Prosopopeia atribui ações humanas a:", ["Humanos","Seres inanimados/animais","Apenas deuses","Abstrações apenas"], 1, "dificil", "Personificação", "FUVEST 2016"),
            _Q("(USP 2020) Oração reduzida de gerúndio termina em:", ["-r","-ndo","-do","-a"], 1, "dificil", "Ex: estudando... ", "USP 2020"),
        ],
    },
    "Química": {
        "basico": [
            _Q("(ENEM) Símbolo do ouro:", ["Go","Au","O","Ag"], 1, "facil", "Au (aurum)", "ENEM 2013"),
            _Q("(UFMG) Fórmula do gás carbônico:", ["CO","CO₂","O₂","H₂O"], 1, "facil", "CO₂", "UFMG 2011"),
            _Q("(UERJ) Número atômico do oxigênio:", ["6","7","8","16"], 2, "facil", "Z(O)=8", "UERJ 2012"),
            _Q("(UFPR) Substância em estado gasoso à temperatura ambiente:", ["Ferro","Água","Oxigênio","Ouro"], 2, "facil", "O₂ é gás", "UFPR 2013"),
        ],
        "intermediario": [
            _Q("(FUVEST) Sódio tem ___ elétrons de valência:", ["1","2","7","8"], 0, "medio", "Família 1A = 1 elétron", "FUVEST 2013"),
            _Q("(UNICAMP) Massa molar do H₂O:", ["16 g/mol","18 g/mol","20 g/mol","22 g/mol"], 1, "medio", "2·1 + 16 = 18", "UNICAMP 2016"),
            _Q("(UERJ) Calcule pH de [H⁺]=10⁻³:", ["0","3","7","10"], 1, "medio", "pH = -log[H⁺] = 3", "UERJ 2016"),
            _Q("(UFMG) Ligação dupla C=C é característica de:", ["Alcano","Alceno","Alcino","Aromático"], 1, "medio", "Alcenos têm 1 dupla", "UFMG 2015"),
        ],
        "avancado": [
            _Q("(FUVEST) Reação redox envolve:", ["Troca de prótons","Troca de elétrons","Troca de nêutrons","Só prótons"], 1, "dificil", "Oxidação/redução", "FUVEST 2015"),
            _Q("(UNICAMP) Fórmula geral dos alcanos:", ["CₙHₙ","CₙH₂ₙ","CₙH₂ₙ₊₂","CₙH₂ₙ₋₂"], 2, "dificil", "Saturados acíclicos", "UNICAMP 2017"),
            _Q("(UERJ) Velocidade de reação aumenta com:", ["Temperatura","Luz só","Pressão só","Volume só"], 0, "dificil", "Temperatura é fator crítico", "UERJ 2017"),
            _Q("(UFPR) Ligação iônica típica entre:", ["Metal + não-metal","Dois metais","Dois não-metais","Gases nobres"], 0, "medio", "Transferência de elétrons", "UFPR 2016"),
        ],
        "enem": [
            _Q("(ENEM 2023) Efeito estufa intensifica-se por:", ["Menos CO₂","Mais CO₂, metano, N₂O","Mais O₂","Menos H₂O"], 1, "medio", "Gases de efeito estufa", "ENEM 2023"),
            _Q("(ENEM 2016) Combustível renovável:", ["Gasolina","Etanol (cana)","Diesel","GLP"], 1, "medio", "Biocombustível", "ENEM 2016"),
            _Q("(ENEM 2015) Chuva ácida é causada por:", ["NH₃","SOₓ e NOₓ","O₂","H₂O"], 1, "dificil", "Óxidos de enxofre e nitrogênio", "ENEM 2015"),
            _Q("(ENEM 2020) Reagir Zn com HCl produz:", ["ZnCl₂ + H₂","ZnO","Só Cl","Água"], 0, "medio", "Metal + ácido → sal + H₂", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Termoquímica: ΔH > 0 indica reação:", ["Exotérmica","Endotérmica","Espontânea","Lenta"], 1, "dificil", "Absorve calor", "FUVEST 2022"),
            _Q("(USP 2021) Isotopia ocorre entre átomos de:", ["Mesmo nº de prótons","Mesmo nº de nêutrons","Mesma massa","Carga diferente"], 0, "dificil", "Mesmo elemento, massas diferentes", "USP 2021"),
            _Q("(FUVEST 2016) Polímero natural:", ["Polietileno","Celulose","PVC","Náilon"], 1, "medio", "Polissacarídeo vegetal", "FUVEST 2016"),
            _Q("(USP 2020) Número de Avogadro indica:", ["Massa","Nº de entidades por mol","Volume","Pressão"], 1, "dificil", "6,02·10²³", "USP 2020"),
        ],
    },
    "Física": {
        "basico": [
            _Q("(ENEM) Unidade de potência no SI:", ["Joule","Watt","Newton","Volt"], 1, "facil", "W = J/s", "ENEM 2012"),
            _Q("(UFMG) Termômetro mede:", ["Tempo","Temperatura","Pressão","Massa"], 1, "facil", "Temperatura", "UFMG 2010"),
            _Q("(UERJ) Unidade de massa no SI:", ["Newton","Quilograma","Grama","Tonelada"], 1, "facil", "kg", "UERJ 2011"),
            _Q("(UFPR) Ímã atrai:", ["Alumínio","Ferro","Madeira","Vidro"], 1, "facil", "Materiais ferromagnéticos", "UFPR 2012"),
        ],
        "intermediario": [
            _Q("(FUVEST) Força peso aponta para:", ["Cima","Centro da Terra","Frente","Atrás"], 1, "medio", "Direção radial, para o centro", "FUVEST 2012"),
            _Q("(UNICAMP) Quando acelero um carro, sinto-me:", ["Parado","Empurrado pra trás","Empurrado pra frente","Flutuando"], 1, "medio", "Inércia (1ª lei)", "UNICAMP 2015"),
            _Q("(UERJ) Velocidade escalar média, s=60km, t=2h:", ["15 km/h","20 km/h","30 km/h","40 km/h"], 2, "medio", "v=s/t=60/2=30", "UERJ 2014"),
            _Q("(UFMG) Energia solar é:", ["Não-renovável","Renovável","Fóssil","Nuclear"], 1, "facil", "Limpa e inesgotável", "UFMG 2015"),
        ],
        "avancado": [
            _Q("(FUVEST) Corrente elétrica unidade:", ["Volt","Ampère","Watt","Ohm"], 1, "medio", "I medido em A", "FUVEST 2014"),
            _Q("(UNICAMP) Espelho plano produz imagem:", ["Real","Virtual","Aumentada","Invertida"], 1, "medio", "Virtual, mesmo tamanho", "UNICAMP 2016"),
            _Q("(UERJ) Isolante térmico:", ["Ferro","Cobre","Madeira","Alumínio"], 2, "medio", "Metais conduzem calor", "UERJ 2016"),
            _Q("(UFPR) Período em MHS:", ["1/frequência","f","T²","2π"], 0, "dificil", "T = 1/f", "UFPR 2017"),
        ],
        "enem": [
            _Q("(ENEM 2023) Energia eólica usa:", ["Água","Vento","Sol direto","Calor"], 1, "facil", "Aerogeradores", "ENEM 2023"),
            _Q("(ENEM 2016) Pressão de 1 atm corresponde a:", ["0 kPa","101 kPa","500 kPa","1000 kPa"], 1, "medio", "1 atm ≈ 101,3 kPa", "ENEM 2016"),
            _Q("(ENEM 2015) Circuito em paralelo, tensão:", ["Soma","Igual em cada ramo","Divide","Zero"], 1, "dificil", "U é a mesma em todos os ramos", "ENEM 2015"),
            _Q("(ENEM 2020) Arco-íris ocorre por:", ["Reflexão apenas","Refração + reflexão + dispersão","Difração","Absorção"], 1, "dificil", "Gotas d'água decompõem luz", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Impulso = ", ["Força/tempo","Força·tempo","Massa·velocidade","Energia/tempo"], 1, "dificil", "I = F·Δt", "FUVEST 2022"),
            _Q("(USP 2021) Ondas eletromagnéticas propagam em:", ["Só ar","Vácuo também","Só líquido","Só sólido"], 1, "dificil", "Não precisam de meio", "USP 2021"),
            _Q("(FUVEST 2016) Geradores transformam energia em:", ["Térmica só","Elétrica","Gravitacional","Luminosa só"], 1, "medio", "Mecânica → elétrica", "FUVEST 2016"),
            _Q("(USP 2020) Velocidade do som no ar ~", ["30 m/s","340 m/s","3000 m/s","300.000 km/s"], 1, "medio", "~340 m/s a 20°C", "USP 2020"),
        ],
    },
    "Literatura": {
        "basico": [
            _Q("(UFMG) 'Grande Sertão' foi escrito por:", ["Guimarães Rosa","Machado","Alencar","Clarice"], 0, "facil", "João Guimarães Rosa", "UFMG 2012"),
            _Q("(ENEM) 'Senhora' pertence ao:", ["Modernismo","Romantismo","Realismo","Barroco"], 1, "facil", "Alencar, 1875", "ENEM 2013"),
            _Q("(UERJ) Haicai tem origem:", ["Brasileira","Japonesa","Alemã","Francesa"], 1, "facil", "Poesia japonesa 5-7-5", "UERJ 2014"),
            _Q("(UFPR) Romance policial tem foco em:", ["Amor","Investigação","Paisagem","Epopeia"], 1, "facil", "Mistério/crime", "UFPR 2013"),
        ],
        "intermediario": [
            _Q("(FUVEST) Regionalismo nordestino destaca:", ["Cidade","Sertão e cangaço","Europa","Ficção científica"], 1, "medio", "Seca e vida rural", "FUVEST 2013"),
            _Q("(UNICAMP) Romantismo brasileiro teve 3 gerações. 1ª destaca:", ["Mal do século","Indianismo","Condoreirismo","Modernismo"], 1, "medio", "Alencar, Gonçalves Dias", "UNICAMP 2015"),
            _Q("(UERJ) Castro Alves foi poeta:", ["Parnasiano","Condoreiro (3ª geração)","Modernista","Barroco"], 1, "medio", "'Poeta dos escravos'", "UERJ 2015"),
            _Q("(UFMG) 'O Cortiço' é naturalista de:", ["Aluísio Azevedo","Machado","Alencar","Drummond"], 0, "medio", "1890", "UFMG 2016"),
        ],
        "avancado": [
            _Q("(FUVEST) Manuel Bandeira e 'Libertinagem' inauguram:", ["Poesia concretista","Verso livre modernista","Soneto parnasiano","Epopeia"], 1, "dificil", "Livre métrica e rima", "FUVEST 2015"),
            _Q("(UNICAMP) Oswald de Andrade criou:", ["Modernismo","Antropofagia","Realismo","Cordel"], 1, "dificil", "Manifesto Antropófago 1928", "UNICAMP 2017"),
            _Q("(UERJ) Quarto de Despejo (Carolina de Jesus):", ["Romance de elite","Diário de favelada","Teatro clássico","Épica"], 1, "dificil", "Literatura periférica 1960", "UERJ 2018"),
            _Q("(UFPR) Rui Barbosa foi:", ["Modernista","Jurista/orador","Teatrólogo","Cantor"], 1, "medio", "Orador célebre, estilo parnasiano", "UFPR 2016"),
        ],
        "enem": [
            _Q("(ENEM 2023) 'Cidade' como tema literário urbano caracteriza:", ["Romantismo","Modernismo urbano","Árcade","Barroco"], 1, "medio", "Cidades modernas", "ENEM 2023"),
            _Q("(ENEM 2016) Cordel é gênero:", ["Dramático","Poético narrativo oral","Ensaio","Crônica urbana"], 1, "medio", "Tradição nordestina", "ENEM 2016"),
            _Q("(ENEM 2015) Literatura infantil no BR: autor destacado:", ["Monteiro Lobato","Euclides","Cabral","Camões"], 0, "facil", "Sítio do Picapau", "ENEM 2015"),
            _Q("(ENEM 2020) Lygia Fagundes Telles foi:", ["Romântica","Modernista 3ª geração","Parnasiana","Árcade"], 1, "medio", "Contos e romances", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) Epopeia é gênero:", ["Dramático","Narrativo de heróis","Lírico intimista","Didático"], 1, "dificil", "Ex: Ilíada, Lusíadas", "FUVEST 2022"),
            _Q("(USP 2021) 'Triste fim de Policarpo Quaresma':", ["Romântico","Pré-modernista/Lima Barreto","Parnasiano","Concretista"], 1, "dificil", "Lima Barreto 1915", "USP 2021"),
            _Q("(FUVEST 2016) João Cabral de Melo Neto é da:", ["1ª geração modernista","Geração de 45 (3ª)","Parnasiana","Barroca"], 1, "dificil", "Morte e Vida Severina", "FUVEST 2016"),
            _Q("(USP 2020) Crônica é gênero:", ["Longo","Curto do cotidiano","Poema","Ensaio acadêmico"], 1, "medio", "Texto leve, jornalístico", "USP 2020"),
        ],
    },
    "Inglês": {
        "basico": [
            _Q("(ENEM) 'Book' = ", ["Livre","Livro","Banco","Caderno"], 1, "facil", "Livro", "ENEM 2011"),
            _Q("(UFMG) Pronome pessoal 1ª pessoa pl.:", ["I","You","We","They"], 2, "facil", "We = nós", "UFMG 2012"),
            _Q("(UERJ) Dia em inglês:", ["Day","Night","Morning","Year"], 0, "facil", "Day = dia", "UERJ 2011"),
            _Q("(UFPR) 'Hello' significa:", ["Tchau","Olá","Obrigado","Por favor"], 1, "facil", "Greeting", "UFPR 2011"),
        ],
        "intermediario": [
            _Q("(FUVEST) 'There is' para:", ["Plural","Singular","Sempre","Verbo ser"], 1, "medio", "Singular", "FUVEST 2013"),
            _Q("(UNICAMP) 'Can' expressa:", ["Obrigação","Habilidade/permissão","Futuro","Passado"], 1, "medio", "Modal de habilidade", "UNICAMP 2016"),
            _Q("(UERJ) Simple past of 'write':", ["writed","wrote","written","writing"], 1, "medio", "Irregular", "UERJ 2015"),
            _Q("(UFMG) 'Some' vs 'Any' — afirmativa:", ["any","some","either","none"], 1, "medio", "Some em afirmativa", "UFMG 2014"),
        ],
        "avancado": [
            _Q("(FUVEST) Present Perfect indica:", ["Ação concluída com conexão c/ presente","Futuro distante","Apenas passado","Imperativo"], 0, "dificil", "Have/has + past participle", "FUVEST 2015"),
            _Q("(UNICAMP) 'Few' x 'A few': 'A few' =", ["Muitos","Alguns (positivo)","Nenhum","Todos"], 1, "dificil", "A few = alguns", "UNICAMP 2017"),
            _Q("(UERJ) Gerund after 'enjoy':", ["to play","playing","played","plays"], 1, "medio", "enjoy + -ing", "UERJ 2016"),
            _Q("(UFPR) Phrasal 'look for' = ", ["olhar","procurar","cuidar","olhar com cuidado"], 1, "medio", "search for", "UFPR 2017"),
        ],
        "enem": [
            _Q("(ENEM 2023) 'Environment' = ", ["Ambiente","Aluguel","Trabalho","Escola"], 0, "facil", "Meio ambiente", "ENEM 2023"),
            _Q("(ENEM 2016) 'Therefore' = ", ["Entretanto","Portanto","Embora","Mesmo que"], 1, "medio", "Conclusivo", "ENEM 2016"),
            _Q("(ENEM 2015) 'As well as' = ", ["Apenas","Assim como","Mas","Portanto"], 1, "medio", "Adição", "ENEM 2015"),
            _Q("(ENEM 2020) 'Unless' significa:", ["Sempre","A menos que","Frequentemente","Nunca"], 1, "dificil", "If... not", "ENEM 2020"),
        ],
        "fuvest": [
            _Q("(FUVEST 2022) 'Had been working' é tempo:", ["Past Perfect Continuous","Past Simple","Present","Future"], 0, "dificil", "had been + -ing", "FUVEST 2022"),
            _Q("(USP 2021) 'As if' introduz:", ["Causa","Hipótese/comparação irreal","Tempo","Condição real"], 1, "dificil", "Como se...", "USP 2021"),
            _Q("(FUVEST 2016) Verb of perception (see, hear) + object + ___:", ["to+verb","bare infinitive/-ing","past","future"], 1, "dificil", "I saw him run/running", "FUVEST 2016"),
            _Q("(USP 2020) 'Not only... but also' é:", ["Contraste","Adição enfática","Causa","Tempo"], 1, "medio", "Correlação aditiva", "USP 2020"),
        ],
    },
}
