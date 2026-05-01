# Upwork Demo Script

Use this script for a short client-facing walkthrough.

## Intro

This is a Python automation tool that migrates image URLs in product spreadsheets into Cloudinary-hosted public URLs. It is designed for catalog cleanup, marketplace onboarding, e-commerce migrations, and supplier spreadsheet processing.

## Problem

Clients often have spreadsheets with private, expiring, or inconsistent image links. Those links are risky for production catalogs because they can break, require authentication, or point to files with misleading extensions.

## Solution

The tool reads spreadsheets from an input folder, validates the required columns, generates traceable product image IDs, downloads each image, detects the real image format, saves a local copy, uploads the image to Cloudinary, and writes the new public URL back to a timestamped output spreadsheet.

## Key Engineering Points

- The code is modular instead of being a one-off script.
- Credentials are loaded from `.env` and are not committed.
- File-level errors are separated from row-level errors.
- A single bad image URL does not stop the whole spreadsheet.
- Every row has a log entry for auditability.
- Processed and failed input files are archived automatically.

## Demo Steps

1. Show `input/sample_products.xlsx`.
2. Show `.env.example` and explain Cloudinary configuration.
3. Run `python src/main.py`.
4. Open the updated spreadsheet in `output/`.
5. Open the process log in `output/`.
6. Show local image files in `output/downloaded_images/`.
7. Show the original file archived in `processed/`.

## Closing Pitch

This project is a realistic example of the automation I build for business operations: spreadsheet ingestion, validation, external API integration, file lifecycle management, and clear reporting for non-technical users.
