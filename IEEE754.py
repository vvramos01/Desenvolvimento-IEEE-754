# Trabalho de Calculo Numerico - IEEE 754
# Vitoria Viviane Ramos da Silva
# Engenharia de Software B - Centro Universitario Filadelfia
# Professora: Tania Camila Kochmanscky Goulart
#
# Obs: fiz a conversao na mao, sem usar struct nem ctypes nem nada pronto.
# A ideia e converter decimal -> binario passo a passo, igual a gente fez no papel.


# -----------------------------------------------------------------------
# FUNCAO 1 - converte um numero decimal para IEEE 754 de 32 bits
# retorna um dicionario com os tres campos separados
# -----------------------------------------------------------------------
def decimal_para_ieee754(numero):

    # caso especial: zero nao tem como normalizar
    if numero == 0.0:
        return {
            "sinal":    "0",
            "expoente": "00000000",
            "mantissa": "00000000000000000000000",
            "completo": "0" * 32,
            "exp_real": 0
        }

    # --- bit de sinal ---
    if numero < 0:
        sinal = "1"
        numero = abs(numero)
    else:
        sinal = "0"

    # --- parte inteira em binario (divisoes por 2) ---
    parte_int  = int(numero)
    parte_frac = numero - parte_int

    if parte_int == 0:
        bin_int = "0"
    else:
        bin_int = ""
        n = parte_int
        while n > 0:
            bin_int = str(n % 2) + bin_int
            n = n // 2

    # --- parte fracionaria em binario (multiplicacoes por 2) ---
    # uso ate 30 iteracoes pra nao entrar em loop infinito com dizimas
    bin_frac = ""
    f = parte_frac
    for _ in range(30):
        f *= 2
        if f >= 1:
            bin_frac += "1"
            f -= 1
        else:
            bin_frac += "0"
        if f == 0:
            break   # terminou exato, pode parar

    # --- normalizacao para 1.xxxxx x 2^e ---
    if parte_int > 0:
        # desloca o ponto para logo apos o primeiro '1' da parte inteira
        expoente = len(bin_int) - 1
        # mantissa = resto da parte inteira + parte fracionaria (sem o 1 implicito)
        mantissa_bruta = bin_int[1:] + bin_frac
    else:
        # parte inteira eh zero: primeiro '1' esta na fracao
        pos = -1
        for i, b in enumerate(bin_frac):
            if b == "1":
                pos = i
                break
        if pos == -1:
            # numero muito pequeno, trato como zero
            return {
                "sinal":    sinal,
                "expoente": "00000000",
                "mantissa": "00000000000000000000000",
                "completo": sinal + "0" * 31,
                "exp_real": 0
            }
        expoente = -(pos + 1)
        mantissa_bruta = bin_frac[pos + 1:]

    # --- expoente com vies 127 ---
    exp_viesado = expoente + 127

    # converto o expoente para 8 bits (sem usar bin() pra mostrar o processo)
    bits_exp = ""
    e = exp_viesado
    for _ in range(8):
        bits_exp = str(e % 2) + bits_exp
        e = e // 2

    # --- 23 bits de mantissa (completa com zeros ou corta se precisar) ---
    mantissa_23 = (mantissa_bruta + "0" * 23)[:23]

    completo = sinal + bits_exp + mantissa_23

    return {
        "sinal":    sinal,
        "expoente": bits_exp,
        "mantissa": mantissa_23,
        "completo": completo,
        "exp_real": expoente
    }


# -----------------------------------------------------------------------
# FUNCAO 2 - converte de volta pra decimal (uso pra validar)
# -----------------------------------------------------------------------
def ieee754_para_decimal(bits):
    s   = int(bits[0])
    exp = int(bits[1:9], 2) - 127
    man = bits[9:]

    # reconstroi 1.mantissa
    valor = 1.0
    for i, b in enumerate(man):
        if b == "1":
            valor += 2 ** (-(i + 1))

    return ((-1) ** s) * (2 ** exp) * valor


