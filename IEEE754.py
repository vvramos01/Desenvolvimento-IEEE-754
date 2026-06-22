"""
Calculadora IEEE 754 - Precisão Simples (32 bits)
Autor: Vitoria Viviane Ramos da Silva
Curso: Engenharia de Software B
Instituição: Centro Universitário Filadélfia
Disciplina: Cálculo Numérico - Ponto Flutuante
Professora: Tânia Camila Kochmanscky Goulart
"""

import struct


def float_para_ieee754(numero: float) -> dict:
    """
    Converte um número decimal para representação IEEE 754 de precisão simples (32 bits).
    Implementado manualmente sem uso de biblioteca pronta para a conversão.

    Retorna um dicionário com:
      - sinal (str): '0' ou '1'
      - expoente (str): 8 bits do expoente com viés 127
      - mantissa (str): 23 bits da fração normalizada
      - binario_completo (str): 32 bits totais
      - expoente_decimal (int): valor do expoente sem viés
    """
    # trata o caso especial do zero
    if numero == 0.0:
        return {
            "sinal": "0",
            "expoente": "00000000",
            "mantissa": "0" * 23,
            "binario_completo": "0" * 32,
            "expoente_decimal": 0
        }

    # --- 1. Determinar o bit de sinal ---
    if numero < 0:
        sinal = "1"
        numero = abs(numero)
    else:
        sinal = "0"

    # 2 converter a parte inteira para binario
    parte_inteira = int(numero)
    parte_fracionaria = numero - parte_inteira

    # converte parte inteira para binario
    if parte_inteira == 0:
        bin_inteiro = "0"
    else:
        bin_inteiro = ""
        temp = parte_inteira
        while temp > 0:
            bin_inteiro = str(temp % 2) + bin_inteiro
            temp //= 2

    # 3 converte a parte fracionária para binario 
    bin_fracionario = ""
    temp_frac = parte_fracionaria
    # ate 30 bits de precisao para a fraçao
    for _ in range(30):
        temp_frac *= 2
        if temp_frac >= 1:
            bin_fracionario += "1"
            temp_frac -= 1
        else:
            bin_fracionario += "0"
        if temp_frac == 0:
            break

    #4 montar o numero binario completo
    numero_binario = bin_inteiro + "." + bin_fracionario

    # 5 normalizar: forma 1.xxxxx × 2^e
    if parte_inteira > 0:
        # parte inteira com digitos: mover ponto para depois do primeiro '1'
        pos_ponto = len(bin_inteiro) - 1       # posição do ponto na representaçao
        expoente = pos_ponto                    # deslocamento a esquerda
        mantissa_completa = bin_inteiro[1:] + bin_fracionario
    else:
        # parte inteira zero: encontrar primeiro '1' na fração
        pos_primeiro_um = -1
        for i, bit in enumerate(bin_fracionario):
            if bit == "1":
                pos_primeiro_um = i
                break
        if pos_primeiro_um == -1:
            # numero muito pequeno, todos zeros — tratar como zero
            return {
                "sinal": sinal,
                "expoente": "00000000",
                "mantissa": "0" * 23,
                "binario_completo": sinal + "0" * 31,
                "expoente_decimal": 0
            }
        expoente = -(pos_primeiro_um + 1)
        mantissa_completa = bin_fracionario[pos_primeiro_um + 1:]

    # 6 calcular expoente com viés 127
    expoente_viesado = expoente + 127

    # Converter expoente para 8 bits binários
    bin_expoente = ""
    temp_exp = expoente_viesado
    for _ in range(8):
        bin_expoente = str(temp_exp % 2) + bin_expoente
        temp_exp //= 2

    # 7 extrair 23 bits da mantissa (fração após o '1.' implícito)
    # completar com zeros se necessário, truncar se maior
    mantissa_23 = (mantissa_completa + "0" * 23)[:23]

    # 8 montar os 32 bits finais ---
    binario_completo = sinal + bin_expoente + mantissa_23

    return {
        "sinal": sinal,
        "expoente": bin_expoente,
        "mantissa": mantissa_23,
        "binario_completo": binario_completo,
        "expoente_decimal": expoente
    }


