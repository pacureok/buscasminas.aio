# main.py en Replit (VERSION COMPLETA con RS, GO, SQL, META y Output Dir)
import re
import os
import json # Para manejar configuración JSON/diccionarios simples

# Función para leer el bloque <meta> y extraer configuraciones
def parse_meta_block(content):
    meta_match = re.search(r'<meta>(.*?)</meta>', content, re.DOTALL)
    if meta_match:
        meta_content = meta_match.group(1).strip()
        config = {}
        # Simple parser para key=value o key = ["item1", "item2"]
        for line in meta_content.split(','):
            line = line.strip()
            if not line or line.startswith('#'): continue # Ignorar líneas vacías o comentarios
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    config[key] = [item.strip().strip('"') for item in value[1:-1].split(',')]
                else:
                    config[key] = value.strip('"') # Remover comillas si existen
        return config
    return {}

# Esta función lee un archivo .aio y extrae los bloques de código
def parse_aio_file(file_path):
    print(f"\n--- Procesando archivo: {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
        return None

    # Obtener configuración del bloque <meta>
    config = parse_meta_block(content)

    # Patrones para encontrar los bloques de código con expresiones regulares
    blocks = {
        'html': re.findall(r'<video>(.*?)</video>', content, re.DOTALL),
        'css': re.findall(r'<cs>(.*?)</cs>', content, re.DOTALL),
        'js': re.findall(r'<tp>(.*?)</tp>', content, re.DOTALL),
        'esp': re.findall(r'\(esp\)(.*?)\(/esp\)', content, re.DOTALL),
        'ing': re.findall(r'<ING>(.*?)</ING>', content, re.DOTALL),
        'net': re.findall(r'<net>(.*?)</net>', content, re.DOTALL),
        'lua': re.findall(r'<lua>(.*?)</lua>', content, re.DOTALL),
        'pat': re.findall(r'\(pat\)(.*?)\(/pat\)', content, re.DOTALL),
        'rs': re.findall(r'<rs>(.*?)</rs>', content, re.DOTALL),   # Nuevo patrón para Rust
        'go': re.findall(r'<go>(.*?)</go>', content, re.DOTALL),   # Nuevo patrón para Go
        'sql': re.findall(r'<sql>(.*?)</sql>', content, re.DOTALL), # Nuevo patrón para SQL
        'meta_block': re.findall(r'<meta>(.*?)</meta>', content, re.DOTALL) # Para guardar el contenido bruto del meta si es necesario
    }
    return blocks, config

# Esta función guardará cada bloque en un archivo separado
def save_blocks_to_files(blocks, config, base_name):
    output_dir = config.get('output_dir', '.') # Usar 'build' si está en meta, sino '.'

    if not os.path.exists(output_dir) and output_dir != '.':
        os.makedirs(output_dir)
        print(f"Directorio de salida '{output_dir}/' creado.")

    # Nombres de archivo, ahora con directorio de salida
    html_output_path = os.path.join(output_dir, 'index.html')
    css_output_path = os.path.join(output_dir, 'style.css')
    js_output_path = os.path.join(output_dir, 'script.js')
    
    esp_output_path = os.path.join(output_dir, f'logic_{base_name}.esp')
    ing_output_path = os.path.join(output_dir, f'logic_{base_name}.ing')
    pat_output_path = os.path.join(output_dir, f'patterns_{base_name}.pat')

    net_output_path = os.path.join(output_dir, f'Program_{base_name}.cs')
    lua_output_path = os.path.join(output_dir, f'main_{base_name}.lua')
    rs_output_path = os.path.join(output_dir, f'src/main_{base_name}.rs') # Rust típicamente en src/
    go_output_path = os.path.join(output_dir, f'main_{base_name}.go')
    sql_output_path = os.path.join(output_dir, f'schema_{base_name}.sql')
    meta_output_path = os.path.join(output_dir, f'config_{base_name}.meta') # Opcional: guardar el meta bruto

    if blocks['html']:
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write(f"<title>{config.get('project_name', 'Aio Project')}</title>\n")
            f.write(f"<link rel='stylesheet' href='{os.path.basename(css_output_path)}'>\n") # Usar solo el nombre del archivo CSS
            f.write("</head>\n<body>\n")
            f.write(blocks['html'][0].strip())
            f.write(f"\n<script src='{os.path.basename(js_output_path)}'></script>\n</body>\n</html>")
        print(f"'{html_output_path}' generado con éxito.")
    
    if blocks['css']:
        with open(css_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['css'][0].strip())
        print(f"'{css_output_path}' generado con éxito.")

    if blocks['js']:
        with open(js_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['js'][0].strip())
        print(f"'{js_output_path}' generado con éxito.")
            
    if blocks['esp']:
        with open(esp_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['esp'][0].strip())
        print(f"Lógica (esp) guardada en '{esp_output_path}'.")
            
    if blocks['ing']:
        with open(ing_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['ing'][0].strip())
        print(f"Lógica (ING) guardada en '{ing_output_path}'.")

    if blocks['pat']:
        with open(pat_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['pat'][0].strip())
        print(f"Patrones (pat) guardados en '{pat_output_path}'.")

    if blocks['net']:
        with open(net_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['net'][0].strip())
        print(f"Código .NET (C#) guardado en '{net_output_path}'.")

    if blocks['lua']:
        with open(lua_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['lua'][0].strip())
        print(f"Código Lua guardado en '{lua_output_path}'.")

    if blocks['rs']: # Nuevo: Rust
        # Crear directorio src si no existe para Rust
        rust_src_dir = os.path.join(output_dir, 'src')
        if not os.path.exists(rust_src_dir):
            os.makedirs(rust_src_dir)
        with open(rs_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['rs'][0].strip())
        print(f"Código Rust guardado en '{rs_output_path}'.")
    
    if blocks['go']: # Nuevo: Go
        with open(go_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['go'][0].strip())
        print(f"Código Go guardado en '{go_output_path}'.")

    if blocks['sql']: # Nuevo: SQL
        with open(sql_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['sql'][0].strip())
        print(f"Código SQL guardado en '{sql_output_path}'.")

    if blocks['meta_block']: # Opcional: guardar el contenido bruto del meta
        with open(meta_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['meta_block'][0].strip())
        print(f"Configuración meta guardada en '{meta_output_path}'.")


# --- Aquí comienza la ejecución del programa ---
print("Buscando archivos .aio en el directorio actual...")
aio_files_found = [f for f in os.listdir('.') if f.endswith('.aio')]

if not aio_files_found:
    print("No se encontraron archivos .aio en el directorio actual.")
else:
    for aio_file in aio_files_found:
        base_name = os.path.splitext(aio_file)[0]
        aio_code_blocks, config = parse_aio_file(aio_file)
        if aio_code_blocks:
            save_blocks_to_files(aio_code_blocks, config, base_name)
    print("\nProcesamiento de todos los archivos .aio completado.")
