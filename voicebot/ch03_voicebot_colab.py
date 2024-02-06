{"nbformat":4,"nbformat_minor":0,"metadata":{"colab":{"provenance":[],"authorship_tag":"ABX9TyMzPf0MTxDWMMDliBtz86em"},"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"}},"cells":[{"cell_type":"code","source":["##### 기본 정보 입력 #####\n","import streamlit as st\n","# audiorecorder 패키지 추가\n","from audiorecorder import audiorecorder\n","# OpenAI 패키지 추가\n","import openai\n","# 파일 삭제를 위한 패키지 추가\n","import os\n","# 시간 정보를 위한 패키지 추가\n","from datetime import datetime\n","# TTS 패키기 추가\n","from gtts import gTTS\n","# 음원 파일 재생을 위한 패키지 추가\n","import base64\n","\n","##### 기능 구현 함수 #####\n","def STT(audio):\n","    # 파일 저장\n","    filename='input.mp3'\n","    audio.export(filename, format=\"mp3\")\n","    # 음원 파일 열기\n","    audio_file = open(filename, \"rb\")\n","    # Whisper 모델을 활용해 텍스트 얻기\n","    transcript = openai.Audio.transcribe(\"whisper-1\", audio_file)\n","    audio_file.close()\n","    # 파일 삭제\n","    os.remove(filename)\n","    return transcript[\"text\"]\n","\n","def ask_gpt(prompt, model):\n","    response = openai.ChatCompletion.create(model=model, messages=prompt)\n","    system_message = response[\"choices\"][0][\"message\"]\n","    return system_message[\"content\"]\n","\n","def TTS(response):\n","    # gTTS 를 활용하여 음성 파일 생성\n","    filename = \"output.mp3\"\n","    tts = gTTS(text=response,lang=\"ko\")\n","    tts.save(filename)\n","\n","    # 음원 파일 자동 재생생\n","    with open(filename, \"rb\") as f:\n","        data = f.read()\n","        b64 = base64.b64encode(data).decode()\n","        md = f\"\"\"\n","            <audio autoplay=\"True\">\n","            <source src=\"data:audio/mp3;base64,{b64}\" type=\"audio/mp3\">\n","            </audio>\n","            \"\"\"\n","        st.markdown(md,unsafe_allow_html=True,)\n","    # 파일 삭제\n","    os.remove(filename)\n","\n","##### 메인 함수 #####\n","def main():\n","    # 기본 설정\n","    st.set_page_config(\n","        page_title=\"음성 비서 프로그램\",\n","        layout=\"wide\")\n","\n","    # session state 초기화\n","    if \"chat\" not in st.session_state:\n","        st.session_state[\"chat\"] = []\n","\n","    if \"messages\" not in st.session_state:\n","        st.session_state[\"messages\"] = [{\"role\": \"system\", \"content\": \"You are a thoughtful assistant. Respond to all input in 25 words and answer in korea\"}]\n","\n","    if \"check_reset\" not in st.session_state:\n","        st.session_state[\"check_reset\"] = False\n","\n","    # 제목\n","    st.header(\"음성 비서 프로그램\")\n","    # 구분선\n","    st.markdown(\"---\")\n","\n","    # 기본 설명\n","    with st.expander(\"음성비서 프로그램에 관하여\", expanded=True):\n","        st.write(\n","        \"\"\"\n","        - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.\n","        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다.\n","        - 답변은 OpenAI의 GPT 모델을 활용했습니다.\n","        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.\n","        \"\"\"\n","        )\n","\n","        st.markdown(\"\")\n","\n","    # 사이드바 생성\n","    with st.sidebar:\n","\n","        # Open AI API 키 입력받기\n","        openai.api_key = st.text_input(label=\"OPENAI API 키\", placeholder=\"Enter Your API Key\", value=\"\", type=\"password\")\n","\n","        st.markdown(\"---\")\n","\n","        # GPT 모델을 선택하기 위한 라디오 버튼 생성\n","        model = st.radio(label=\"GPT 모델\",options=[\"gpt-4\", \"gpt-3.5-turbo\"])\n","\n","        st.markdown(\"---\")\n","\n","        # 리셋 버튼 생성\n","        if st.button(label=\"초기화\"):\n","            # 리셋 코드\n","            st.session_state[\"chat\"] = []\n","            st.session_state[\"messages\"] = [{\"role\": \"system\", \"content\": \"You are a thoughtful assistant. Respond to all input in 25 words and answer in korea\"}]\n","            st.session_state[\"check_reset\"] = True\n","\n","    # 기능 구현 공간\n","    col1, col2 =  st.columns(2)\n","    with col1:\n","        # 왼쪽 영역 작성\n","        st.subheader(\"질문하기\")\n","        # 음성 녹음 아이콘 추가\n","        audio = audiorecorder(\"클릭하여 녹음하기\", \"녹음중...\")\n","        if (audio.duration_seconds > 0) and (st.session_state[\"check_reset\"]==False):\n","            # 음성 재생\n","            st.audio(audio.export().read())\n","            # 음원 파일에서 텍스트 추출\n","            question = STT(audio)\n","\n","            # 채팅을 시각화하기 위해 질문 내용 저장\n","            now = datetime.now().strftime(\"%H:%M\")\n","            st.session_state[\"chat\"] = st.session_state[\"chat\"]+ [(\"user\",now, question)]\n","            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장\n","            st.session_state[\"messages\"] = st.session_state[\"messages\"]+ [{\"role\": \"user\", \"content\": question}]\n","\n","    with col2:\n","        # 오른쪽 영역 작성\n","        st.subheader(\"질문/답변\")\n","        if  (audio.duration_seconds > 0)  and (st.session_state[\"check_reset\"]==False):\n","            # ChatGPT에게 답변 얻기\n","            response = ask_gpt(st.session_state[\"messages\"], model)\n","\n","            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장\n","            st.session_state[\"messages\"] = st.session_state[\"messages\"]+ [{\"role\": \"system\", \"content\": response}]\n","\n","            # 채팅 시각화를 위한 답변 내용 저장\n","            now = datetime.now().strftime(\"%H:%M\")\n","            st.session_state[\"chat\"] = st.session_state[\"chat\"]+ [(\"bot\",now, response)]\n","\n","            # 채팅 형식으로 시각화 하기\n","            for sender, time, message in st.session_state[\"chat\"]:\n","                if sender == \"user\":\n","                    st.write(f'<div style=\"display:flex;align-items:center;\"><div style=\"background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;\">{message}</div><div style=\"font-size:0.8rem;color:gray;\">{time}</div></div>', unsafe_allow_html=True)\n","                    st.write(\"\")\n","                else:\n","                    st.write(f'<div style=\"display:flex;align-items:center;justify-content:flex-end;\"><div style=\"background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;\">{message}</div><div style=\"font-size:0.8rem;color:gray;\">{time}</div></div>', unsafe_allow_html=True)\n","                    st.write(\"\")\n","\n","            # gTTS 를 활용하여 음성 파일 생성 및 재생\n","            TTS(response)\n","        else:\n","            st.session_state[\"check_reset\"] = False\n","\n","if __name__==\"__main__\":\n","    main()"],"metadata":{"colab":{"base_uri":"https://localhost:8080/","height":576},"id":"5z2ZrBur4MFC","executionInfo":{"status":"error","timestamp":1706945880307,"user_tz":-540,"elapsed":686,"user":{"displayName":"EropeConsulting erope3v","userId":"02383037699136280687"}},"outputId":"fa9813f0-b417-4b04-bf22-70bfec871133"},"execution_count":17,"outputs":[{"output_type":"error","ename":"ImportError","evalue":"cannot import name 'Iterator' from 'typing_extensions' (/usr/local/lib/python3.10/dist-packages/typing_extensions.py)","traceback":["\u001b[0;31m---------------------------------------------------------------------------\u001b[0m","\u001b[0;31mImportError\u001b[0m                               Traceback (most recent call last)","\u001b[0;32m<ipython-input-17-c1d63ad99d09>\u001b[0m in \u001b[0;36m<cell line: 6>\u001b[0;34m()\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0maudiorecorder\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0maudiorecorder\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;31m# OpenAI 패키지 추가\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 6\u001b[0;31m \u001b[0;32mimport\u001b[0m \u001b[0mopenai\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      7\u001b[0m \u001b[0;31m# 파일 삭제를 위한 패키지 추가\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      8\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mos\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/__init__.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m      6\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0mtyping_extensions\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0moverride\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      7\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 8\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mtypes\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      9\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0m_types\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mNoneType\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mTransport\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mProxiesTypes\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     10\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0m_utils\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mfile_from_path\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/types/__init__.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m      3\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0m__future__\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mannotations\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 5\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0mimage\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mImage\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mImage\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      6\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0mmodel\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mModel\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mModel\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      7\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0mshared\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mFunctionDefinition\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mFunctionDefinition\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mFunctionParameters\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mFunctionParameters\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/types/image.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m      3\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0mtyping\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mOptional\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 5\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_models\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mBaseModel\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      6\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      7\u001b[0m \u001b[0m__all__\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0;34m[\u001b[0m\u001b[0;34m\"Image\"\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/_models.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m     31\u001b[0m     \u001b[0mHttpxRequestFiles\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     32\u001b[0m )\n\u001b[0;32m---> 33\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0m_utils\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mis_list\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mis_given\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mis_mapping\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mparse_date\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mparse_datetime\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mstrip_not_given\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     34\u001b[0m from ._compat import (\n\u001b[1;32m     35\u001b[0m     \u001b[0mPYDANTIC_V2\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/_utils/__init__.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m     39\u001b[0m     \u001b[0mextract_type_var_from_base\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mextract_type_var_from_base\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     40\u001b[0m )\n\u001b[0;32m---> 41\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0;34m.\u001b[0m\u001b[0m_streams\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mconsume_sync_iterator\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mconsume_sync_iterator\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mconsume_async_iterator\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mconsume_async_iterator\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     42\u001b[0m from ._transform import (\n\u001b[1;32m     43\u001b[0m     \u001b[0mPropertyInfo\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mPropertyInfo\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;32m/usr/local/lib/python3.10/dist-packages/openai/_utils/_streams.py\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m      1\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0mtyping\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mAny\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 2\u001b[0;31m \u001b[0;32mfrom\u001b[0m \u001b[0mtyping_extensions\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mIterator\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mAsyncIterator\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      3\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;32mdef\u001b[0m \u001b[0mconsume_sync_iterator\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0miterator\u001b[0m\u001b[0;34m:\u001b[0m \u001b[0mIterator\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0mAny\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m)\u001b[0m \u001b[0;34m->\u001b[0m \u001b[0;32mNone\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;31mImportError\u001b[0m: cannot import name 'Iterator' from 'typing_extensions' (/usr/local/lib/python3.10/dist-packages/typing_extensions.py)","","\u001b[0;31m---------------------------------------------------------------------------\u001b[0;32m\nNOTE: If your import is failing due to a missing package, you can\nmanually install dependencies using either !pip or !apt.\n\nTo view examples of installing some common dependencies, click the\n\"Open Examples\" button below.\n\u001b[0;31m---------------------------------------------------------------------------\u001b[0m\n"],"errorDetails":{"actions":[{"action":"open_url","actionText":"Open Examples","url":"/notebooks/snippets/importing_libraries.ipynb"}]}}]}]}