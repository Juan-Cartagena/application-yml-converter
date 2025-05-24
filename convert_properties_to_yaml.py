import os
import glob
import yaml
from collections import defaultdict

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
    result = defaultdict(dict)

    for key, value in dot_dict.items():
        parts = key.split('.')
        d = result
        for part in parts[:-1]:
            if part not in d or not isinstance(d[part], dict):
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value

    return dict(result)

def convert_properties_to_yaml(props):
    nested = nested_dict_from_dot_keys(props)
    return yaml.dump(nested, sort_keys=False, allow_unicode=True)

def main():
    files = glob.glob("audit---application.properties")
    for file in files:
        props = parse_properties_file(file)
        app_name = props.get("spring.application.name")
        if not app_name:
            print(f"Archivo {file} no tiene 'spring.application.name'. Se omite.")
            continue

        output_dir = os.path.join(os.getcwd(), app_name)
        os.makedirs(output_dir, exist_ok=True)

        yaml_content = convert_properties_to_yaml(props)

        output_file = os.path.join(output_dir, "application-local.yml")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        print(f"Convertido {file} a {output_file}")

if __name__ == "__main__":
    main()