# -----------------------------------------------------------------------
# FUNCAO 3 - soma dois floats no esquema IEEE 754 (32 bits, manual)
# -----------------------------------------------------------------------
def somar_ieee754(a, b):
    ra = decimal_para_ieee754(a)
    rb = decimal_para_ieee754(b)

    ea = ra["exp_real"]
    eb = rb["exp_real"]

    # pego as mantissas como inteiros de 24 bits (1 implicito na frente)
    ma = int("1" + ra["mantissa"], 2)
    mb = int("1" + rb["mantissa"], 2)

    # alinho os expoentes: o menor desloca pra direita
    if ea >= eb:
        dif = ea - eb
        mb >>= dif
        exp_resultado = ea
    else:
        dif = eb - ea
        ma >>= dif
        exp_resultado = eb

    # aplico os sinais
    if ra["sinal"] == "1":
        ma = -ma
    if rb["sinal"] == "1":
        mb = -mb

    soma = ma + mb

    sinal_r = "0"
    if soma < 0:
        sinal_r = "1"
        soma = abs(soma)

    if soma == 0:
        return {
            "decimal_calculadora": 0.0,
            "ieee754":             decimal_para_ieee754(0.0),
            "decimal_python":      a + b
        }

    # normalizo: ajusto ate ter exatamente 24 bits
    nbits = soma.bit_length()
    if nbits > 24:
        soma >>= (nbits - 24)
        exp_resultado += (nbits - 24)
    elif nbits < 24:
        soma <<= (24 - nbits)
        exp_resultado -= (24 - nbits)

    # tiro o 1 implicito e pego 23 bits
    man_final = bin(soma)[2:][1:]
    man_final = (man_final + "0" * 23)[:23]

    ev = exp_resultado + 127
    bits_e = format(ev, "08b")

    bits_r = sinal_r + bits_e + man_final
    valor_r = ieee754_para_decimal(bits_r)

    return {
        "decimal_calculadora": valor_r,
        "ieee754": {
            "sinal":    sinal_r,
            "expoente": bits_e,
            "mantissa": man_final,
            "completo": bits_r,
            "exp_real": exp_resultado
        },
        "decimal_python": a + b
    }


# -----------------------------------------------------------------------
# mostra os campos de forma organizada
# -----------------------------------------------------------------------
def mostrar_campos(numero, rep):
    bits = rep["completo"]
    print(f"\n  Numero: {numero}")
    print(f"  Sinal     : {rep['sinal']}")
    print(f"  Expoente  : {rep['expoente']}  (decimal: {rep['exp_real'] + 127} - 127 = {rep['exp_real']})")
    print(f"  Mantissa  : {rep['mantissa']}")
    print(f"  32 bits   : {bits[0]} | {bits[1:9]} | {bits[9:]}")


# ===================================================================
#  EXECUCAO PRINCIPAL
# ===================================================================
if __name__ == "__main__":

    print("=" * 62)
    print("  Calculadora IEEE 754 - Precisao Simples (32 bits)")
    print("  Vitoria Viviane Ramos da Silva")
    print("  UniFil - Engenharia de Software B")
    print("=" * 62)

    # ------------------------------------------------------------------
    # PARTE 1 - converto os 3 numeros manualmente
    # ------------------------------------------------------------------
    print("\n\n>>> PARTE 1 - Conversao dos 3 numeros escolhidos\n")

    escolhidos = [13.75, -0.1, 100.5]

    for num in escolhidos:
        print("-" * 50)
        rep = decimal_para_ieee754(num)
        mostrar_campos(num, rep)

        # valido convertendo de volta
        de_volta = ieee754_para_decimal(rep["completo"])
        erro = abs(num - de_volta)
        print(f"\n  Convertido de volta: {de_volta}")
        print(f"  Erro de representacao: {erro:.2e}")

    # ------------------------------------------------------------------
    # PARTE 2 - calculadora: solicita dois numeros, opera e compara
    # ------------------------------------------------------------------
    print("\n\n>>> PARTE 2 - Calculadora: soma de dois numeros\n")

    # os dois numeros de entrada
    a = 0.1
    b = 0.2
    print(f"  Entrada A = {a}")
    print(f"  Entrada B = {b}")

    rep_a = decimal_para_ieee754(a)
    rep_b = decimal_para_ieee754(b)

    print("\n--- IEEE 754 de A ---")
    mostrar_campos(a, rep_a)

    print("\n--- IEEE 754 de B ---")
    mostrar_campos(b, rep_b)

    resultado = somar_ieee754(a, b)

    print("\n--- Soma ---")
    print(f"\n  Pela calculadora (32 bits manual) : {resultado['decimal_calculadora']}")
    print(f"  Pela operacao normal do Python    : {resultado['decimal_python']}")
    print(f"  Valor exato esperado              : 0.3")

    print("\n  IEEE 754 do resultado:")
    mostrar_campos(resultado["decimal_calculadora"], resultado["ieee754"])

    # comparo os bits
    bits_calc = resultado["ieee754"]["completo"]
    bits_py   = decimal_para_ieee754(resultado["decimal_python"])["completo"]

    diff_decimal = abs(resultado["decimal_calculadora"] - resultado["decimal_python"])
    diff_exato   = abs(resultado["decimal_python"] - 0.3)

    print(f"\n--- Comparacao de bits ---")
    print(f"  Bits calculadora : {bits_calc}")
    print(f"  Bits Python (f32): {bits_py}")
    print(f"  Bits iguais?     : {'SIM' if bits_calc == bits_py else 'NAO - diferem!'}")

    print(f"\n--- Erros ---")
    print(f"  Diferenca calculadora x Python   : {diff_decimal:.4e}")
    print(f"  Diferenca Python x valor exato   : {diff_exato:.4e}")

    print("\n" + "=" * 62)
    print("  Fim")
    print("=" * 62)
