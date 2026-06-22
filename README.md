# Calculadora IEEE 754 — Precisão Simples (32 bits)

Trabalho prático da disciplina de **Cálculo Numérico** do curso de Engenharia de Software do Centro Universitário Filadélfia (UniFil).

Professora: Tânia Camila Kochmanscky Goulart

---

## Sobre o projeto

O programa converte números decimais para o formato **IEEE 754 de precisão simples (32 bits)** e realiza operações de soma seguindo o mesmo algoritmo que o hardware usa — tudo implementado do zero, sem bibliotecas de conversão prontas.

A ideia foi entender de verdade o que acontece por baixo quando o computador armazena um número com vírgula: como ele divide em sinal, expoente e mantissa, por que números como `0.1` não têm representação exata em binário, e o que isso causa nos cálculos.

---

## O que o código faz

- Converte qualquer número decimal para os 3 campos IEEE 754: **sinal (1 bit)**, **expoente (8 bits, viés 127)** e **mantissa (23 bits)**
- Converte de volta (IEEE 754 → decimal) para validar o resultado
- Soma dois números seguindo o algoritmo real: alinha expoentes, soma mantissas, normaliza
- Compara o resultado da calculadora com a operação nativa do Python e mostra a diferença

---

## Como executar

Só precisa do Python 3 instalado, sem dependências externas.

```bash
python ieee754_calculadora.py
```

---

## Exemplo de saída

```
>>> PARTE 1 - Conversao dos 3 numeros escolhidos

  Numero: 13.75
  Sinal     : 0
  Expoente  : 10000010  (decimal: 130 - 127 = 3)
  Mantissa  : 10111000000000000000000
  32 bits   : 0 | 10000010 | 10111000000000000000000
  Convertido de volta: 13.75  |  Erro: 0.00e+00

  Numero: -0.1
  Sinal     : 1
  Expoente  : 01111011  (decimal: 123 - 127 = -4)
  Mantissa  : 10011001100110011001100
  32 bits   : 1 | 01111011 | 10011001100110011001100
  Convertido de volta: -0.09999999403953552  |  Erro: 5.96e-09

>>> PARTE 2 - Calculadora: soma de dois numeros

  Entrada A = 0.1   ->  0 | 01111011 | 10011001100110011001100
  Entrada B = 0.2   ->  0 | 01111100 | 10011001100110011001100

  Pela calculadora (32 bits manual) : 0.29999998211860657
  Pela operacao normal do Python    : 0.30000000000000004
  Valor exato esperado              : 0.3

  Bits iguais quando convertidos para 32 bits? SIM
```

---

## Por que 0.1 + 0.2 ≠ 0.3?

O sistema binário só representa exatamente frações cujo denominador é potência de 2 (1/2, 1/4, 1/8...). O número 0.1 = 1/10, e 10 tem o fator 5 — que não é potência de 2. Então a representação em binário vira uma dízima periódica infinita, e com só 23 bits de mantissa ela precisa ser cortada em algum ponto. Esse corte é o erro de arredondamento.

É o mesmo problema de tentar escrever 1/3 em decimal com um número finito de casas.

---

## Funções implementadas

| Função | Descrição |
|---|---|
| `decimal_para_ieee754(n)` | Converte n para os 32 bits IEEE 754 |
| `ieee754_para_decimal(bits)` | Reconstrói o float a partir dos 32 bits |
| `somar_ieee754(a, b)` | Soma seguindo o algoritmo IEEE 754 |
| `mostrar_campos(n, rep)` | Exibe os campos formatados |

---

## Referências

- VIANA, Gerardo Valdisio Rodrigues. *Padrão IEEE 754 para Aritmética Binária de Ponto Flutuante*. UECE.
- KNUTH, Donald E. *The Art of Computer Programming*, v. 2. Addison-Wesley, 1998.
- ANSI/IEEE Std 754-1985 — *IEEE Standard for Binary Floating-Point Arithmetic*.
