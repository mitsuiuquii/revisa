"""Novo seed data reorganizado por CONTEÚDO + DIFICULDADE.
Estrutura: Matéria -> Conteúdo (tema) -> Lição com Dificuldade específica"""

SUBJECTS_SEED = [
    {"name": "Matemática", "icon": "Calculator", "color": "#3B82F6", "description": "Funções, geometria, álgebra, trigonometria"},
    {"name": "Biologia", "icon": "Leaf", "color": "#86EFAC", "description": "Citologia, genética, ecologia, fisiologia"},
]

# Novo formato: CONTENT_BANK[Matéria][Conteúdo][Dificuldade] = Lista de questões
def Q(prompt, options, ci, exp, source):
    return {"prompt": prompt, "options": options, "correct_index": ci, "explanation": exp, "source": source}

CONTENT_BANK = {
    "Matemática": {
        # CONTEÚDO 1: Aritmética Básica
        "Aritmética Básica": {
            "basico": [
                Q("Quanto é 3/4 + 1/2?", ["3/8","5/4","4/6","2/3"], 1, "3/4 + 2/4 = 5/4", "UFPR 2010"),
                Q("O valor de 2³ × 2² é:", ["32","16","8","64"], 0, "2³⁺² = 2⁵ = 32", "UERJ 2012"),
                Q("Qual o MMC de 12 e 18?", ["6","24","36","72"], 2, "MMC(12,18)=36", "UFMG 2008"),
                Q("25% de 200 vale:", ["25","40","50","75"], 2, "200·0,25 = 50", "ENEM 2014"),
                Q("Resolva: 3x = 21:", ["3","6","7","21"], 2, "x = 21/3 = 7", "UFRJ 2009"),
                Q("Se 3/5 de um reservatório de água estão cheios, qual a porcentagem que falta para enchê-lo?", ["20%", "40%", "60%", "80%"], 1, "3/5 = 60%, logo faltam 40%", "ENEM 2011"),
                Q("O resultado da expressão 10 + 10 × 10 - 10 ÷ 10 é:", ["109", "100", "99", "10"], 0, "Seguindo a ordem: 10 + 100 - 1 = 109", "VUNESP 2014"),
                Q("Em uma cidade, 2/3 dos moradores são adultos. Se há 600 moradores no total, quantos são adultos?", ["200", "300", "400", "500"], 2, "(2/3) de 600 = 1200 / 3 = 400", "UERJ (Adaptada)"),
                Q("O valor da potência (0,2)² é:", ["0,4", "0,04", "0,004", "4"], 1, "0,2 × 0,2 = 0,04", "IFSP 2013"),
                Q("Um automóvel consome 1 litro de combustível a cada 12 km. Quantos litros gastará em uma viagem de 300 km?", ["20", "25", "30", "35"], 1, "300 km ÷ 12 km/l = 25 litros", "FUVEST (Baseada)"),
                Q("Um bife de 200g tem 15% de gordura. Qual a massa de gordura, em gramas, nesse bife?", ["15g", "25g", "30g", "45g"], 2, "200 × 0,15 = 30", "ENEM 2010"),
                Q("Se x + 7 = 15, o valor de x² é:", ["8", "16", "64", "225"], 2, "x = 15 - 7 = 8; x² = 8² = 64", "CESGRANRIO"),
                Q("A terça parte de 3 elevado a 10 é:", ["1 elevado a 10", "3 elevado a 9", "3 elevado a 3", "9 elevado a 10"], 1, "3¹⁰ / 3¹ = 3¹⁰⁻¹ = 3⁹", "FATEC")
            ],
            "intermediario": [
                Q("Se f(x)=2x+5, então f(3) vale:", ["6","8","11","13"], 2, "2·3+5=11", "FUVEST 2011"),
                Q("As raízes de x²−7x+12=0 são:", ["1 e 12","3 e 4","2 e 6","-3 e -4"], 1, "Soma 7, produto 12 → 3 e 4", "UFMG 2013"),
                Q("Uma PA tem a₁=3, razão 4. O 5º termo é:", ["15","19","23","27"], 1, "a₅ = 3 + 4·4 = 19", "ENEM 2018"),
                Q("A média aritmética de cinco números é 7. Se o número 3 for retirado do conjunto, qual será a nova média aritmética?", ["7", "8", "9", "10"], 1, "Soma original = 5 × 7 = 35. Nova soma = 35 - 3 = 32. Nova média = 32 / 4 = 8", "FUVEST"),
                Q("Um produto que custava R$ 100,00 sofreu um aumento de 20% e, em seguida, um desconto de 20%. Qual o preço final?", ["R$ 100,00", "R$ 96,00", "R$ 104,00", "R$ 80,00"], 1, "100 × 1,20 = 120; 120 × 0,80 = 96", "ENEM"),
                Q("Se 6 operários levam 10 dias para completar uma obra, quantos dias 12 operários, com a mesma produtividade, levariam?", ["20", "5", "15", "10"], 1, "Grandezas inversamente proporcionais: 6 × 10 = 12 × x -> 60 = 12x -> x = 5", "VUNESP"),
                Q("Em um mapa de escala 1:500.000, a distância entre duas cidades é de 10 cm. Qual a distância real em quilômetros?", ["5 km", "50 km", "500 km", "5.000 km"], 1, "10 cm × 500.000 = 5.000.000 cm = 50.000 m = 50 km", "UERJ"),
                Q("Um investidor aplica R$ 1.000,00 a juros simples de 3% ao mês. Qual será o montante (capital + juros) após 4 meses?", ["R$ 1.120,00", "R$ 1.030,00", "R$ 1.125,50", "R$ 1.200,00"], 0, "J = 1000 × 0,03 × 4 = 120. Montante = 1000 + 120 = 1120", "FGV"),
                Q("João gastou 1/3 do seu salário com aluguel e 1/4 do que sobrou com alimentação. Que fração do salário total restou?", ["1/2", "1/4", "5/12", "7/12"], 0, "Sobrou 2/3. Gastou 1/4 de 2/3 = 2/12 = 1/6. Resto final: 2/3 - 1/6 = 4/6 - 1/6 = 3/6 = 1/2", "UNESP"),
                Q("A razão entre o número de homens e mulheres em uma sala é de 2 para 3. Se há 12 homens, qual o total de pessoas na sala?", ["18", "24", "30", "36"], 2, "2/3 = 12/x -> 2x = 36 -> x = 18 mulheres. Total = 12 + 18 = 30", "PUC-SP")
            ],
            "avancado": [
                Q("A soma dos 10 primeiros termos de uma PA com a₁=2 e razão 3 é:", ["155","165","175","185"], 0, "S = n(a₁+aₙ)/2 = 10·(2+29)/2 = 155", "ENEM 2019"),
                Q("(1+i)² no plano complexo:", ["2i","1+2i","2+2i","0"], 0, "1+2i+i² = 1+2i-1 = 2i", "FUVEST 2017"),
                Q("Resolva 2ˣ⁺¹ = 16:", ["2","3","4","5"], 1, "2ˣ⁺¹=2⁴ → x=3", "UNICAMP 2018"),
                Q("Se log 2 = 0,30 e log 3 = 0,48, o valor de log 15 é:", ["1,18", "0,78", "1,08", "1,28"], 0, "log 15 = log(30/2) = log 3 + log 10 - log 2 = 0,48 + 1 - 0,30 = 1,18", "FATEC"),
                Q("O 20º termo da progressão aritmética (2, 9, 16, ...) é:", ["135", "140", "142", "149"], 0, "a20 = a1 + 19r = 2 + 19(7) = 2 + 133 = 135", "FUVEST"),
                Q("O valor da expressão i¹⁰¹ + i¹⁰² + i¹⁰³ + i¹⁰⁴, onde i é a unidade imaginária, é:", ["0", "1", "-1", "i"], 0, "A soma de quatro potências consecutivas de i é sempre zero", "MACKENZIE"),
                Q("O montante de R$ 1.000,00 após 2 meses a juros compostos de 10% ao mês é:", ["R$ 1.200,00", "R$ 1.210,00", "R$ 1.100,00", "R$ 1.110,00"], 1, "M = C(1+i)ⁿ = 1000 * (1,1)² = 1000 * 1,21 = 1210", "ENEM"),
                Q("O resto da divisão do número 2¹⁰⁰ por 3 é:", ["0", "1", "2", "3"], 1, "2 ≡ -1 (mod 3); logo 2¹⁰⁰ ≡ (-1)¹⁰⁰ = 1 (mod 3)", "OBM"),
                Q("De quantas maneiras diferentes 4 pessoas podem se sentar em uma fila de 4 cadeiras?", ["4", "8", "16", "24"], 3, "P4 = 4! = 4 * 3 * 2 * 1 = 24", "VUNESP"),
                Q("A soma dos termos da progressão geométrica infinita (1, 1/2, 1/4, 1/8, ...) é:", ["1,5", "2", "2,5", "3"], 1, "S = a1 / (1 - q) = 1 / (1 - 0,5) = 1 / 0,5 = 2", "UNICAMP"),
                Q("Se log₂ x + log₂ (x - 2) = 3, o valor real de x é:", ["2", "4", "6", "8"], 1, "log₂(x²-2x)=3 -> x²-2x=8 -> x²-2x-8=0. Raízes 4 e -2 (x>2)", "UNESP"),
                Q("O valor de log₂ 0,25 é:", ["2", "-2", "0,5", "-0,5"], 1, "log₂ (1/4) = log₂ (2⁻²) = -2", "UECE")
            ],
        },
        
        # CONTEÚDO 2: Geometria
        "Geometria": {
            "basico": [
                Q("Área de retângulo 8×5 cm:", ["13","26","30","40"], 3, "A = 8·5 = 40 cm²", "UERJ 2010"),
                Q("Perímetro de triângulo equilátero lado 6:", ["12","18","24","36"], 1, "3·6=18", "FUVEST 2010"),
                Q("Volume de cubo aresta 5 cm:", ["25","50","100","125"], 3, "5³=125 cm³", "ENEM 2018"),
                Q("Se uma piscina quadrada tem área total de 400 m², qual a medida de cada um de seus lados?", ["10m", "20m", "40m", "100m"], 1, "L² = 400 -> L = √400 = 20", "ENEM 2012"),
                Q("Um campo de futebol retangular tem 100m de comprimento e 70m de largura. Qual seu perímetro?", ["170m", "340m", "7000m", "240m"], 1, "P = 2 × (100 + 70) = 340m", "VUNESP"),
                Q("Em um triângulo retângulo, um dos ângulos agudos mede 35°. Quanto mede o outro ângulo agudo?", ["35°", "45°", "55°", "65°"], 2, "90° + 35° + x = 180° -> x = 55°", "FUVEST"),
                Q("Um cabo de aço sustenta um poste de 12m de altura. Se o cabo está preso ao chão a 5m da base, qual seu comprimento?", ["13m", "15m", "17m", "20m"], 0, "x² = 12² + 5² = 144 + 25 = 169 -> x = 13", "UFRJ"),
                Q("Qual o suplemento de um ângulo que mede 70°?", ["20°", "110°", "180°", "290°"], 1, "Ângulos suplementares somam 180°. 180 - 70 = 110", "UERJ"),
                Q("Uma praça circular tem 50m de raio. Usando π = 3, qual o comprimento aproximado de uma volta completa?", ["150m", "300m", "600m", "900m"], 1, "C = 2 × π × r = 2 × 3 × 50 = 300", "ENEM 2013"),
                Q("Um triângulo possui dois ângulos internos medindo 60° cada. Este triângulo é classificado como:", ["Isósceles", "Escaleno", "Retângulo", "Equilátero"], 3, "O terceiro ângulo também mede 60° (180-60-60), logo todos os lados são iguais", "MACKENZIE"),
                Q("Qual a área de um triângulo que possui base de 8 cm e altura de 5 cm?", ["13 cm²", "20 cm²", "40 cm²", "80 cm²"], 1, "Área = (base × altura) / 2 = (8 × 5) / 2 = 20", "UNESP"),
                Q("Um terreno retangular de 25m por 10m terá uma cerca em todo o seu contorno. Quantos metros de cerca serão necessários?", ["35m", "50m", "70m", "250m"], 2, "Perímetro = 2 × (25 + 10) = 70", "IFSP")
            ],
            "intermediario": [
                Q("sen(60°) =", ["1/2","√2/2","√3/2","1"], 2, "Valor notável", "UNICAMP 2014"),
                Q("Razão de proporção entre 18 e 24:", ["1/2","2/3","3/4","4/5"], 2, "18/24 = 3/4", "FUVEST 2009"),
                Q("Num triângulo ABC, os lados AB e AC medem 4 e 5, e o ângulo entre eles é de 60 graus. O lado BC mede:", ["raiz de 21", "raiz de 61", "raiz de 31", "9"], 0, "a² = 4² + 5² - 2 * 4 * 5 * cos 60 = 16 + 25 - 20 = 21", "FUVEST"),
                Q("Um cilindro circular reto tem raio da base 3 cm e altura 10 cm. O volume desse cilindro, em cm³, é:", ["30 pi", "60 pi", "90 pi", "100 pi"], 2, "V = pi * r² * h = pi * 3² * 10 = 90 pi", "VUNESP"),
                Q("A distância entre os pontos A(1, 2) e B(4, 6) no plano cartesiano é:", ["3", "4", "5", "7"], 2, "d = raiz de ((4-1)² + (6-2)²) = raiz de (3² + 4²) = 5", "UECE"),
                Q("A soma dos ângulos internos de um hexágono regular é:", ["360 graus", "540 graus", "720 graus", "900 graus"], 2, "S = (n-2) * 180 = (6-2) * 180 = 720", "MACKENZIE"),
                Q("Um mestre de obras usa uma régua de 1m para medir a sombra de um prédio. A régua tem sombra de 0,5m e o prédio de 20m. A altura do prédio é:", ["10m", "40m", "30m", "50m"], 1, "Por semelhança: H/1 = 20/0,5 resulta em H = 40", "ENEM"),
                Q("No triângulo retângulo, se sen(x) = 3/5 e a hipotenusa é 10, o valor do cateto oposto a x é:", ["3", "6", "8", "5"], 1, "sen(x) = CO/H -> 3/5 = x/10 -> x = 6", "UNESP"),
                Q("A área de um setor circular de raio 6 cm e ângulo central de 60 graus é:", ["3 pi cm²", "6 pi cm²", "12 pi cm²", "36 pi cm²"], 1, "A = (60/360) * pi * 6² = (1/6) * 36 pi = 6 pi", "IFSP"),
                Q("A área de um triângulo com lados 6 cm e 8 cm e ângulo entre eles de 30 graus é:", ["12 cm²", "24 cm²", "48 cm²", "6 cm²"], 0, "A = (1/2) * a * b * sen(30) = 0,5 * 6 * 8 * 0,5 = 12", "UNICAMP"),
                Q("Se o volume de um cubo é 64 cm³, sua área total é:", ["16 cm²", "64 cm²", "96 cm²", "384 cm²"], 2, "L³ = 64 -> L = 4. Área total = 6 * L² = 6 * 16 = 96", "UFMG"),
                Q("Um ângulo inscrito em uma circunferência que subentende um arco de 180 graus (diâmetro) mede:", ["45 graus", "90 graus", "180 graus", "60 graus"], 1, "O ângulo inscrito é metade do arco central: 180/2 = 90", "PUC-PR")
            ],
            "avancado": [
                Q("Equação da circunferência centro (1,2) raio 3:", ["(x−1)²+(y−2)²=9","x²+y²=9","(x+1)²+(y+2)²=9","x²+y²=3"], 0, "Forma reduzida", "UERJ 2017"),
                Q("Determinante de [[3,0],[2,5]]:", ["10","15","17","21"], 1, "3·5−0·2=15", "UERJ 2018"),
                Q("Qual o raio da circunferência de equação x² + y² - 4x + 6y - 12 = 0?", ["3", "4", "5", "25"], 2, "Completando quadrados: (x-2)² + (y+3)² = 25. Logo, R² = 25 e R = 5", "MACKENZIE"),
                Q("Qual a razão entre o volume de uma esfera e o volume de um cilindro circular reto circunscrito a ela?", ["1/2", "2/3", "3/4", "1"], 1, "V_esfera = (4/3) * pi * R³. V_cilindro = pi * R² * 2R = 2 * pi * R³. Dividindo um pelo outro, sobra 2/3", "UFRGS"),
                Q("A distância da origem (0,0) à reta de equação 3x + 4y - 10 = 0 no plano cartesiano é:", ["2", "4", "5", "10"], 0, "d = módulo(30 + 40 - 10) / raiz de (3² + 4²) = 10 / raiz de 25 = 10 / 5 = 2", "PUC-RJ"),
                Q("Um cone circular reto tem raio da base 3 cm e geratriz 5 cm. O seu volume, em cm³, é:", ["12 pi", "15 pi", "36 pi", "60 pi"], 0, "Por Pitágoras: h² + 3² = 5² resulta em h = 4. Volume = (1/3) * pi * 3² * 4 = 12 pi", "VUNESP"),
                Q("O raio da circunferência inscrita em um triângulo retângulo de lados medindo 3 cm, 4 cm e 5 cm é:", ["1 cm", "1,5 cm", "2 cm", "2,5 cm"], 0, "Área = semiperímetro * raio -> 6 = ((3+4+5)/2) * r -> 6 = 6 * r -> r = 1", "FUVEST"),
                Q("As retas de equações y = 2x + 1 e y = -x + 4 se interceptam no ponto:", ["(1, 3)", "(2, 5)", "(0, 1)", "(-1, 5)"], 0, "Igualando: 2x + 1 = -x + 4 -> 3x = 3 -> x = 1. Substituindo x=1 em qualquer equação, achamos y=3", "UNESP"),
                Q("A diagonal de um paralelepípedo retângulo cujas dimensões são 2 cm, 3 cm e 6 cm mede:", ["5 cm", "7 cm", "9 cm", "11 cm"], 1, "D = raiz de (2² + 3² + 6²) = raiz de (4 + 9 + 36) = raiz de 49 = 7", "UERJ"),
                Q("O comprimento do eixo maior da elipse de equação x²/25 + y²/9 = 1 é:", ["3", "5", "6", "10"], 3, "A equação padrão é x²/a² + y²/b² = 1. Logo, a² = 25, o que dá a = 5. O eixo maior é 2a = 10", "UFSCar"),
                Q("A área de um hexágono regular de lado 2 cm é:", ["3 * raiz de 3", "6 * raiz de 3", "12 * raiz de 3", "24 * raiz de 3"], 1, "A área de 1 hexágono equivale a 6 triângulos equiláteros: 6 * (L² * raiz de 3 / 4) = 6 * (4 * raiz de 3 / 4) = 6 * raiz de 3", "UDESC")
            ],
        },

        # CONTEÚDO 3: Trigonometria
        "Trigonometria": {
            "basico": [
                Q("sen(90°) − cos(0°):", ["0","1","-1","2"], 0, "1−1=0", "USP 2020"),
            ],
            "intermediario": [
                Q("tg(45°) =", ["0","1","√2","√3/3"], 1, "Tangente de 45° = 1", "UFMG 2017"),
                Q("log₂(8) =", ["2","3","4","8"], 1, "2³=8", "UFPR 2015"),
            ],
            "avancado": [
                Q("Número complexo i² vale:", ["i","-1","1","0"], 1, "Definição: i²=-1", "FUVEST 2014"),
            ],
        },
    },
    
    "Biologia": {
        # CONTEÚDO 1: Citologia
        "Citologia": {
            "basico": [
                Q("A unidade básica de todos os seres vivos é:", ["Tecido","Órgão","Célula","Sistema"], 2, "Célula = unidade da vida", "UFMG 2008"),
                Q("Onde ocorre a fotossíntese?", ["Mitocôndria","Cloroplasto","Núcleo","Vacúolo"], 1, "Nos cloroplastos", "ENEM 2013"),
                Q("Insulina é um:", ["Carboidrato","Hormônio","Vitamina","Mineral"], 1, "Hormônio do pâncreas", "UFRJ 2012"),
            ],
            "intermediario": [
                Q("Material genético está principalmente no(a):", ["Citoplasma","Núcleo","Membrana","Ribossomo"], 1, "DNA no núcleo", "FUVEST 2011"),
                Q("ATP é produzido majoritariamente em:", ["Lisossomo","Mitocôndria","Golgi","Vacúolo"], 1, "Cadeia respiratória mitocondrial", "UNICAMP 2014"),
            ],
            "avancado": [
                Q("Síntese proteica ocorre nos:", ["Cloroplastos","Ribossomos","Lisossomos","Vacúolos"], 1, "Tradução do mRNA", "FUVEST 2014"),
            ],
        },
        
        # CONTEÚDO 2: Genética
        "Genética": {
            "basico": [
                Q("Cromossomos sexuais femininos:", ["XY","XX","XO","YY"], 1, "XX", "UFMG 2014"),
                Q("Cromossomos somáticos humanos:", ["23","44","46","48"], 2, "23 pares = 46", "UFMG 2010"),
            ],
            "intermediario": [
                Q("Tipo sanguíneo doador universal:", ["A","B","AB","O−"], 3, "O− doa para todos", "UERJ 2013"),
                Q("Reprodução assexuada gera:", ["Variabilidade","Cópias geneticamente iguais","Gametas","Mutação"], 1, "Sem combinação genética", "ENEM 2015"),
                Q("Meiose ocorre nas células:", ["Somáticas","Germinativas","Musculares","Nervosas"], 1, "Formação de gametas", "UNICAMP 2016"),
            ],
            "avancado": [
                Q("Cariótipo humano tem:", ["22 pares","23 pares","24 pares","25 pares"], 1, "46 = 23 pares", "UFRJ 2016"),
                Q("Transcrição gênica produz:", ["DNA","mRNA","Proteína","Lipídio"], 1, "RNA mensageiro a partir do DNA", "UERJ 2019"),
            ],
        },

        # CONTEÚDO 3: Ecologia
        "Ecologia": {
            "basico": [
                Q("Reino dos cogumelos:", ["Plantae","Fungi","Animalia","Protista"], 1, "Reino Fungi", "UERJ 2010"),
            ],
            "intermediario": [
                Q("Ecossistema é formado por:", ["Só seres vivos","Bióticos + abióticos","Apenas solo","Apenas água"], 1, "Interação dos fatores", "UFMG 2015"),
            ],
            "avancado": [
                Q("Ciclo do carbono envolve:", ["Apenas respiração","Fotossíntese, respiração, decomposição","Só combustão","Apenas animais"], 1, "Múltiplos processos", "USP 2020"),
            ],
        },
    },
}

ACHIEVEMENTS_SEED = [
    {"name": "Iniciante", "description": "Completou primeira lição", "icon": "Zap", "criteria": {"lessons_completed": 1}},
    {"name": "Persistente", "description": "Completou 10 lições", "icon": "Flame", "criteria": {"lessons_completed": 10}},
    {"name": "Streaker", "description": "Manteve 7 dias de sequência", "icon": "Heart", "criteria": {"streak_days": 7}},
    {"name": "Campeão", "description": "Alcançou 100 XP", "icon": "Trophy", "criteria": {"xp": 100}},
    {"name": "Mestre", "description": "Alcançou 1000 XP", "icon": "Crown", "criteria": {"xp": 1000}},
]
