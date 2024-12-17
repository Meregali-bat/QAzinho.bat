import random

def generate_cpf():
    # Gerar os primeiros 9 dígitos aleatórios
    cpf = [random.randint(0, 9) for _ in range(9)]

    # Calcular o primeiro dígito verificador
    sum1 = sum((cpf[i] * (10 - i) for i in range(9)))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    cpf.append(digit1)

    # Calcular o segundo dígito verificador
    sum2 = sum((cpf[i] * (11 - i) for i in range(10)))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    cpf.append(digit2)

    return ''.join(map(str, cpf))