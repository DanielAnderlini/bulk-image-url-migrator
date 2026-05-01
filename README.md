# Bulk Image URL Migrator

`bulk-image-url-migrator` is a production-oriented Python automation tool for migrating product image URLs from private or temporary sources into Cloudinary-hosted public URLs.

It reads `.xlsx` and `.csv` product spreadsheets from `input/`, validates the required structure, downloads each image, detects the real image format with Pillow, stores a local copy, uploads the image to Cloudinary, writes the public URL back into a new spreadsheet, creates a detailed process log, and archives the original input file.

## Business Problem

E-commerce, ERP, and catalog teams often receive spreadsheets with private image URLs from suppliers, legacy systems, or client drives. Those URLs are not stable enough for storefronts, marketplaces, or public catalogs.

This tool turns those spreadsheets into migration-ready deliverables:

- stable generated product image IDs
- verified local image files
- Cloudinary public URLs
- row-level success and failure logs
- processed and failed file archives

## Features

- Processes `.xlsx` and `.csv` files from `input/`
- Requires the `ImageURL` column
- Adds `GeneratedProductID` and `PublicImageURL` columns when missing
- Generates traceable IDs using timestamp, row number, URL hash, and UUID
- Downloads images with configurable timeouts and retry handling for transient failures
- Detects real image format using Pillow instead of trusting file extensions
- Supports `jpg`, `jpeg`, `png`, `webp`, and `gif`
- Uploads images to Cloudinary using the generated ID as `public_id`
- Writes timestamped updated spreadsheets and process logs
- Adds execution batch IDs to every process log row
- Prints a final execution summary with file, row, image, and timing totals
- Moves successfully processed files to `processed/`
- Moves critically invalid files to `failed/`
- Continues processing rows when row-level errors occur

## Project Structure

```text
bulk-image-url-migrator/
├── input/
│   └── sample_products.xlsx
├── processed/
├── failed/
├── output/
│   └── downloaded_images/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── input_validator.py
│   ├── file_manager.py
│   ├── product_id_generator.py
│   ├── spreadsheet_reader.py
│   ├── image_downloader.py
│   ├── image_detector.py
│   ├── image_uploader.py
│   ├── spreadsheet_writer.py
│   └── process_logger.py
└── docs/
    ├── screenshots/
    ├── demo_workflow.md
    ├── upwork_demo_script.md
    └── technical_notes.md
```

## Installation

```bash
cd bulk-image-url-migrator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## Configuration

Copy the example environment file:

```bash
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Then set your Cloudinary credentials:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_FOLDER=upwork-demo-products
```

The sample project can still run without credentials, but upload steps will be logged as row-level failures. This is intentional so validation, download, image detection, local image saving, logging, and file archiving can be demonstrated safely without committing secrets.

When Cloudinary credentials are missing, the tool prints a clear warning before file processing starts:

```text
Cloudinary credentials not configured.
Uploads will fail but local processing and logging will continue.
```

Download retry behavior is configurable:

```env
REQUEST_TIMEOUT_SECONDS=30
DOWNLOAD_RETRY_COUNT=3
DOWNLOAD_RETRY_DELAY_SECONDS=2
```

Retries are used for transient failures such as timeouts, connection errors, and temporary HTTP status codes. Permanent failures such as invalid URLs and `404 Not Found` are not retried.

## How To Run

From the project root:

```bash
python src/main.py
```

The tool will scan `input/` for `.xlsx` and `.csv` files.

At the end of each run, it prints a client-friendly execution summary:

```text
EXECUTION SUMMARY
FILES PROCESSED: 3
FILES FAILED: 1

ROWS SUCCESS: 127
ROWS FAILED: 9
ROWS SKIPPED: 4

TOTAL IMAGES DOWNLOADED: 118
TOTAL IMAGES UPLOADED: 118

TOTAL EXECUTION TIME: 00:02:14
```

## Output Generated

For an input file named `sample_products.xlsx`, the tool generates:

```text
output/sample_products_updated_YYYYMMDD_HHMMSS.xlsx
output/sample_products_process_log_YYYYMMDD_HHMMSS.csv
output/downloaded_images/IMG_YYYYMMDDHHMMSS_R2_A1B2C3_UUID8.jpg
```

After successful file processing, the original input is archived as:

```text
processed/sample_products_PROCESSED_YYYYMMDD_HHMMSS.xlsx
```

If a critical validation error occurs, the original input is moved to:

```text
failed/sample_products_FAILED_YYYYMMDD_HHMMSS.xlsx
```

## Error Handling

Critical file-level errors stop processing for that file:

- file cannot be opened
- unsupported file format
- empty file
- missing required `ImageURL` column
- output file cannot be written

Row-level errors are logged and processing continues:

- empty `ImageURL`
- invalid URL
- download failure
- downloaded content is not an image
- unsupported image format
- Cloudinary upload failure

## Process Log

Each run creates a CSV log with:

```text
file_name, execution_batch_id, row_number, product_description,
GeneratedProductID, original_url, download_status, detected_format,
local_file, upload_status, public_url, error_message, processed_at
```

Statuses are `SUCCESS`, `FAILED`, and `SKIPPED`.

The `execution_batch_id` uses the format `BATCH_YYYYMMDDHHMMSS_UUID6` so spreadsheet output, logs, and console runs can be traced back to the same execution.

## Demo Screenshots

Screenshot placeholders are prepared in `docs/screenshots/` for a polished GitHub or Upwork presentation:

- console execution
- updated spreadsheet
- process log
- downloaded images folder
- processed folder result

No fake screenshots are included. Add real screenshots after running the demo locally.

## Portfolio Positioning

This project demonstrates the kind of automation often requested by e-commerce operators, medical suppliers, catalog managers, and agencies handling product data cleanup. It shows practical production concerns: validation, safe file movement, traceable IDs, row-level resilience, environment-based credentials, clear logs, and modular Python design.

## Future Improvements

- Add retry/backoff for transient upload failures
- Add concurrent row processing with rate limiting
- Add optional dry-run mode
- Add structured JSON logs
- Add unit tests for validators and image detection
- Add Docker packaging for repeatable deployments
"# bulk-image-url-migrator" 
