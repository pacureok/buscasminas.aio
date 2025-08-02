# main.py en Replit (VERSION COMPLETA con RS, GO, SQL, META, Output Dir, SLN, XAML, CONFIG, CSPROJ y CREA)
import re
import os
import json # Para manejar configuración JSON/diccionarios simples
import shutil # Para operaciones de borrado de directorios

# Placeholder para los estados de los pines de (esp)
# En una implementación real, esto vendría de un intérprete de (esp)
esp_pin_states = {
    "n": "si", # Por defecto, 'si' para game_over
    "p": "no",  # Por defecto, 'no' para victory
}

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

# Función para parsear el bloque <crea>
def parse_crea_block(crea_content, output_dir):
    commands = crea_content.split(',')
    
    print("\n--- Procesando comandos <crea> ---")
    for command in commands:
        cmd = command.strip()
        if not cmd or cmd.startswith('#'): continue

        # Comando $crea=file
        create_match = re.match(r'\$crea=file Name="([^"]+)"\s*(%extencion\s*\.([^,]+))?\s*(%Not_extencion)?', cmd)
        if create_match:
            name = create_match.group(1)
            extension = create_match.group(3)
            not_extension_flag = create_match.group(4)

            file_path = os.path.join(output_dir, name.replace('_', ' ')) # Reemplaza _ por espacio
            
            if not_extension_flag:
                # Si es %Not_extencion, intentar crear un directorio
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                    print(f"Directorio creado: '{file_path}'")
                else:
                    print(f"Directorio ya existe: '{file_path}'")
            else:
                # Crear un archivo con o sin extensión
                final_path = f"{file_path}.{extension}" if extension else file_path
                try:
                    with open(final_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Archivo creado por Aio: {os.path.basename(final_path)}\n")
                    print(f"Archivo creado: '{final_path}'")
                except Exception as e:
                    print(f"Error al crear archivo '{final_path}': {e}")
            continue

        # Comando %borra
        delete_match = re.match(r'%borra=(Name="([^"]+)"|file="([^"]+)")\s*(%all)?\s*(%([a-zA-Z0-9\.,]+))?\s*(&con\s*"([^"]+)")?', cmd)
        if delete_match:
            name_to_delete = delete_match.group(2)
            path_to_delete = delete_match.group(4)
            all_flag = delete_match.group(5)
            specific_files_str = delete_match.group(7) # Ej: index.html,ejemplo.c
            conditional_logic = delete_match.group(9) # Ej: "funcion_esp_que_devuelve_n"

            target_path = ""
            if name_to_delete:
                target_path = os.path.join(output_dir, name_to_delete.replace('_', ' '))
            elif path_to_delete:
                target_path = os.path.join(output_dir, path_to_delete.replace('_', ' '))
            
            # Evaluar la condición &con
            condition_met = True
            if conditional_logic:
                # Aquí es donde el intérprete de Aio real consultaría el estado de (esp)
                # Para esta demo, lo simulamos.
                pin_name = conditional_logic.strip('"')
                if pin_name in esp_pin_states:
                    if esp_pin_states[pin_name] == "no": # Asumimos "no" significa no ejecutar borrado
                        condition_met = False
                        print(f"Condición '{pin_name}' es 'no'. Borrado no ejecutado para '{target_path}'.")
                else:
                    print(f"Advertencia: Pin '{pin_name}' no encontrado en estados de (esp). Ejecutando borrado por defecto.")
            
            if not condition_met:
                continue # Saltar el borrado si la condición no se cumple

            # Ejecutar el borrado
            if all_flag: # %all
                if os.path.exists(target_path):
                    if os.path.isdir(target_path):
                        shutil.rmtree(target_path)
                        print(f"Directorio y contenido borrados: '{target_path}'")
                    else:
                        os.remove(target_path)
                        print(f"Archivo borrado: '{target_path}'")
                else:
                    print(f"Advertencia: '{target_path}' no encontrado para borrado %all.")
            elif specific_files_str: # %file1,file2,...
                files_to_delete = [f.strip() for f in specific_files_str.split(',')]
                for f_name in files_to_delete:
                    file_to_delete_path = os.path.join(target_path, f_name.replace('_', ' '))
                    if os.path.exists(file_to_delete_path) and os.path.isfile(file_to_delete_path):
                        os.remove(file_to_delete_path)
                        print(f"Archivo borrado: '{file_to_delete_path}'")
                    else:
                        print(f"Advertencia: '{file_to_delete_path}' no encontrado para borrado.")
            elif name_to_delete: # %borra=Name="ejemplo.js" (borra solo ese archivo en output_dir)
                if os.path.exists(target_path) and os.path.isfile(target_path):
                    os.remove(target_path)
                    print(f"Archivo borrado: '{target_path}'")
                else:
                    print(f"Advertencia: '{target_path}' no encontrado para borrado por nombre.")
            else:
                print(f"Error: Comando %borra inválido o incompleto: {cmd}")
            continue
        
        print(f"Advertencia: Comando <crea> no reconocido o mal formado: '{cmd}'")


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
        'rs': re.findall(r'<rs>(.*?)</rs>', content, re.DOTALL),
        'go': re.findall(r'<go>(.*?)</go>', content, re.DOTALL),
        'sql': re.findall(r'<sql>(.*?)</sql>', content, re.DOTALL),
        'meta_block': re.findall(r'<meta>(.*?)</meta>', content, re.DOTALL),
        'crea_block': re.findall(r'<crea>(.*?)</crea>', content, re.DOTALL), # Nuevo patrón para <crea>
        'sln': re.findall(r'<sln>(.*?)</sln>', content, re.DOTALL), # Nuevo patrón para SLN
        'xaml': re.findall(r'<xaml>(.*?)</xaml>', content, re.DOTALL), # Nuevo patrón para XAML
        'config': re.findall(r'<config>(.*?)</config>', content, re.DOTALL), # Nuevo patrón para CONFIG
        'csproj': re.findall(r'<csproj>(.*?)</csproj>', content, re.DOTALL), # Nuevo patrón para CSPROJ
    }
    return blocks, config

