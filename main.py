# main.py en Replit (VERSION SUPER COMPLETA con .NET, CREA, META, y Output Dir)
import re
import os
import shutil # Para operaciones de borrado de directorios

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
                    config[key] = value.strip('"') # Remover comillas si existen
        return config
    return {}

# NUEVA FUNCIÓN: Para procesar el bloque <crea>
def process_crea_block(crea_content, output_dir="."):
    print(f"\n--- Ejecutando comandos <crea> en {output_dir}/ ---")
    
    # Asegúrate de que el directorio de salida exista antes de crear/borrar
    if output_dir != "." and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    lines = [line.strip() for line in crea_content.split(',') if line.strip()]
    
    for line in lines:
        if line.startswith('#'): continue # Ignorar comentarios

        # Comando: $crea=file Name="NOMBRE" %extencion .js,
        crea_file_match = re.match(r'\$crea=file\s+Name="([^"]+)"(?:\s+%extencion\s+([^\s,]+(?:,[^\s,]+)*))?(?:\s+%Not_extencion)?', line)
        if crea_file_match:
            name = crea_file_match.group(1)
            extensions_str = crea_file_match.group(2)
            not_extension_flag = '%Not_extencion' in line

            if not_extension_flag:
                file_path = os.path.join(output_dir, name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Archivo creado por .Aio: {name}\n")
                print(f"  Archivo '{file_path}' creado.")
            elif extensions_str:
                extensions = [ext.strip() for ext in extensions_str.split(',')]
                for ext in extensions:
                    file_path = os.path.join(output_dir, f"{name}{ext}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Archivo creado por .Aio: {name}{ext}\n")
                    print(f"  Archivo '{file_path}' creado.")
            else:
                # Si no hay extensión ni %Not_extencion, crear el archivo con el nombre dado.
                file_path = os.path.join(output_dir, name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Archivo creado por .Aio: {name}\n")
                print(f"  Archivo '{file_path}' creado (sin extensión explícita).")
            continue

        # Comando: %borra=Name="ejemplo.js"
        borra_name_match = re.match(r'%borra=Name="([^"]+)"', line)
        if borra_name_match:
            file_to_delete = os.path.join(output_dir, borra_name_match.group(1))
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
                print(f"  Archivo '{file_to_delete}' borrado.")
            else:
                print(f"  Advertencia: Archivo '{file_to_delete}' no encontrado para borrar.")
            continue

        # Comando: %borra=file="la ruta" %all
        borra_all_match = re.match(r'%borra=file="([^"]+)"\s+%all', line)
        if borra_all_match:
            target_path = os.path.join(output_dir, borra_all_match.group(1))
            if os.path.exists(target_path):
                # Borrar todo el contenido del directorio
                for item in os.listdir(target_path):
                    item_path = os.path.join(target_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path) # Borrar subdirectorios recursivamente
                print(f"  Contenido del directorio '{target_path}' borrado.")
            else:
                print(f"  Advertencia: Directorio '{target_path}' no encontrado para borrar %all.")
            continue
        
        # Comando: %borra=file="la ruta" %index.html,ejemplo.c,
        # Nota: La parte &con funcion {...} se ignora por ahora.
        borra_files_match = re.match(r'%borra=file="([^"]+)"\s+([^&]+)(?:&con.*)?', line)
        if borra_files_match:
            target_path = os.path.join(output_dir, borra_files_match.group(1))
            files_to_delete_str = borra_files_match.group(2).strip()
            files_to_delete = [f.strip() for f in files_to_delete_str.split(',') if f.strip()]
            
            for file_name in files_to_delete:
                file_path = os.path.join(target_path, file_name)
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"  Archivo '{file_path}' borrado.")
                    else:
                        print(f"  Advertencia: '{file_path}' no es un archivo para borrar.")
                else:
                    print(f"  Advertencia: Archivo '{file_path}' no encontrado para borrar.")
            continue

        print(f"  Advertencia: Comando <crea> no reconocido o incompleto: '{line}'")


# Esta función lee un archivo .aio y extrae los bloques de código
def parse_aio_file(file_path):
    print(f"\n--- Procesando archivo: {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
        return None, None

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
        'crea': re.findall(r'<crea>(.*?)</crea>', content, re.DOTALL), # Nuevo patrón para <crea>
        'sln': re.findall(r'<sln>(.*?)</sln>', content, re.DOTALL), # Nuevo patrón para .sln
        'csproj': re.findall(r'<csproj>(.*?)</csproj>', content, re.DOTALL), # Nuevo patrón para .csproj
        'xaml': re.findall(r'<xaml>(.*?)</xaml>', content, re.DOTALL), # Nuevo patrón para .xaml
        'config': re.findall(r'<config>(.*?)</config>', content, re.DOTALL), # Nuevo patrón para .config
        'meta_block': re.findall(r'<meta>(.*?)</meta>', content, re.DOTALL) # Contenido bruto del meta
    }
    return blocks, config

# Esta función guardará cada bloque en un archivo separado
def save_blocks_to_files(blocks, config, base_name):
    output_dir = config.get('output_dir', '.') # Usar 'build' si está en meta, sino '.'

    # Si hay un bloque <crea>, procesarlo primero
    if blocks['crea']:
        for crea_content in blocks['crea']:
            process_crea_block(crea_content, output_dir)

    if not os.path.exists(output_dir) and output_dir != '.':
        os.makedirs(output_dir)
        print(f"Directorio de salida '{output_dir}/' creado.")

    # Nombres de archivo, ahora con directorio de salida
    # Nombres base para archivos .NET a partir del project_name de meta, si existe
    project_name = config.get('project_name', base_name)

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
    
    sln_output_path = os.path.join(output_dir, f'{project_name}.sln') # Nuevo: .sln
    csproj_output_path = os.path.join(output_dir, f'{project_name}.csproj') # Nuevo: .csproj
    xaml_output_path = os.path.join(output_dir, f'MainWindow.xaml') # Nuevo: .xaml (nombre genérico)
    config_output_path = os.path.join(output_dir, f'App.config') # Nuevo: .config (nombre genérico)

    meta_output_path = os.path.join(output_dir, f'config_{base_name}.meta')

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
        print(f"Archivo de solución (.sln) guardado en '{sln_output_path}'.")

    if blocks['csproj']:
        with open(csproj_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['csproj'][0].strip())
        print(f"Archivo de proyecto C# (.csproj) guardado en '{csproj_output_path}'.")

    if blocks['xaml']:
        with open(xaml_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['xaml'][0].strip())
        print(f"Archivo XAML (.xaml) guardado en '{xaml_output_path}'.")

    if blocks['config']:
        with open(config_output_path, 'w', encoding='utf-8') as f:
            f.write(blocks['config'][0].strip())
        print(f"Archivo de configuración (.config) guardado en '{config_output_path}'.")

    if blocks['meta_block']:
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
