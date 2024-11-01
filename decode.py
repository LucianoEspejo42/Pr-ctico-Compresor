def add_header(binary_string):
    # Calcular la cantidad de bits de padding necesarios
    required_bits = (8 - ((len(binary_string) + 3) % 8)) % 8
    
    # Añadir el padding al final de la secuencia
    binary_string += '0' * required_bits
    
    # Añadir los bits de padding al principio de la cabecera como 3 bits
    return format(required_bits, '03b') + binary_string

def remove_header(compressed_sequence):
    # Extraer los primeros 3 bits que representan la cantidad de bits de padding
    padding_bits = int(compressed_sequence[:3], 2)
    
    # Eliminar los primeros 3 bits de padding y los bits de relleno al final
    compressed_sequence = compressed_sequence[3:]
    if padding_bits > 0:
        compressed_sequence = compressed_sequence[:-padding_bits]
    
    return compressed_sequence

def load_compressed_file(filename):
    with open(filename, 'rb') as file:
        # Leer índice BWT (2 bytes)
        index_bwt = int.from_bytes(file.read(2), byteorder='big')
        
        # Leer contexto inicial (2 bytes)
        initial_context = file.read(2).decode('utf-8')
        
        # Leer códigos Shannon
        codes = {}
        num_contexts = int.from_bytes(file.read(1), byteorder='big')
        
        for _ in range(num_contexts):
            # Leer contexto
            context_length = int.from_bytes(file.read(1), byteorder='big')
            context = file.read(context_length).decode('utf-8')
            
            # Leer símbolos para este contexto
            num_symbols = int.from_bytes(file.read(1), byteorder='big')
            context_codes = {}
            
            for _ in range(num_symbols):
                # Leer símbolo
                symbol_length = int.from_bytes(file.read(1), byteorder='big')
                symbol = file.read(symbol_length).decode('utf-8')
                
                # Leer código binario
                num_bits = int.from_bytes(file.read(1), byteorder='big')
                code_bytes = file.read((num_bits + 7) // 8)
                code = bin(int.from_bytes(code_bytes, byteorder='big'))[2:].zfill(num_bits)
                
                context_codes[symbol] = code
            
            codes[context] = context_codes

        # Leer los datos comprimidos
        compressed_data = file.read()
        
        # Convertir a secuencia de bits
        compressed_sequence = ''.join(format(byte, '08b') for byte in compressed_data)
        
        return index_bwt, initial_context, codes, compressed_sequence

def shannon_decode(codes, compressed_sequence, initial_context):
    # Eliminar el header y los bits de padding
    compressed_sequence = remove_header(compressed_sequence)
    
    decoded_sequence = list(initial_context)
    
    while len(compressed_sequence) > 0:
        current_context = ''.join(decoded_sequence[-2:])
        
        # Verificar si existe el contexto
        if current_context not in codes:
            print(f"Error: Contexto '{current_context}' no encontrado")
            break
        
        # Buscar el código correspondiente
        found_match = False
        for symbol, code in codes[current_context].items():
            if compressed_sequence.startswith(code):
                decoded_sequence.append(symbol)
                compressed_sequence = compressed_sequence[len(code):]
                found_match = True
                break
        
        # Si no se encuentra coincidencia, romper para evitar bucle infinito
        if not found_match:
            print("Error: No se encontró coincidencia para el contexto actual")
            break
    
    return ''.join(decoded_sequence)

def inverse_bwt(bwt_sequence, index):
    table = [''] * len(bwt_sequence)
    for i in range(len(bwt_sequence)):
        table = sorted(bwt_sequence[i] + table[i] for i in range(len(bwt_sequence)))
    
    return table[index]

def decompress_file(compressed_filename, output_filename):
    
    # Descomprimir el archivo
    index_bwt, initial_context, codes, compressed_sequence = load_compressed_file(compressed_filename)
    
    print("Obteniendo texto original...")
    # Decodificar la secuencia
    decoded_sequence = shannon_decode(codes, compressed_sequence, initial_context)
    
    # Aplicar BWT inverso
    original_text = inverse_bwt(decoded_sequence, index_bwt)
    
    # Guardar texto original
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(original_text)
    
    return original_text

if __name__ == '__main__':
    print("Descomprimiendo el archivo...")
    # Descomprimir el archivo
    original_text = decompress_file('comprimido.bwtsh', 'descompress.txt')
    print("Archivo descomprimido exitosamente.")
    import os
    decompress_size = os.path.getsize('descompress.txt')
    original_file = os.path.getsize('texto_original.txt')
    
    print(f"\nEstadísticas de compresión:")
    print(f"Tamaño del archivo original: {original_file} bytes")
    print(f"Tamaño del archivo descomprimido: {decompress_size} bytes")