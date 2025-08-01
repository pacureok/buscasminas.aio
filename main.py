# main.py en Replit (VERSIÓN CON (pat) Y run_logic_from_...)
import re
import os

# Esta función lee un archivo .aio y extrae los bloques de código
def parse_aio_file(file_path):
    print(f"\n--- Procesando archivo: {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
        return None

    # Patrones para encontrar los bloques de código con expresiones regulares
    blocks = {
        'html': re.findall(r'<video>(.*?)</video>', content, re.DOTALL),
        'css': re.findall(r'<cs>(.*?)</cs>', content, re.DOTALL),
        'js': re.findall(r'<tp>(.*?)</tp>', content, re.DOTALL),
        'esp': re.findall(r'\(esp\)(.*?)\(/esp\)', content, re.DOTALL),
        'ing': re.findall(r'<ING>(.*?)</ING>', content, re.DOTALL),
        'net': re.findall(r'<net>(.*?)</net>', content, re.DOTALL),
        'lua': re.findall(r'<lua>(.*?)</lua>', content, re.DOTALL),
        'pat': re.findall(r'\(pat\)(.*?)\(/pat\)', content, re.DOTALL) # Nuevo patrón para (pat)
    }
    return blocks

# Esta función guardará cada bloque en un archivo separado
def save_blocks_to_files(blocks, base_name):
    html_output_name = 'index.html'
    css_output_name = 'style.css'
    js_output_name = 'script.js'
    esp_output_name = f'logic_{base_name}.esp'
    ing_output_name = f'logic_{base_name}.ing'
    net_output_name = f'Program_{base_name}.cs'
    lua_output_name = f'main_{base_name}.lua'
    pat_output_name = f'patterns_{base_name}.pat' # Nombre para el archivo (pat)

    if blocks['html']:
        with open(html_output_name, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write(f"<title>Buscaminas Aio - {base_name}</title>\n")
            f.write(f"<link rel='stylesheet' href='{css_output_name}'>\n")
            f.write("</head>\n<body>\n")
            f.write(blocks['html'][0].strip())
            f.write(f"\n<script src='{js_output_name}'></script>\n</body>\n</html>")
        print(f"'{html_output_name}' generado con éxito.")
    
    if blocks['css']:
        with open(css_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['css'][0].strip())
        print(f"'{css_output_name}' generado con éxito.")

    if blocks['js']:
        with open(js_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['js'][0].strip())
        print(f"'{js_output_name}' generado con éxito.")
            
    if blocks['esp']:
        with open(esp_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['esp'][0].strip())
        print(f"Lógica (esp) guardada en '{esp_output_name}'.")
            
    if blocks['ing']:
        with open(ing_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['ing'][0].strip())
        print(f"Lógica (ING) guardada en '{ing_output_name}'.")

    if blocks['net']:
        with open(net_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['net'][0].strip())
        print(f"Código .NET (C#) guardado en '{net_output_name}'.")

    if blocks['lua']:
        with open(lua_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['lua'][0].strip())
        print(f"Código Lua guardado en '{lua_output_name}'.")

    if blocks['pat']: # Nuevo bloque (pat)
        with open(pat_output_name, 'w', encoding='utf-8') as f:
            f.write(blocks['pat'][0].strip())
        print(f"Patrones (pat) guardados en '{pat_output_name}'.")


# --- Aquí comienza la ejecución del programa ---
print("Buscando archivos .aio en el directorio actual...")
aio_files_found = [f for f in os.listdir('.') if f.endswith('.aio')]

if not aio_files_found:
    print("No se encontraron archivos .aio en el directorio actual.")
else:
    for aio_file in aio_files_found:
        base_name = os.path.splitext(aio_file)[0]
        aio_code_blocks = parse_aio_file(aio_file)
        if aio_code_blocks:
            save_blocks_to_files(aio_code_blocks, base_name)
    print("\nProcesamiento de todos los archivos .aio completado.")
