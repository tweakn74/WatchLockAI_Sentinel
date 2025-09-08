import yaml,sys
p="DOCS/mitre/rules/baseline.yaml"
try:
    data=yaml.safe_load(open(p)) or {}
    if isinstance(data, list):
        r = data
    else:
        r = data.get('rules', [])
    print("RC2_RULES_COUNT", len(r))
except Exception as e:
    print("RC2_YAML_ERR",e)