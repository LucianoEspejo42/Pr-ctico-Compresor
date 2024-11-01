<h1 align="center"> Práctico Teoría de la Información </h1>

Este proyecto implementa un compresor de archivos diseñado para reducir el tamaño de archivos mediante un enfoque de compresión en dos etapas:

- `Transformación Burrows-Wheeler (BWT)`
- `Codificación Shannon con Modelo de Markov de Orden 2`

## Pasos a seguir para la ejecución del proyecto 

- Ejecuta el archivo `encode.py`.
- Ingresa el nombre del archivo a comprimir. Puedes ingresar el nombre con o sin la extensión (.txt).
- Automáticamente comenzará la compresión del archivo, aplicando primero la Transformada de Burrows-Wheeler (BWT) y luego la codificación de Shannon con modelo de Markov de orden 2.
- Al finalizar la compresión, se generará un nuevo archivo llamado `comprimido.bwtsh`, y se mostrará en pantalla el tamaño del archivo original junto con el tamaño de este nuevo archivo.
- Finalmente, ejecuta el archivo `decode.py`. Este creará un archivo llamado `descompress.txt` donde se guardará la cadena decodificada, mostrando también en pantalla el tamaño de este archivo junto con el tamaño del archivo original.

## Actualizaciones
- Se dividio el programa en dos:`encode.py` y `decode.py`
- Se valida que el peso del archivo de entrada del `encode.py` coincida con el de salida del `decode.py`
