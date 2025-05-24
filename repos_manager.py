import os
import subprocess
import shutil

# ✅ Configuración fácilmente editable
REPO_URLS = [
    "https://github.com/cartagena-corp/lm-audit.git",
    "https://github.com/cartagena-corp/lm-comments.git",
    "https://github.com/cartagena-corp/lm-config.git",
    "https://github.com/cartagena-corp/lm-integration.git",
    "https://github.com/cartagena-corp/lm-issues.git",
    "https://github.com/cartagena-corp/lm-notifications.git",
    "https://github.com/cartagena-corp/lm-oauth.git",
    "https://github.com/cartagena-corp/lm-projects.git",
    "https://github.com/cartagena-corp/lm-sprint.git",
    "https://github.com/cartagena-corp/lm-users.git"
    
    # Agrega más repos aquí
]

COMMIT_MESSAGE = "Actualización de archivos de configuración"
CONFIG_FILES = ["application-local.yml", "application-pre.yml"]

# Ruta base donde se clonan los repositorios
TARGET_DIR = r"C:\git\cartagena-corporation\la-muralla"  # <- Cambiar si se desea otra ubicación

# Ruta donde está el script (y los archivos yml originales)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ Error ejecutando: {command}")
        print(result.stderr.decode())
    return result


def clone_repos():
    os.makedirs(TARGET_DIR, exist_ok=True)

    for url in REPO_URLS:
        repo_name = url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(TARGET_DIR, repo_name)

        if not os.path.exists(repo_path):
            print(f"📥 Clonando {repo_name}...")
            run_command(f"git clone {url}", cwd=TARGET_DIR)
        else:
            print(f"✅ Repositorio {repo_name} ya existe, se omite clonación.")

        # Crear carpeta config y copiar archivos
        config_path = os.path.join(repo_path, "src/main/resources/config")
        os.makedirs(config_path, exist_ok=True)

        for file in CONFIG_FILES:
            src_file = os.path.join(SCRIPT_DIR, file)
            if os.path.exists(src_file):
                shutil.copy(src_file, config_path)
                print(f"📄 Copiado {file} a {config_path}")
            else:
                print(f"⚠️ Archivo {file} no encontrado en {SCRIPT_DIR}")


def push_changes():
    for url in REPO_URLS:
        repo_name = url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(TARGET_DIR, repo_name)

        if not os.path.exists(repo_path):
            print(f"⚠️ Repositorio {repo_name} no existe localmente, se omite.")
            continue

        print(f"\n🔄 Procesando {repo_name}...")
        run_command("git pull", cwd=repo_path)
        run_command("git add .", cwd=repo_path)
        run_command(f'git commit -m "{COMMIT_MESSAGE}"', cwd=repo_path)
        run_command("git push", cwd=repo_path)


if __name__ == "__main__":
    opcion = input("¿Qué deseas hacer?\n1. Clonar y copiar archivos\n2. Subir cambios (pull + commit + push)\nSelecciona (1/2): ")

    if opcion == "1":
        clone_repos()
    elif opcion == "2":
        push_changes()
    else:
        print("❌ Opción inválida.")
