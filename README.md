# dj-serializers-to-ts
Script for generating TS interfaces from Django serializers, supports nested relationships and correctly imports nested types.

# Django Serializer → TypeScript Interface Generator

This script converts your Django REST Framework serializers into TypeScript interfaces for frontend use.

## ✅ Features

- Traverses nested folders under `appname/serializers/` (or your intended directory)
- Converts all DRF field types to TS types
- Handles nested serializers as `import type` in generated .ts files
- Generates one `.ts` file per serializer
- Produces a `tempindex.ts` file with exports for quick imports

## 🗂 Directory Structure

```
appname/
  serializers/
    submodule1/
      serializers1.py
    submodule2/
      serializers2.py
```

Generated output:

```
frontend/
  src/
    lib/
      types/
        serializers/
          submodule1/
            SerializerName1.ts
            SerializerName2.ts
          submodule2/
            SerializerName3.ts
            SerializerName4.ts
          tempindex.ts
```

## ⚙️ Setup

1. Make sure your Django project is configured correctly:
    - Your environment has Django and `djangorestframework` installed
    - Your `DJANGO_SETTINGS_MODULE` is correctly set

2. Adjust these values at the top of the script:

```py
BACKEND_DIR = "appname/serializers"
FRONTEND_DIR = "../frontend/src/lib/types/serializers"
DJANGO_SETTINGS_MODULE = "your_project.settings"
```

3. Run the script from your Django root:

```bash
python scripts/dj_serializers_to_ts.py
```

## 💡 Tip

You can auto-run this as part of your backend build or commit hook if your frontend types need to stay up-to-date.

---

**Note:** This does not inspect the full queryset logic or lists from viewsets. It only inspects declared DRF `Serializer` classes.
