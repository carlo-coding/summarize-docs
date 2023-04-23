import os
import pytesseract
from PIL import Image
import PyPDF2
from dotenv import load_dotenv
import os
import openai
import subprocess
import pyttsx3
import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

pytesseract.pytesseract.tesseract_cmd = r"D:\\Programas\\Tesseract-OCR\\tesseract.exe"

def get_timestamped_filename(file_extension):
    # Obtener la fecha y hora actual
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Concatenar la marca de tiempo y la extensión del archivo
    filename = f"{timestamp}.{file_extension}"
    return filename

def text_to_audio(text):
    # Inicializar el motor de texto a voz
    engine = pyttsx3.init()
    # Convertir el texto en voz
    path = os.path.join("ReadAloudFiles", get_timestamped_filename("mp3"))
    engine.save_to_file(text, path)
    engine.runAndWait()

def read_text(text):
    # Inicializar el motor de texto a voz
    engine = pyttsx3.init()
    # Convertir el texto en voz
    engine.say(text)
    engine.runAndWait()

def extract_and_speed_up_audio(video_path):
    # Obtener la ruta de la carpeta donde está el archivo de video
    folder_path = os.path.dirname(video_path)
    # Obtener el nombre del archivo de video sin la extensión
    file_name = os.path.splitext(os.path.basename(video_path))[0]
    # Definir el nombre del archivo de audio resultante
    audio_output = os.path.join(folder_path, file_name + '.mp3')
    # Ejecutar el comando ffmpeg para extraer el audio y acelerarlo x2
    subprocess.run(['ffmpeg', '-i', video_path, '-vn', '-filter:a', 'atempo=2.0', audio_output])
    # Eliminar el archivo de video
    os.remove(video_path)
    return audio_output

# Función para extraer texto de una imagen
def extract_text_from_image(image_path):
    # Abre la imagen utilizando Pillow
    img = Image.open(image_path)
    # Esta parte es una solución temporal ya que no sé porque rota las imagenes.
    img = img.rotate(-90, expand=True)
    # Utiliza Pytesseract para extraer el texto de la imagen
    text = pytesseract.image_to_string(img, lang='spa')
    return text