# Esta función guardará cada bloque en un archivo separado
def save_blocks_to_files(blocks, config, base_name):
    output_dir = config.get('output_dir', '.')

    if not os.path.exists(output_dir) and output_dir != '.':
        os.makedirs(output_dir)
        print(f"Directorio de salida '{output_dir}/' creado.")

    # Lista de tuplas (contenido_bloque, nombre_archivo_deseado, extensión)
    files_to_create = []

    # Bloques web
    if blocks['html']: files_to_create.append((blocks['html'][0], 'index', '.html'))
    if blocks['css']: files_to_create.append((blocks['css'][0], 'style', '.css'))
    if blocks['js']: files_to_create.append((blocks['js'][0], 'script', '.js'))

    # Bloques de lógica DSL
    if blocks['esp']: files_to_create.append((blocks['esp'][0], f'logic_{base_name}', '.esp'))
    if blocks['ing']: files_to_create.append((blocks['ing'][0], f'logic_{base_name}', '.ing'))
    if blocks['pat']: files_to_create.append((blocks['pat'][0], f'patterns_{base_name}', '.pat'))

    # Bloques de otros lenguajes
    if blocks['net']: files_to_create.append((blocks['net'][0], f'Program_{base_name}', '.cs'))
    if blocks['lua']: files_to_create.append((blocks['lua'][0], f'main_{base_name}', '.lua'))
    if blocks['rs']: files_to_create.append((blocks['rs'][0], f'src/main_{base_name}', '.rs')) # Rust en src/
    if blocks['go']: files_to_create.append((blocks['go'][0], f'main_{base_name}', '.go'))
    if blocks['sql']: files_to_create.append((blocks['sql'][0], f'schema_{base_name}', '.sql'))

    # Nuevos bloques .NET/configuración
    if blocks['sln']: files_to_create.append((blocks['sln'][0], f'{base_name}', '.sln'))
    if blocks['xaml']: files_to_create.append((blocks['xaml'][0], f'MainPage', '.xaml')) # O un nombre genérico
    if blocks['config']: files_to_create.append((blocks['config'][0], f'App', '.config')) # App.config
    if blocks['csproj']: files_to_create.append((blocks['csproj'][0], f'{base_name}', '.csproj'))


    for content, name, ext in files_to_create:
        # Manejo especial para Rust (va en src/)
        if ext == '.rs':
            file_dir = os.path.join(output_dir, os.path.dirname(name))
            file_name = os.path.basename(name)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            full_path = os.path.join(file_dir, f'{file_name}{ext}')
        else:
            full_path = os.path.join(output_dir, f'{name}{ext}')

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                # Caso especial para HTML: añadir encabezado y enlaces a CSS/JS
                if ext == '.html':
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                    f.write(f"<title>{config.get('project_name', 'Aio Project')}</title>\n")
                    f.write(f"<link rel='stylesheet' href='{os.path.basename(os.path.join(output_dir, 'style.css'))}'>\n")
                    f.write("</head>\n<body>\n")
                    f.write(content.strip())
                    f.write(f"\n<script src='{os.path.basename(os.path.join(output_dir, 'script.js'))}'></script>\n</body>\n</html>")
                else:
                    f.write(content.strip())
            print(f"'{full_path}' generado con éxito.")
        except Exception as e:
            print(f"Error al generar '{full_path}': {e}")
            
    # Procesa el bloque <crea> después de generar los archivos iniciales
    if blocks['crea_block']:
        for crea_content in blocks['crea_block']:
            parse_crea_block(crea_content, output_dir)

    # Opcional: guardar el contenido bruto del meta
    if blocks['meta_block']:
        meta_output_path = os.path.join(output_dir, f'config_{base_name}.meta')
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