def ieee754_para_float(bits: str) -> float:
    """
    Converte uma string de 32 bits (IEEE 754) de volta para float decimal.
    """
    sinal = int(bits[0])
    expoente_viesado = int(bits[1:9], 2)
    mantissa_bits = bits[9:32]

    expoente = expoente_viesado - 127

    #reconstruir valor da mantissa: 1 + soma(bit_i / 2^i)
    valor_mantissa = 1.0
    for i, bit in enumerate(mantissa_bits):
        if bit == "1":
            valor_mantissa += 2 ** (-(i + 1))

    valor = ((-1) ** sinal) * (2 ** expoente) * valor_mantissa
    return valor


def somar_ieee754(a: float, b: float) -> dict:
    """
    Soma dois floats usando a representação IEEE 754 (32 bits) implementada manualmente.
    Segue o algoritmo padrão de adição em ponto flutuante:
      1. Alinhar expoentes
      2. Somar mantissas
      3. Normalizar resultado
    """
    rep_a = float_para_ieee754(a)
    rep_b = float_para_ieee754(b)

    exp_a = rep_a["expoente_decimal"]
    exp_b = rep_b["expoente_decimal"]

    # reconstituir mantissas como inteiros de 24 bits (1 implícito + 23)
    mant_a_int = int("1" + rep_a["mantissa"], 2)
    mant_b_int = int("1" + rep_b["mantissa"], 2)

    # alinhar expoentes (deslocar a mantissa do menor para a direita)
    if exp_a >= exp_b:
        diff = exp_a - exp_b
        mant_b_int >>= diff
        exp_result = exp_a
    else:
        diff = exp_b - exp_a
        mant_a_int >>= diff
        exp_result = exp_b

    # considera sinais
    if rep_a["sinal"] == "1":
        mant_a_int = -mant_a_int
    if rep_b["sinal"] == "1":
        mant_b_int = -mant_b_int

    mant_result = mant_a_int + mant_b_int

    # determinar sinal do resultado
    sinal_result = "0"
    if mant_result < 0:
        sinal_result = "1"
        mant_result = abs(mant_result)

    # normalizar: encontrar posição do bit mais significativo
    if mant_result == 0:
        return {
            "resultado_decimal_calculadora": 0.0,
            "resultado_ieee754": float_para_ieee754(0.0),
            "resultado_decimal_python": a + b
        }

    # ajusta expoente e mantissa para forma normalizada 1.xxx
    bit_len = mant_result.bit_length()
    if bit_len > 24:
        shift = bit_len - 24
        mant_result >>= shift
        exp_result += shift
    elif bit_len < 24:
        shift = 24 - bit_len
        mant_result <<= shift
        exp_result -= shift

    # extrair os 23 bits da mantissa (descartando o 1 implícito)
    mantissa_final = bin(mant_result)[2:][1:]  # remove '0b' e o '1' inicial
    mantissa_final = (mantissa_final + "0" * 23)[:23]

    # expoente com viés
    exp_viesado = exp_result + 127
    bin_exp = format(exp_viesado, "08b")

    bits_resultado = sinal_result + bin_exp + mantissa_final
    resultado_decimal = ieee754_para_float(bits_resultado)

    return {
        "resultado_decimal_calculadora": resultado_decimal,
        "resultado_ieee754": {
            "sinal": sinal_result,
            "expoente": bin_exp,
            "mantissa": mantissa_final,
            "binario_completo": bits_resultado,
            "expoente_decimal": exp_result
        },
        "resultado_decimal_python": a + b
    }


