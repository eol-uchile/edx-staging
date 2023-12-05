import os
import re
import sys
import logging
from jinja2 import Template, Environment, FileSystemLoader
import subprocess

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Expresiones regulares
package_pattern_with_link = re.compile(r'^-e git\+(https://[^\s@]+)@[^#]+#egg=([^\s]+)')
package_pattern_without_link = re.compile(r'^([^=\s]+)==([\d\.]+)')


def get_repository_branch(data):
    try:
        command = f"git branch --show-current"
        branch = subprocess.check_output(command, shell=True, universal_newlines=True).strip()
        data['repository_branch'] = branch
    except Exception as e:
        logger.exception(f"Error subprocess: {e}")
        sys.exit(-1)

def get_repository_info(data):
    try:
        url_command = f"git remote get-url origin"
        repository_url = subprocess.check_output(url_command, shell=True, universal_newlines=True).strip().replace(".git","")

        # Extraer el nombre del repositorio de la URL
        repository_name_match = re.search(r'/([^/]+)$', repository_url)
        repository_name = repository_name_match.group(1) if repository_name_match else None

        data['repository_url'] = repository_url
        data['repository_name'] = repository_name
    except Exception as e:
        logger.exception(f"Error subprocess: {e}")
        sys.exit(-1)

def get_docker_image_info(data):
    try:
        command = f"head -n1 Dockerfile | cut -d' ' -f2"
        first_line = subprocess.check_output(command, shell=True, universal_newlines=True).strip().replace(".git","")

        # Obtener el base_image_tag que viene después del '='
        base_image_tag = first_line.split(':')[1].strip()

        url = 'https://' + first_line

        data['docker_image_url'] = url
        data['docker_image_name'] = base_image_tag
    except Exception as e:
        logger.exception(f"Error subprocess: {e}")
        sys.exit(-1)

def process_themes(themes_path, data):
    for theme in os.listdir(themes_path):
        theme_path = os.getcwd()+'/'+ themes_path+'/'+ theme
        if os.path.isdir(theme_path):
            link = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=theme_path, universal_newlines=True).strip()
            data['themes'].append({'name': theme, 'link': link})

# Funcion que permite obtener el basename (nombre del archivo sin extensión) y un indicador has_links que indica si hay enlaces en el archivo.
def extract_info_from_txt(txt_file_path):
    basename = os.path.splitext(os.path.basename(txt_file_path))[0].lower()
    has_links = False

    with open(txt_file_path, 'r') as file:
        for line in file:
            # Buscar información del paquete con enlace
            package_match = package_pattern_with_link.match(line)
            if package_match:
                has_links = True
                link = package_match.group(1)
                package_name = package_match.group(2)

                return basename, has_links, {
                    'name': package_name,
                    'version': None,  # El paquete con enlace no tiene versión en este contexto
                    'link': link
                }

            # Buscar información del paquete sin enlace
            package_match = package_pattern_without_link.match(line)
            if package_match:
                package_name = package_match.group(1)
                package_version = package_match.group(2)

                return basename, has_links, {
                    'name': package_name,
                    'version': package_version,
                    'link': None
                }

    return basename, has_links, None

def process_txt_files(requirements_path, data):
    # Procesar cada archivo .txt en la carpeta '/requirements'
    for txt_file in os.listdir(requirements_path):
        if txt_file.endswith(".txt"):
            txt_file_path = os.path.join(requirements_path, txt_file)
            try:
                process_txt_file(txt_file_path, data)
            except Exception as e:
                logger.exception(f"Error processing {txt_file}: {e}")
                sys.exit(-1)

def process_txt_file(txt_file_path, data):
    # Extraer el basename y los nombres de los paquetes desde el archivo .txt
    basename, _, has_links = extract_info_from_txt(txt_file_path)

    # Agregar información al diccionario de datos
    data['requirements'].append({
        'basename': basename,
        'packages': [],
        'has_links': has_links
    })

    with open(txt_file_path, 'r') as file:
        for line in file:
            # Buscar información del paquete con enlace
            package_match = package_pattern_with_link.match(line)
            if package_match:
                has_links = True
                link = package_match.group(1)
                package_name = package_match.group(2)

                if not data['requirements']:
                    # Si la lista está vacía, agregar un diccionario vacío para contener los paquetes
                    data['requirements'].append({'basename': basename, 'packages': [], 'has_links': has_links})

                data['requirements'][-1]['packages'].append({
                    'name': package_name,
                    'version': None,  # El paquete con enlace no tiene versión en este contexto
                    'link': link
                })

            # Buscar información del paquete sin enlace
            package_match = package_pattern_without_link.match(line)
            if package_match:
                package_name = package_match.group(1)
                package_version = package_match.group(2)

                if not data['requirements']:
                    # Si la lista está vacía, agregar un diccionario vacío para contener los paquetes
                    data['requirements'].append({'basename': basename, 'packages': [], 'has_links': has_links})

                data['requirements'][-1]['packages'].append({
                    'name': package_name,
                    'version': package_version,
                    'link': None
                })



if __name__ == "__main__":
    requirements_path = 'requirements'
    themes_path = 'themes'
    diagram_template_path = 'templates/diagram_template.j2'
    diagram_file_path = os.path.join('diagrams', 'diagram.puml')

    # Configurar entorno de Jinja2
    env = Environment(loader=FileSystemLoader(os.path.dirname(diagram_template_path)))
    template = env.get_template(os.path.basename(diagram_template_path))


    # Datos que se pasan al template
    data = {'requirements': [],
        'themes': []}

    try:
        get_repository_info(data)
        get_docker_image_info(data)
        get_repository_branch(data)
        process_txt_files(requirements_path, data)
        process_themes(themes_path, data)
        logger.info(f"DATA ----->:{data}")
    except Exception as e:
        logger.exception(f"Error processing files: {e}")
        sys.exit(-1)

    # Renderizar el template con los datos
    rendered_content = template.render(data=data)

    # Escribir el contenido renderizado en el archivo PlantUML
    with open(diagram_file_path, 'w') as file:
        file.write(rendered_content)
