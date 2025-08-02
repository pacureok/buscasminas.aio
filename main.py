# main.py en Replit (VERSION CON SLN, XAML, CONFIG, CSPROJ y CREA block)
import re
import os
import json # Para manejar configuración JSON/diccionarios simples

# --- Funciones Auxiliares ---

# Función para leer el bloque <meta> y extraer configuraciones
def parse_meta_block(content):
    meta_match = re.search(r'<meta>(.*?)</meta>', content, re.DOTALL)
    if meta_match:
        meta_content = meta_match.group(1).strip()
        config = {}
        for line in meta_content.split(','):
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    config[key] = [item.strip().strip('"') for item in value[1:-1].split(',')]
                else:
                    config[key] = value.strip('"')
        return config
    return {}

# Función para procesar el bloque <crea>
def process_crea_block(crea_content, output_base_dir="."):
    print(f"\n--- Procesando bloque <crea> ---")
    commands = crea_content.split(',') # Dividir por coma para cada comando/linea

    for command_line in commands:
        command_line = command_line.strip()
        if not command_line or command_line.startswith('#'):
            continue # Ignorar líneas vacías o comentarios

        # --- Comando $crea file ---
        crea_match = re.match(r'\$crea\s+file\s+Name="([^"]+)"(?:\s+%extencion\s+(\.[a-zA-Z0-9]+))?(?:\s+%No_extension)?', command_line)
        if crea_match:
            file_name = crea_match.group(1)
            extension = crea_match.group(2)
            has_no_extension = '%No_extension' in command_line # Check if the flag is present

            final_file_name = file_name
            if extension and not has_no_extension:
                final_file_name = file_name + extension
            elif has_no_extension and '.' in file_name: # If No_extension is true but name has dot, remove extension
                final_file_name = file_name.rsplit('.', 1)[0]
            
            file_path = os.path.join(output_base_dir, final_file_name)
            
            # Asegurar que el directorio existe
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)

            try:
                with open(file_path, 'a', encoding='utf-8') as f: # 'a' para crear si no existe, o añadir.
                    pass # Solo crear el archivo vacío o tocarlo.
                print(f"  Archivo creado/tocado: '{file_path}'")
            except Exception as e:
                print(f"  Error al crear archivo '{file_path}': {e}")
            continue # Pasar al siguiente comando

        # --- Comando %borra ---
        borra_match = re.match(r'%borra\s+(?:file\s+Name="([^"]+)"|path="([^"]+)"(?:\s+%all|\s+Files=\[([^\]]+)\])(?:\s+IfCondition="([^"]+)")?)', command_line)
        if borra_match:
            # Capturas: (file_name para borra file) | (path para borra path) (all | files list) (condition)
            file_name_to_delete = borra_match.group(1)
            path_to_delete_from = borra_match.group(2)
            is_all = '%all' in command_line
            files_list_str = borra_match.group(3)
            condition_flag = borra_match.group(4) # Esto es conceptual por ahora

            # Lógica para la condición (muy básica, solo conceptual)
            execute_delete = True
            if condition_flag:
                # Aquí, en una implementación real, se evaluaría 'condition_flag'
                # Por ahora, simulamos que siempre es verdadero o que se imprime un aviso
                print(f"  Aviso: La condición '{condition_flag}' para borrar no se evalúa dinámicamente en este prototipo.")
                # execute_delete = (some_global_config_dict.get(condition_flag, False) == True)
            
            if not execute_delete:
                print(f"  Omitting delete command due to condition: {command_line}")
                continue


            if file_name_to_delete: # %borra file Name="...."
                file_path = os.path.join(output_base_dir, file_name_to_delete)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"  Archivo borrado: '{file_path}'")
                    except Exception as e:
                        print(f"  Error al borrar archivo '{file_path}': {e}")
                else:
                    print(f"  Advertencia: Archivo '{file_path}' no encontrado para borrar.")

            elif path_to_delete_from: # %borra path="..."
                target_path = os.path.join(output_base_dir, path_to_delete_from)
                if not os.path.exists(target_path):
                    print(f"  Advertencia: Ruta '{target_path}' no encontrada para borrar.")
                    continue

                if is_all: # %borra path="..." %all
                    try:
                        for item in os.listdir(target_path):
                            item_path = os.path.join(target_path, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                print(f"  Borrado: '{item_path}'")
                            elif os.path.isdir(item_path): # Opcional: borrar subdirectorios recursivamente
                                pass # Para este ejemplo, solo borramos archivos. Usar shutil.rmtree para directorios.
                        print(f"  Todos los archivos en '{target_path}' borrados.")
                    except Exception as e:
                        print(f"  Error al borrar todos los archivos en '{target_path}': {e}")
                
                elif files_list_str: # %borra path="..." Files=["file1", "file2"]
                    try:
                        # Parsear la lista de archivos (ej. "file1.html","file2.css")
                        files_to_delete_raw = [f.strip().strip('"') for f in files_list_str.split(',')]
                        for f_name in files_to_delete_raw:
                            file_path = os.path.join(target_path, f_name)
                            if os.path.exists(file_path) and os.path.isfile(file_path):
                                os.remove(file_path)
                                print(f"  Borrado: '{file_path}'")
                            else:
                                print(f"  Advertencia: Archivo '{file_path}' no encontrado o no es un archivo para borrar.")
                    except Exception as e:
                        print(f"  Error al borrar archivos específicos en '{target_path}': {e}")
            continue

        print(f"  Advertencia: Comando <crea> no reconocido o mal formado: '{command_line}'")


# --- Funciones Principales de Parsing y Guardado ---

# Esta función lee un archivo .aio y extrae los bloques de código
def parse_aio_file(file_path):
    print(f"\n--- Procesando archivo: {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
        return None, {}

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
        'rs': re.findall(r'<rs>(.*?)</rs>', content, re.DOTALL),
        'go': re.findall(r'<go>(.*?)</go>', content, re.DOTALL),
        'sql': re.findall(r'<sql>(.*?)</sql>', content, re.DOTALL),
        'sln': re.findall(r'<sln>(.*?)</sln>', content, re.DOTALL),   # Nuevo patrón para SLN
        'xaml': re.findall(r'<xaml>(.*?)</xaml>', content, re.DOTALL), # Nuevo patrón para XAML
        'config': re.findall(r'<config>(.*?)</config>', content, re.DOTALL), # Nuevo patrón para CONFIG
        'csproj': re.findall(r'<csproj>(.*?)</csproj>', content, re.DOTALL), # Nuevo patrón para CSPROJ
        'crea': re.findall(r'<crea>(.*?)</crea>', content, re.DOTALL), # Nuevo patrón para CREA
        'meta_block': re.findall(r'<meta>(.*?)</meta>', content, re.DOTALL) # Para guardar el contenido bruto del meta si es necesario
    }
    return blocks, config

# Esta función guardará cada bloque en un archivo separado
def save_blocks_to_files(blocks, config, base_name):
    output_dir = config.get('output_dir', '.')

    if not os.path.exists(output_dir) and output_dir != '.':
        os.makedirs(output_dir)
        print(f"Directorio de salida '{output_dir}/' creado.")

    # Rutas absolutas para los archivos de salida
    html_output_path = os.path.join(output_dir, 'index.html')
    css_output_path = os.path.join(output_dir, 'style.css')
    js_output_path = os.path.join(output_dir, 'script.js')
    
    # Archivos de lógica y otros
    esp_output_path = os.path.join(output_dir, f'logic_{base_name}.esp')
    ing_output_path = os.path.join(output_dir, f'logic_{base_name}.ing')
    pat_output_path = os.path.join(output_dir, f'patterns_{base_name}.pat')

    net_output_path = os.path.join(output_dir, f'Program_{base_name}.cs')
    lua_output_path = os.path.join(output_dir, f'main_{base_name}.lua')
    rs_output_path = os.path.join(output_dir, f'src/main_{base_name}.rs') # Rust típicamente en src/
    go_output_path = os.path.join(output_dir, f'main_{base_name}.go')
    sql_output_path = os.path.join(output_dir, f'schema_{base_name}.sql')

    # Archivos .NET de proyecto
    sln_output_path = os.path.join(output_dir, f'{base_name}.sln')
    xaml_output_path = os.path.join(output_dir, f'{base_name}.xaml')
    config_output_path = os.path.join(output_dir, f'App.config') # O Web.config
    csproj_output_path = os.path.join(output_dir, f'{base_name}.csproj')

    meta_output_path = os.path.join(output_dir, f'config_{base_name}.meta') # Opcional: guardar el meta bruto


    if blocks['html']:
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write(f"<title>{config.get('project_name', 'Aio Project')}</title>\n")
            f.write(f"<link rel='stylesheet' href='{os.path.basename(css_output_path)}'>\n")
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

    if blocks['rs']:
        rust_src_dir = os.path.join(output_dir, 'src')
        if not os.path.exists(rust_src_dir):
            os.makedirs(rust_src_dir)
        with open(rs_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['rs'][0].strip())
        print(f"Código Rust guardado en '{rs_output_path}'.")
    
    if blocks['go']:
        with open(go_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['go'][0].strip())
        print(f"Código Go guardado en '{go_output_path}'.")

    if blocks['sql']:
        with open(sql_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['sql'][0].strip())
        print(f"Código SQL guardado en '{sql_output_path}'.")

    # Nuevos bloques .NET
    if blocks['sln']:
        with open(sln_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['sln'][0].strip())
        print(f"Archivo de Solución (.sln) guardado en '{sln_output_path}'.")

    if blocks['xaml']:
        with open(xaml_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['xaml'][0].strip())
        print(f"Archivo XAML (.xaml) guardado en '{xaml_output_path}'.")

    if blocks['config']:
        with open(config_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['config'][0].strip())
        print(f"Archivo de Configuración (.config) guardado en '{config_output_path}'.")

    if blocks['csproj']:
        with open(csproj_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['csproj'][0].strip())
        print(f"Archivo de Proyecto C# (.csproj) guardado en '{csproj_output_path}'.")

    if blocks['meta_block']:
        with open(meta_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['meta_block'][0].strip())
        print(f"Configuración meta guardada en '{meta_output_path}'.")

    # Procesar el bloque <crea> DESPUÉS de haber generado todos los demás archivos
    # para que pueda operar sobre ellos si es necesario.
    if blocks['crea']:
        for crea_content_block in blocks['crea']:
            process_crea_block(crea_content_block, output_dir)


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
