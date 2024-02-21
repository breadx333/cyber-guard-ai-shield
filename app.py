from flask import Flask, request, render_template
from google.cloud import speech_v1p1beta1 as speech
import google.generativeai as genai

app = Flask(__name__)

client = speech.SpeechClient.from_service_account_file('google_secret_key.json')

genai.configure(api_key="AIzaSyDGUEkj5M2cjBIVLjfvCxJbq6O0ypnoxwI")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return 'No file part'
    
    audio_file = request.files['audio']

    if audio_file.filename == '':
        return 'No selected file'

    # Transcribe audio file
    content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
        diarization_config=diarization_config,
    )

    response = client.recognize(config=config, audio=audio)

    # all_text = []

    # for phrase in response.results:
    #     best_alternative = phrase.alternatives[0]
    #     all_text.append(best_alternative)
    
    # print(" ".join(convert_to_text(response)))

    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    # prompt_parts = [ "Диалог: " + " ".join(convert_to_text(response)) + "Ответь пожалуйста, это мошенничество да или нет?"
    # ]

    prompt_parts = [ "Dialogue: " + " ".join(convert_to_text(response)) + "\n\nAnswer this is a fraud, yes or no? And ask me why?"
    ]

    response_gemini = model.generate_content(prompt_parts)
    answer_from_gemini = response_gemini.text


    # print(response)

    # Get transcription result
    # transcription = ""
    # for result in response.results:
    #     transcription += result.alternatives[0].transcript + " "

    return answer_from_gemini #"testing" #transcription

def convert_to_text(response: speech.RecognizeResponse):
    all_text = []
    for phrase in response.results:
        all_text.append(get_text_from_audio(phrase))
    return all_text

def get_text_from_audio(result: speech.SpeechRecognitionResult):
    best_alternative = result.alternatives[0]
    return best_alternative.transcript

if __name__ == '__main__':
    app.run(debug=True, port=5001)
