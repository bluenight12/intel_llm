import openai

#모델 생성 및 API 키 입력
API_KEY = "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" # OpenAI API 키 입력
client = openai.OpenAI(api_key = API_KEY)
# 녹음파일 열기pip
audio_file = open("output.mp3", "rb")
# whisper 모델에 음원파일 전달하기
transcript = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
#결과 보기
print(transcript.text)