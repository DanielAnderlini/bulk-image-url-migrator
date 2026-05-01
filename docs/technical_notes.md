# Technical Notes

## Architecture

The project is split into small modules with clear responsibilities:

- `config.py` loads typed settings and creates folders.
- `file_manager.py` discovers input files and archives processed or failed files.
- `input_validator.py` separates critical file validation from row-level processing.
- `spreadsheet_reader.py` reads `.xlsx` and `.csv` files into pandas.
- `product_id_generator.py` creates traceable low-collision image IDs.
- `image_downloader.py` handles URL validation and HTTP download errors.
- `image_detector.py` uses Pillow to validate image bytes and detect real format.
- `image_uploader.py` wraps Cloudinary configuration and upload.
- `spreadsheet_writer.py` writes timestamped Excel output.
- `process_logger.py` collects and writes row-level CSV logs.
- `main.py` orchestrates the workflow.

## File-Level Versus Row-Level Errors

Critical file-level errors stop processing for the current file because output integrity cannot be guaranteed:

- unreadable file
- unsupported extension
- empty spreadsheet
- missing `ImageURL`
- failure writing output artifacts

Row-level errors are recoverable and are written to the process log:

- blank URL
- malformed URL
- HTTP request failure
- invalid image bytes
- unsupported image type
- upload failure

## Image Format Detection

The tool does not trust URL extensions or HTTP content type alone. It opens the downloaded bytes with Pillow and calls `verify()`. The detected Pillow format is mapped to a normalized extension:

```text
JPEG -> jpg
PNG  -> png
WEBP -> webp
GIF  -> gif
```

## Cloudinary Uploads

Each uploaded asset uses:

```text
public_id = CLOUDINARY_FOLDER / GeneratedProductID
```

This keeps Cloudinary assets traceable back to spreadsheet rows and local files.

## Windows Compatibility

Paths are managed with `pathlib.Path`, and the project is runnable from the project root using:

```bash
python src/main.py
```

## Operational Notes

- The generated output spreadsheet is always `.xlsx`, even when the input is `.csv`.
- Temporary Office files beginning with `~$` are ignored.
- Existing destination files are never overwritten during archive moves.
- Missing Cloudinary credentials produce row-level upload failures, not committed secrets or hardcoded demo credentials.
