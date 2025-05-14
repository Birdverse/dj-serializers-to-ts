"""
🔁 Django Serializer → TypeScript Interface Generator

This script walks your Django project's serializer directory and auto-generates matching
TypeScript interface files that mirror your serializer output structures — including nested serializers.

🔷 Features:
- Maps DRF fields to accurate TypeScript types
- Supports nested serializers with correct relative import paths
- Generates individual `.ts` interface files organized by backend folder structure
- Auto-builds a tempindex.ts file for easy importing

💡 Requirements:
- Your serializers must inherit from DRF BaseSerializer
- Django project must be configured and bootstrapped correctly (see DJANGO_SETTINGS_MODULE)

👨‍💻 Example usage:
    python scripts/dev/dj_serializers_to_ts.py
"""

import os
import sys
import inspect
import importlib.util
from pathlib import Path

# ───── CONFIG ─────────────────────────────────────────────────────
BACKEND_DIR = "appname/serializers"
FRONTEND_DIR = "../frontend/src/lib/types/serializers"
TEMP_INDEX_FILENAME = "tempindex.ts"
DJANGO_SETTINGS_MODULE = "config.settings"

# ───── SETUP DJANGO ───────────────────────────────────────────────
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
import django
django.setup()

from rest_framework import serializers

# ───── FIELD MAP ──────────────────────────────────────────────────
FIELD_TYPE_MAP = {
    "CharField": "string", "TextField": "string", "SlugField": "string",
    "EmailField": "string", "URLField": "string", "DateField": "string",
    "DateTimeField": "string", "TimeField": "string", "BooleanField": "boolean",
    "NullBooleanField": "boolean", "IntegerField": "number", "SmallIntegerField": "number",
    "BigIntegerField": "number", "PositiveIntegerField": "number", "PositiveSmallIntegerField": "number",
    "FloatField": "number", "DecimalField": "number", "JSONField": "any",
    "DictField": "Record<string, any>", "ListField": "any[]", "SerializerMethodField": "any",
    "PrimaryKeyRelatedField": "number", "ManyRelatedField": "number[]",
    "ImageField": "string", "FileField": "string", "ChoiceField": "string"
}

# 🧠 Cache type locations
interface_locations = {}

def extract_serializer_fields(cls):
    fields = {}
    for field_name, field in cls().get_fields().items():
        if isinstance(field, serializers.ListSerializer) and hasattr(field, "child"):
            nested_name = field.child.__class__.__name__.replace("Serializer", "")
            ts_type = f"{nested_name}[]"
        elif isinstance(field, serializers.BaseSerializer):
            nested_name = field.__class__.__name__.replace("Serializer", "")
            ts_type = nested_name
        else:
            ts_type = FIELD_TYPE_MAP.get(field.__class__.__name__, "any")
        fields[field_name] = ts_type
    return fields

def find_serializer_classes(file_path, module_path):
    spec = importlib.util.spec_from_file_location(module_path, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [
        (name.replace("Serializer", ""), cls)
        for name, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, serializers.BaseSerializer) and cls.__module__ == module_path
    ]

def write_ts_interface(name, fields, out_path, deps, current_dir):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for dep in sorted(deps):
            if dep == name or dep not in interface_locations:
                continue
            dep_path = interface_locations[dep]
            rel_path = os.path.relpath(dep_path, current_dir).replace(".ts", "").replace(os.sep, "/")
            f.write(f"import type {{ {dep} }} from './{rel_path}';\n")
        if deps:
            f.write("\n")
        f.write(f"export interface {name} {{\n")
        for field, ts_type in fields.items():
            f.write(f"  {field}?: {ts_type};\n")
        f.write("}\n")

def main():
    base = Path(BACKEND_DIR).resolve()
    out_base = Path(FRONTEND_DIR).resolve()
    index_lines = []
    all_interfaces = {}

    for file_path in base.rglob("*.py"):
        if file_path.name.startswith("__"):
            continue
        relative_path = file_path.relative_to(base)
        module_path = ".".join(["api.serializers"] + list(relative_path.with_suffix("").parts))

        for interface_name, cls in find_serializer_classes(file_path, module_path):
            fields = extract_serializer_fields(cls)
            out_path = out_base / relative_path.parent / f"{interface_name}.ts"
            interface_locations[interface_name] = out_path
            all_interfaces[interface_name] = (fields, out_path)

    for interface_name, (fields, out_path) in all_interfaces.items():
        deps = {
            t.replace("[]", "") for t in fields.values()
            if t not in FIELD_TYPE_MAP.values() and t != "any"
        }
        write_ts_interface(interface_name, fields, out_path, deps, out_path.parent)
        rel_import = os.path.relpath(out_path, out_base).replace(".ts", "").replace(os.sep, "/")
        index_lines.append(f"export * from './{rel_import}';")

    (out_base).mkdir(parents=True, exist_ok=True)
    with open(out_base / TEMP_INDEX_FILENAME, "w") as f:
        f.write("// 🔄 Auto-generated. Do not edit manually.\n\n")
        f.write("\n".join(sorted(set(index_lines))) + "\n")

    print("✅ TypeScript interfaces generated.")

if __name__ == "__main__":
    main()
