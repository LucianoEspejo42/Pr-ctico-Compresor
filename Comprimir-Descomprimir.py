import collections
from collections import defaultdict
import math
import numpy as np

def burrows_wheeler_transform(s):
    """Aplica la Transformada de Burrows-Wheeler."""
    table = sorted(s[i:] + s[:i] for i in range(len(s)))
    last_column = ''.join(row[-1] for row in table)
    return last_column, table.index(s)

def burrows_wheeler_inverse(last_column, idx):
    """Aplica la Transformada de Burrows-Wheeler inversa."""
    table = [''] * len(last_column)
    for i in range(len(last_column)):
        table = sorted(last_column[i] + table[i] for i in range(len(last_column)))
    return table[idx]

# Función para calcular las probabilidades condicionales (Markov de orden 2)
def calculate_conditional_probabilities(sequence):
    context_counts = defaultdict(lambda: defaultdict(int))
    for i in range(2, len(sequence)):
        context = sequence[i-2:i]  # Los dos símbolos anteriores (contexto)
        symbol = sequence[i]       # El símbolo actual
        context_counts[context][symbol] += 1
    
    # Convertimos las cuentas a probabilidades
    conditional_probabilities = {}
    for context, counts in context_counts.items():
        total = sum(counts.values())
        conditional_probabilities[context] = {symbol: count / total for symbol, count in counts.items()}
    
    return conditional_probabilities

# Función para aplicar el algoritmo de Shannon y generar los códigos
def shannon_coding(conditional_probabilities):
    codes = {}
    
    for context, probs in conditional_probabilities.items():
        sorted_probs = sorted(probs.items(), key=lambda item: item[1], reverse=True)
        code = ""
        for i, (symbol, prob) in enumerate(sorted_probs):
            # Asignamos códigos binarios
            codes[(context, symbol)] = format(i, f'0{len(sorted_probs)}b')  
    
    return codes

# Función para decodificar una secuencia usando Shannon con Markov de orden 2
def decode_sequence(encoded_sequence, initial_context, codes):
    decoded_sequence = list(initial_context)  # Iniciamos con el contexto inicial (dos primeros símbolos)
    
    i = 0
    while i < len(encoded_sequence):
        context = ''.join(decoded_sequence[-2:])  # Obtenemos los últimos dos símbolos como contexto
        # Buscamos cuál símbolo tiene asignado el código actual en ese contexto
        for (ctx, symbol), code in codes.items():
            if ctx == context and encoded_sequence.startswith(code, i):
                decoded_sequence.append(symbol)
                i += len(code)  # Avanzamos en la secuencia codificada
                break
    
    return ''.join(decoded_sequence)

# Función para codificar la secuencia
def encode_sequence(sequence, codes):
    encoded_seq = []
    for i in range(2, len(sequence)):
        context = sequence[i-2:i]  # Los dos símbolos anteriores
        symbol = sequence[i]       # El símbolo actual
        encoded_seq.append(codes.get((context, symbol), ''))  # Codificar el símbolo dado el contexto
    return ''.join(encoded_seq)

# Función para comprimir la secuencia
def compress(sequence):
    bwt_result, original_index = burrows_wheeler_transform(sequence)
    print(f"\nResultado BWT: {bwt_result} (Índice original: {original_index})")

    probabilidad_condicional = calculate_conditional_probabilities(bwt_result)

    shannon_code = shannon_coding(probabilidad_condicional)

    secuencia_comprimida =encode_sequence(bwt_result, shannon_code)

    print("Probabilidades condicionales:")
    for context, prob_dict in probabilidad_condicional.items():
        print(f"Contexto {context}: {prob_dict}")

    print("\nCódigos Shannon:")
    for (context, symbol), code in shannon_code.items():
        print(f"Contexto {context}, símbolo '{symbol}' → código: {code}")

    return secuencia_comprimida, shannon_code, bwt_result, original_index

if __name__ == '__main__':
    sequence = input("Ingrese la secuencia a comprimir: ")

    compressed_seq, shannon_code, bwt_result, index_bwt = compress(sequence)
    print(f"\nSecuencia comprimida: {compressed_seq}")

    decode_sequence = decode_sequence(compressed_seq, bwt_result[:2],shannon_code)

    print(f"Sequencia descomprimida: {burrows_wheeler_inverse(decode_sequence, index_bwt)}")


    #print(burrows_wheeler_inverse(compressed_seq, original_index))
    #decompressed_seq = burrows_wheeler_inverse(compressed_seq, original_index)
    #print(f"\nSecuencia descomprimida: {decompressed_seq}")