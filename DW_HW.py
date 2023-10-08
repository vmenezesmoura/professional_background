from math import pi, log
import sys

def K_to_C(K, D, Q):
    a = 0.53*(K/D) + 0.094*(K/D)**0.225
    b = 88*(K/D)**0.44
    c = 1.62*(K/D)**0.134
    A = pi*D**2/4
    V = Q/A
    Re = V*D/0.000001
    f = a + b*Re**(-c) #simplificada de Wood
    J_DW = 0.0826* f * Q**2/D**5
    C = (J_DW * D**4.87 * Q**(-1.85) /10.643)**(-1/1.85)
    return (Re, C)

def C_to_K(C, D, Q):
    J_HW = 10.643* C**(-1.85) * D**(-4.87) * Q**1.85
    f = J_HW*D**5 / (0.0826*Q**2)
    A = pi*D**2/4
    V = Q/A
    Re = V*D/0.000001
    K = D/(10**((1/f**0.5 - 1.14)/2)) #simplificada de Karman-Prandtl (turbulento)
    return (Re, K)

while True:
    print('***Pressione ENTER a qualquer momento para sair***')
    print('Você deseja:\n(1) Transformar K em C (Wood)\n(2) Transformar C em K (Karman-Prandtl - inoperante)\n\t1')
    try:
        #apenas é aceitável a transformação de K em C, por enquanto
        escolha = 1#int(input('Você deseja:\n(1) Transformar K em C (Wood)\n(2) Transformar C em K (Karman-Prandtl - inoperante)\n\t'))
    except Exception as e:
        raise e('Entrada inválida!')
    else:
        if escolha == 1:
            K = float(input('Entre com o valor de K (mm): '))
            D = float(input('Entre com o valor de D (mm): '))
            Q = float(input('Entre com o valor de Q (L/s): '))
            resposta = K_to_C(K, D, Q)
            print(f'\tC_equivalente = {int(round(resposta[1], 0))}\n\tRe = {round(resposta[0], 1)}')
        elif escolha == 2:
            C = float(input('Entre com o valor de C: '))
            D = float(input('Entre com o valor de D (m): '))
            Q = float(input('Entre com o valor de Q (m³/s): '))
            resposta = C_to_K(C, D, Q)
            print(f'\tK_equivalente (m) = {round(resposta[1], 2)}\n\tRe = {round(resposta[0], 1)}')
        else:
            sys.exit()