def exibir_representacao(numero: float, rep: dict):
    """
    Exibe de forma clara os campos da representação IEEE 754 de um número.
    """
    print(f"\n  Número decimal: {numero}")
    print(f"  Sinal     (1 bit):  {rep['sinal']}")
    print(f"  Expoente  (8 bits): {rep['expoente']}  →  valor decimal: {rep['expoente_decimal'] + 127} - 127 = {rep['expoente_decimal']}")
    print(f"  Mantissa (23 bits): {rep['mantissa']}")
    print(f"  Representação completa (32 bits):")
    bits = rep["binario_completo"]
    print(f"  {bits[0]} {bits[1:9]} {bits[9:32]}")
    print(f"  (sinal) (expoente) (mantissa)")


# ============================================================
# programa principal
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  CALCULADORA IEEE 754 - Precisão Simples (32 bits)")
    print("  Vitoria Viviane Ramos da Silva")
    print("  Centro Universitário Filadélfia - Engenharia de Software B")
    print("=" * 60)

    # parte 1: conversão de 3 números escolhidos
    print("\n" + "=" * 60)
    print("  PARTE 1 — Conversão de 3 números para IEEE 754")
    print("=" * 60)

    numeros_parte1 = [13.75, -0.1, 100.5]

    for num in numeros_parte1:
        print(f"\n{'─'*50}")
        rep = float_para_ieee754(num)
        exibir_representacao(num, rep)

        # validaçao: converter de volta e comparar
        valor_recuperado = ieee754_para_float(rep["binario_completo"])
        print(f"\n  Validação (conversão inversa): {valor_recuperado}")
        diff = abs(num - valor_recuperado)
        print(f"  Diferença (erro de representação): {diff:.2e}")

    # parte 2: Calculadora com dois numeros fornecidos
    print("\n" + "=" * 60)
    print("  PARTE 2 — Calculadora IEEE 754: Soma de dois números")
    print("=" * 60)

    # numeros de entrada para a calculadora
    a = 0.1
    b = 0.2

    print(f"\n  Número A = {a}")
    print(f"  Número B = {b}")

    rep_a = float_para_ieee754(a)
    rep_b = float_para_ieee754(b)

    print("\n--- Representação IEEE 754 do número A ---")
    exibir_representacao(a, rep_a)

    print("\n--- Representação IEEE 754 do número B ---")
    exibir_representacao(b, rep_b)

    # realizar a soma
    resultado = somar_ieee754(a, b)

    print("\n--- Resultado da Soma ---")
    print(f"\n  A + B (calculadora IEEE 754): {resultado['resultado_decimal_calculadora']}")
    print(f"  A + B (operação normal Python): {resultado['resultado_decimal_python']}")

    rep_res = resultado["resultado_ieee754"]
    print("\n  Representação IEEE 754 do resultado:")
    exibir_representacao(resultado["resultado_decimal_calculadora"], rep_res)

    # comparaçao e analise
    print("\n--- Análise dos resultados ---")
    calc = resultado["resultado_decimal_calculadora"]
    py = resultado["resultado_decimal_python"]
    esperado = 0.3

    print(f"\n  Valor esperado matematicamente: {esperado}")
    print(f"  Resultado pela calculadora:      {calc}")
    print(f"  Resultado pelo Python (a + b):   {py}")
    print(f"\n  Diferença entre calculadora e Python: {abs(calc - py):.2e}")
    print(f"  Diferença em relação ao valor exato:  {abs(py - esperado):.2e}")

    # comparaçao dos bits
    bits_calc = rep_res["binario_completo"]
    rep_py = float_para_ieee754(py)
    bits_py = rep_py["binario_completo"]

    print(f"\n  Bits do resultado (calculadora): {bits_calc}")
    print(f"  Bits do resultado (Python):       {bits_py}")
    print(f"  Bits idênticos? {'SIM' if bits_calc == bits_py else 'NÃO — há diferença nos bits!'}")

    print("\n" + "=" * 60)
    print("  Fim da execução")
    print("=" * 60)
