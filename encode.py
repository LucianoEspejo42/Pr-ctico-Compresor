import heapq
from collections import defaultdict
import struct
import json

def read_text_as_utf8(filename):
    try:
        with open(filename, 'rb') as file:
            read_text = ''
            while True:
                byte = file.read(1)
                if not byte:
                    break
                char = byte.decode('Windows-1252').encode('utf-8').decode('utf-8')
                read_text += char
            return read_text
    except FileNotFoundError:
        print(f"El archivo '{filename}' no se encuentra.")
        return None
    except UnicodeDecodeError:
        print("Error al decodificar el archivo.")
        return None

# Funciones BWT existentes...
def insert_shift(string):
    string = list(string)
    ultimo_caracter = string.pop()
    string.insert(0, ultimo_caracter)
    return ''.join(string)

def sort_headquarters(headquarters):
    heapq.heapify(headquarters)
    return [heapq.heappop(headquarters) for _ in range(len(headquarters))]

def obtain_bwt(headquarter):
    return ''.join(i[-1] for i in headquarter)

def bwt(string):
    headquarter = list()
    for i in range(len(string)):
        string = insert_shift(string)
        headquarter.append(string)
        headquarter = sort_headquarters(headquarter)
    return (obtain_bwt(headquarter), find_index(headquarter, string))

def find_index(headquarter, string):
    return headquarter.index(string)

# Funciones de codificación Shannon
def calculate_conditional_probabilities(sequence):
    context_counts = defaultdict(lambda: defaultdict(int))
    for i in range(2, len(sequence)):
        context = sequence[i-2:i]
        symbol = sequence[i]
        context_counts[context][symbol] += 1
    
    conditional_probabilities = {}
    for context, counts in context_counts.items():
        total = sum(counts.values())
        conditional_probabilities[context] = {symbol: count / total for symbol, count in counts.items()}
    return conditional_probabilities

def shannon_coding(conditional_probabilities):
    codes = defaultdict(dict)
    for context, probs in conditional_probabilities.items():
        sorted_probs = sorted(probs.items(), key=lambda item: item[1], reverse=True)
        for i, (symbol, prob) in enumerate(sorted_probs):
            codes[context][symbol] = format(i, f'0{len(sorted_probs)}b')
    return codes

def encode_sequence(sequence, codes):
    encoded_seq = []
    for i in range(2, len(sequence)):
        context = sequence[i-2:i]
        symbol = sequence[i]
        if context in codes and symbol in codes[context]:
            encoded_seq.append(codes[context][symbol])
        else:
            print(f"No se encontró el código para el contexto '{context}' y el símbolo '{symbol}'")
            return None
    return ''.join(encoded_seq)

import struct

def shannon_dict_to_bytearray(shannon_codes):
    byte_array = bytearray()
    
    for context, symbols in shannon_codes.items():
        # Convertir el contexto (2 caracteres) a bytes ASCII y agregar al bytearray
        byte_array.extend(context.encode('ascii'))
        
        # Agregar el número de símbolos para este contexto
        byte_array.append(len(symbols))
        
        for symbol, binary_code in symbols.items():
            # Convertir el símbolo a un solo byte ASCII
            byte_array.append(ord(symbol))
            
            # Convertir la cadena binaria a un entero y empaquetarla en bytes
            code_length = len(binary_code)
            binary_value = int(binary_code, 2)
            
            # Guardar la longitud del código binario y el valor en el bytearray
            byte_array.append(code_length)  # Guardar la longitud
            byte_array.extend(struct.pack('>I', binary_value)[-1:])  # Guardar solo los bits necesarios
        
    return byte_array

def add_header(binary_string):
    # Calcular la cantidad de bits de padding necesarios
    required_bits = (8 - ((len(binary_string) + 3) % 8)) % 8
    
    # Añadir el padding al final de la secuencia
    binary_string += '0' * required_bits
    
    # Añadir los bits de padding al principio de la cabecera como 3 bits
    return format(required_bits, '03b') + binary_string

