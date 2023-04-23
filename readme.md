# Setup Instructions

To use this script, you need to follow the steps below:

## 1. Set up the required environment variables

This script requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `TESSERACT_OCR_EXECUTABLE_PATH`: The path to the Tesseract OCR executable file.

## 2. Download and install the required software

### FFMPEG

FFmpeg is a free, open-source software that is used to handle multimedia files. It is required to extract audio from video files and to speed up the audio.

- Windows: Visit [https://www.ffmpeg.org/download.html#build-windows](https://www.ffmpeg.org/download.html#build-windows) and download the latest version of the static build. Extract the downloaded file and add the `bin` directory to your system's PATH.
- macOS: Run the command `brew install ffmpeg` in your terminal.
- Linux: Run the command `sudo apt-get install ffmpeg` in your terminal.

### Tesseract OCR

Tesseract OCR is a free and open-source OCR engine that is used to extract text from images. It is required to extract text from image files.

- Windows: Visit [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) and download the latest version of the installer for Windows. Install the software and add the Tesseract installation directory to your system's PATH.
- macOS: Run the command `brew install tesseract` in your terminal.
- Linux: Run the command `sudo apt-get install tesseract-ocr` in your terminal.

## 3. Install the required Python packages

This script requires the following Python packages:

- `pytesseract`
- `Pillow`
- `PyPDF2`
- `python-dotenv`
- `openai`
- `pyttsx3`

You can install these packages by running the following command in your terminal:

```
pip install pytesseract Pillow PyPDF2 python-dotenv openai pyttsx3
```

After completing these steps, you should be able to use the script.
