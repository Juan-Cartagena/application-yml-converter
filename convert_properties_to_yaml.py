import os
import glob
import yaml

# 🔐 Claves sensibles en formato .properties → nombre de variable de entorno
SENSITIVE_KEYS = {
    "spring.datasource.username": "DB_USERNAME",
    "spring.datasource.password": "DB_PASSWORD",
    "spring.security.oauth2.client.registration.google.client-id": "GOOGLE_CLIENT_ID",
    "spring.security.oauth2.client.registration.google.client-secret": "GOOGLE_CLIENT_SECRET",
    "app.jwt.secret": "JWT_SECRET"
}

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

        props, env_vars = convert_sensitive_props(props)

        output_dir = os.path.join(os.getcwd(), app_name)
        os.makedirs(output_dir, exist_ok=True)

        yaml_content = convert_properties_to_yaml(props)
        with open(os.path.join(output_dir, "application-local.yml"), 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        if env_vars:
            write_env_file(env_vars, output_dir)
            print(f"✅ {file} → application-local.yml + .env (con variables sensibles)")
        else:
            print(f"✅ {file} → application-local.yml (sin variables sensibles)")

if __name__ == "__main__":
    main()
