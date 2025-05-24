import os
import glob
import yaml
import re

# 🔐 Claves sensibles: clave .properties → nombre variable de entorno
SENSITIVE_KEYS = {
    "spring.datasource.username": "DB_USERNAME",
    "spring.datasource.password": "DB_PASSWORD",
    "spring.security.oauth2.client.registration.google.client-id": "GOOGLE_CLIENT_ID",
    "spring.security.oauth2.client.registration.google.client-secret": "GOOGLE_CLIENT_SECRET",
    "app.jwt.secret": "JWT_SECRET"
}

# 🔧 Configuración para entorno "pre"
PRE_DB_HOST = "localhost"
PRE_DB_PORT = "5433"

def parse_properties_file(file_path):
    props = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                props[key.strip()] = value.strip()
    return props

def nested_dict_from_dot_keys(dot_dict):
    result = {}
    for key, value in dot_dict.items():
        parts = key.split('.')
        d = result
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value
    return result

def convert_sensitive_props(props):
    env_vars = {}
    for full_key, env_var in SENSITIVE_KEYS.items():
        if full_key in props:
            env_vars[env_var] = props[full_key]
            props[full_key] = f"${{{env_var}}}"
    return props, env_vars

def convert_properties_to_yaml(props):
    nested = nested_dict_from_dot_keys(props)
    return yaml.dump(nested, sort_keys=False, allow_unicode=True)

def write_env_file(env_vars, output_dir):
    env_path = os.path.join(output_dir, ".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def modify_url_for_pre(props):
    url_key = "spring.datasource.url"
    if url_key in props:
        original_url = props[url_key]
        # Reemplaza host y puerto en una URL típica de JDBC
        # Ejemplo: jdbc:postgresql://localhost:5432/dbname
        new_url = re.sub(r'//([^:/]+)(:\d+)?', f"//{PRE_DB_HOST}:{PRE_DB_PORT}", original_url)
        props[url_key] = new_url
    return props

def main():
    files = glob.glob("*---application.properties")
    if not files:
        print("No se encontraron archivos que terminen en '---application.properties'")
        return

    for file in files:
        props = parse_properties_file(file)
        app_name = props.get("spring.application.name")
        if not app_name:
            print(f"⚠️  Archivo {file} no tiene 'spring.application.name'. Se omite.")
            continue

        output_dir = os.path.join(os.getcwd(), app_name)
        os.makedirs(output_dir, exist_ok=True)

        # ✅ application-local.yml
        props_local, env_vars = convert_sensitive_props(props.copy())
        yaml_local = convert_properties_to_yaml(props_local)
        with open(os.path.join(output_dir, "application-local.yml"), 'w', encoding='utf-8') as f:
            f.write(yaml_local)
        if env_vars:
            write_env_file(env_vars, output_dir)

        # 🆕 application-pre.yml con IP y puerto personalizados
        props_pre = modify_url_for_pre(props.copy())
        props_pre, _ = convert_sensitive_props(props_pre)
        yaml_pre = convert_properties_to_yaml(props_pre)
        with open(os.path.join(output_dir, "application-pre.yml"), 'w', encoding='utf-8') as f:
            f.write(yaml_pre)

        print(f"✅ {file} → application-local.yml, application-pre.yml + .env")

if __name__ == "__main__":
    main()