def save_compressed_file(filename, bwt_result, index_bwt, codes, compressed_sequence):
    with open(filename, 'wb') as file:
        # Escribir index_bwt como entero de 2 bytes
        file.write(index_bwt.to_bytes(2, byteorder='big'))
        
        # Escribir los primeros dos dígitos de bwt_result
        initial_context = bwt_result[:2].encode('utf-8')
        file.write(initial_context)
        
        # Serializar y escribir codes de Shannon
        context_list = list(codes.keys())
        file.write(len(context_list).to_bytes(1, byteorder='big'))  # Cantidad de contextos
        
        for context in context_list:
            # Codificar contexto y escribirlo
            context_bytes = context.encode('utf-8')
            file.write(len(context_bytes).to_bytes(1, byteorder='big'))  # Longitud del contexto
            file.write(context_bytes)  # Contexto
            
            symbols = codes[context]
            file.write(len(symbols).to_bytes(1, byteorder='big'))  # Cantidad de símbolos en el contexto
            
            for symbol, code in symbols.items():
                symbol_bytes = symbol.encode('utf-8')
                file.write(len(symbol_bytes).to_bytes(1, byteorder='big'))  # Longitud del símbolo
                file.write(symbol_bytes)  # Símbolo
                
                # Código en bits
                code_int = int(code, 2)
                num_bits = len(code)
                file.write(num_bits.to_bytes(1, byteorder='big'))
                
                # Convertir a bytes y escribir el código binario
                num_bytes = (num_bits + 7) // 8
                code_bytes = code_int.to_bytes(num_bytes, byteorder='big')
                file.write(code_bytes)
        
        # Calcular la cantidad de bits de padding
        required_bits = (8 - ((len(compressed_sequence) + 3) % 8)) % 8
        
        # Añadir padding al inicio de la secuencia comprimida
        padded_sequence = format(required_bits, '03b') + compressed_sequence
        
        # Rellenar con ceros al final para asegurar múltiplo de 8
        padded_sequence += '0' * required_bits
        
        # Convertir la secuencia padded en bytes
        byte_data = bytearray(int(padded_sequence[i:i+8], 2) for i in range(0, len(padded_sequence), 8))
        
        # Escribir los bytes de la secuencia
        file.write(byte_data)

# Ejemplo de uso
if __name__ == '__main__':

    nombre_archivo = input("Ingrese el nombre del archivo: ")

    if not nombre_archivo.endswith(".txt"):
        nombre_archivo += ".txt"

    # Paso 1: Leer el archivo original
    texto_original = read_text_as_utf8(nombre_archivo)
    if texto_original is None:
        exit(1)
    # Paso 2: Aplicar BWT
    print("Aplicando BWT...")
    bwt_result, index_bwt = bwt(texto_original)
    
    # Paso 3: Calcular probabilidades y códigos Shannon
    print("Calculando códigos Shannon...")
    conditional_probs = calculate_conditional_probabilities(bwt_result)
    shannon_code = shannon_coding(conditional_probs)

    #print(shannon_code)
    
    # Paso 4: Codificar secuencia
    print("Codificando secuencia...")
    secuencia_comprimida = encode_sequence(bwt_result, shannon_code)
    if secuencia_comprimida is None:
        print("Error en la codificación")
        exit(1)
    
    # Paso 5: Guardar el archivo comprimido
    print("Guardando archivo comprimido...")
    save_compressed_file('comprimido.bwtsh', bwt_result[:2], index_bwt, shannon_code, secuencia_comprimida)
    
    # Paso 6: Mostrar estadísticas de compresión
    import os
    original_size = len(texto_original.encode('utf-8'))
    compressed_size = os.path.getsize('comprimido.bwtsh')
  
    
    print(f"\nEstadísticas de compresión:")
    print(f"Tamaño original: {original_size} bytes")
    print(f"Tamaño comprimido: {compressed_size} bytes")
