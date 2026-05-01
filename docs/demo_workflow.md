# Demo Workflow

This walkthrough shows how to demo the project without exposing any private client data.

## 1. Prepare The Environment

```bash
cd bulk-image-url-migrator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add Cloudinary credentials to `.env` if you want the upload step to complete successfully.

## 2. Review The Sample Input

Open:

```text
input/sample_products.xlsx
```

The file contains eight sample compression garment and medical product rows with public test image URLs.

Required column:

```text
ImageURL
```

Recommended catalog columns:

```text
Long Description
Product Categories
Item Sub category
Base Unit of Measure
```

## 3. Run The Migrator

```bash
python src/main.py
```

The console prints progress for each file and row.

## 4. Inspect The Results

Check the generated spreadsheet:

```text
output/sample_products_updated_YYYYMMDD_HHMMSS.xlsx
```

It includes:

```text
GeneratedProductID
PublicImageURL
```

Check the process log:

```text
output/sample_products_process_log_YYYYMMDD_HHMMSS.csv
```

Check local downloaded images:

```text
output/downloaded_images/
```

## 5. Confirm File Archiving

After successful processing, the original input is moved to:

```text
processed/
```

Files with critical validation errors are moved to:

```text
failed/
```

## Demo Tip

For a clean second run, move the processed sample file back into `input/` or create a new spreadsheet in `input/`.