def extract_text_from_audio(audio_path):
    audio_file = open(audio_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"] 

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(pdf_path):
    # Abre el archivo PDF utilizando PyPDF2
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        # Itera sobre cada página del PDF y extrae el texto
        text = ''
        for i in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[i]
            text += page.extract_text()
    return text

# Ruta de la carpeta donde se encuentran los archivos
folder_path = './docs/'

def get_text_from_docs(folder_path):
    # Itera sobre cada archivo en la carpeta y extrae el texto
    all_text = ''
    for filename in os.listdir(folder_path):
        print(f"Leyendo contenido de {filename} ...")
        # Crea la ruta completa al archivo
        file_path = os.path.join(folder_path, filename)
        # Si el archivo es una imagen, extrae el texto utilizando la función extract_text_from_image()
        if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.webp'):
            image_text = extract_text_from_image(file_path)
            all_text += image_text
        # Si el archivo es un PDF, extrae el texto utilizando la función extract_text_from_pdf()
        elif filename.endswith('.pdf'):
            pdf_text = extract_text_from_pdf(file_path)
            all_text += pdf_text
        elif filename.endswith('.mp3') or filename.endswith('.wav'):
            audio_text = extract_text_from_audio(file_path)
            all_text += audio_text
        elif filename.endswith(".mp4") or filename.endswith('.mkv'):
            audio_path = extract_and_speed_up_audio(file_path)
            audio_text = extract_text_from_audio(audio_path)
            all_text += audio_text

    # Escribe el resultado en un archivo de texto
    with open('resultado.txt', 'w', encoding="utf-8") as f:
        f.write(all_text)

max_number_of_words = 1024
system_prompt_get_ideas="""
Eres un asistente que dado un fragmento de texto incompleto puede dar al usuario las piezas de información que consideres importantes o que podrían venir como respuesta a preguntas de examen como datos concretos o conceptos.
Sólo extrae las piezas de información más relevantes que deben ser de 1 a 3 conceptos o datos concretos resumidos en una sola oración corta.
Si no hay nuevos conceptos o datos concretos entonces responde texto vacio.
Siempre sin importar que debes retornar esta lista con el siguiente formato:
concepto1
@separador
concepto2
@seperador
concepto3
Es decir, entre cada pieza de información o concepto debes incluir '@separador', es obligatorio y no puedes saltarlo.
En caso de sólo ser un concepto o dato concreto entonces no incluyas el @separador.
¡APEGATE A ESTE FORMATO Y NADA MÁS!
"""
system_prompt_explain_idea="""
Eres un asistente que dado una entrada del usuario crea una explicación breve en español que debe ser clara, precisa, objetiva, coherente y detallada, si es necesario incluir formulas o ejemplos prácticos y siempre busca crear una explicación orientada en aplicaciones a la vida real.
Debe ser un resumen, intenta no extender mucho tu respuesta.
Debes responder en el siguiente formato:
Título. (Obligatorio) ¡Siempre debe haber un título!
Contenido. (Obligatorio) Siempre debe haber contenido breve. ¡No más de un párrafo!.
Formulas. (Opcional) Si no hay formulas dejalo en blanco.
Ejemplos prácticos. (Opcional) Si no hay ejemplos prácticos dejalo en blanco.
Y asegurate de no incluir las palabras "Titulo" o ""Contenido" en tu respuesta.
"""

def get_text_segments(archivo, palabras_por_segmento):
    with open(archivo, 'r', encoding="utf-8") as f:
        texto = f.read().replace('\n', ' ')
    texto = ' '.join(texto.split())
    palabras = texto.split()
    segmentos = []
    for i in range(0, len(palabras), palabras_por_segmento):
        segmentos.append(' '.join(palabras[i:i+palabras_por_segmento]))
    return segmentos


def summarize_result():
    segments = get_text_segments('resultado.txt', max_number_of_words)
    key_ideas = []
    summary_text = ""
    for i, segment in enumerate(segments):
      # Only get the last 20 ideas from key_ideas
      all_ideas = '\n@separador\n'.join(key_ideas[-20:])
      dynamic_prompt = f"{system_prompt_get_ideas}\nNo incluyas los seiguientes conceptos que ya fueron incluidos:\n{all_ideas}\nSi no hay conceptos relevantes entonces reponde texto vacio"
      completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
          {"role": "system", "content": dynamic_prompt},
          {"role": "user", "content": segment}
        ],
        temperature=0
      )
      new_ideas = f"{completion.choices[0].message.content}".split('@separador')
      print(f"Se extrajeron {len(new_ideas)} ideas del segmento {i+1}/{len(segments)}, longitud: {len(segment.split())} palabras")
      key_ideas += new_ideas

    # Remover elementos que contengan EMPTY o sean strings vacios de la lista
    key_ideas = [x for x in key_ideas if x != 'EMPTY' and x != '']
    # Agrupamos ideas de 4 en 4 contatenandolas creando una nueva lista.
    key_ideas = ['\n'.join(key_ideas[i:i+4]) for i in range(0, len(key_ideas), 4)]

    for i, keyidea in enumerate(key_ideas):
      completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
          {"role": "system", "content": system_prompt_explain_idea},
          {"role": "user", "content": keyidea}
        ],
        temperature=0,
      )
      print(f"Se resumió la idea {i+1}/{len(key_ideas)}")
      summary_text += f"\n{completion.choices[0].message.content}\n\n"
    with open('resumen.txt', 'w', encoding="utf-8") as f:
        f.write(summary_text)

# Make a menu to select the option
def menu():
    print("1. Extraer texto de documentos")
    print("2. Resumir texto extraido")
    print("3. Convertir resumen a audio")
    print("4. Leer resumen")
    print("5. Salir")
    return int(input("Ingrese una opción: "))
# Main loop
while True:
    option = menu()
    if option == 1:
        get_text_from_docs(folder_path)
    elif option == 2:
        summarize_result()
    elif option == 3:
        with open('resumen.txt', 'r', encoding="utf-8") as f:
            text = f.read()
            text_to_audio(text)
    elif option == 4:
        with open('resumen.txt', 'r', encoding="utf-8") as f:
            text = f.read()
            read_text(text)
    elif option == 5:
        break
    else:
        print("Opción inválida")