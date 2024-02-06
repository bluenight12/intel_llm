{"nbformat":4,"nbformat_minor":0,"metadata":{"colab":{"provenance":[],"authorship_tag":"ABX9TyPNHQwEgmougQfjucfCsUM5"},"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"}},"cells":[{"cell_type":"code","execution_count":1,"metadata":{"colab":{"base_uri":"https://localhost:8080/","height":400},"id":"aXFD4rUgy3ov","executionInfo":{"status":"error","timestamp":1706960879226,"user_tz":-540,"elapsed":9,"user":{"displayName":"EropeConsulting erope3v","userId":"02383037699136280687"}},"outputId":"981be452-d886-4d0a-ca30-830eb3eb4121"},"outputs":[{"output_type":"error","ename":"ModuleNotFoundError","evalue":"No module named 'openai'","traceback":["\u001b[0;31m---------------------------------------------------------------------------\u001b[0m","\u001b[0;31mModuleNotFoundError\u001b[0m                       Traceback (most recent call last)","\u001b[0;32m<ipython-input-1-57a9b992b4a7>\u001b[0m in \u001b[0;36m<cell line: 3>\u001b[0;34m()\u001b[0m\n\u001b[1;32m      1\u001b[0m \u001b[0;31m###### 기본 정보 설정 단계 #######\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      2\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mjson\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 3\u001b[0;31m \u001b[0;32mimport\u001b[0m \u001b[0mopenai\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      4\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mthreading\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mtime\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n","\u001b[0;31mModuleNotFoundError\u001b[0m: No module named 'openai'","","\u001b[0;31m---------------------------------------------------------------------------\u001b[0;32m\nNOTE: If your import is failing due to a missing package, you can\nmanually install dependencies using either !pip or !apt.\n\nTo view examples of installing some common dependencies, click the\n\"Open Examples\" button below.\n\u001b[0;31m---------------------------------------------------------------------------\u001b[0m\n"],"errorDetails":{"actions":[{"action":"open_url","actionText":"Open Examples","url":"/notebooks/snippets/importing_libraries.ipynb"}]}}],"source":["###### 기본 정보 설정 단계 #######\n","import json\n","import openai\n","import threading\n","import time\n","import queue as q\n","import os\n","\n","# OpenAI API KEY\n","client = openai.OpenAI(api_key = os.environ['OPENAI_API'])\n","\n","###### 메인 함수 단계 #######\n","\n","# 메인 함수\n","def lambda_handler(event, context):\n","\n","    run_flag = False\n","    start_time = time.time()\n","    # 카카오 정보 저장\n","    kakaorequest = json.loads(event['body'])\n","    # 응답 결과를 저장하기 위한 텍스트 파일 생성\n","\n","    filename =\"/tmp/botlog.txt\"\n","    if not os.path.exists(filename):\n","        with open(filename, \"w\") as f:\n","            f.write(\"\")\n","    else:\n","        print(\"File Exists\")\n","\n","    # 답변 생성 함수 실행\n","    response_queue = q.Queue()\n","    request_respond = threading.Thread(target=responseOpenAI,\n","                                        args=(kakaorequest, response_queue,filename))\n","    request_respond.start()\n","\n","    # 답변 생성 시간 체크\n","    while (time.time() - start_time < 3.5):\n","        if not response_queue.empty():\n","            # 3.5초 안에 답변이 완성되면 바로 값 리턴\n","            response = response_queue.get()\n","            run_flag= True\n","            break\n","        # 안정적인 구동을 위한 딜레이 타임 설정\n","        time.sleep(0.01)\n","\n","    # 3.5초 내 답변이 생성되지 않을 경우\n","    if run_flag== False:\n","        response = timeover()\n","\n","    return{\n","        'statusCode':200,\n","        'body': json.dumps(response),\n","        'headers': {\n","            'Access-Control-Allow-Origin': '*',\n","        }\n","    }\n","\n","# 답변/사진 요청 및 응답 확인 함수\n","def responseOpenAI(request,response_queue,filename):\n","    # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시\n","    if '생각 다 끝났나요?' in request[\"userRequest\"][\"utterance\"]:\n","        # 텍스트 파일 열기\n","        with open(filename) as f:\n","            last_update = f.read()\n","        # 텍스트 파일 내 저장된 정보가 있을 경우\n","        if len(last_update.split())>1:\n","            kind = last_update.split()[0]\n","            if kind == \"img\":\n","                bot_res, prompt = last_update.split()[1],last_update.split()[2]\n","                response_queue.put(imageResponseFormat(bot_res,prompt))\n","            else:\n","                bot_res = last_update[4:]\n","                response_queue.put(textResponseFormat(bot_res))\n","            dbReset(filename)\n","\n","    # 이미지 생성을 요청한 경우\n","    elif '/img' in request[\"userRequest\"][\"utterance\"]:\n","        dbReset(filename)\n","        prompt = request[\"userRequest\"][\"utterance\"].replace(\"/img\", \"\")\n","        bot_res = getImageURLFromDALLE(prompt)\n","        response_queue.put(imageResponseFormat(bot_res,prompt))\n","        save_log = \"img\"+ \" \" + str(bot_res) + \" \" + str(prompt)\n","        with open(filename, 'w') as f:\n","            f.write(save_log)\n","\n","    # ChatGPT 답변을 요청한 경우\n","    elif '/ask' in request[\"userRequest\"][\"utterance\"]:\n","        dbReset(filename)\n","        prompt = request[\"userRequest\"][\"utterance\"].replace(\"/ask\", \"\")\n","        bot_res = getTextFromGPT(prompt)\n","        response_queue.put(textResponseFormat(bot_res))\n","\n","        save_log = \"ask\"+ \" \" + str(bot_res)\n","        with open(filename, 'w') as f:\n","            f.write(save_log)\n","\n","    #아무 답변 요청이 없는 채팅일 경우\n","    else:\n","        # 기본 response 값\n","        base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}\n","        response_queue.put(base_response)\n","\n","###### 기능 구현 단계 #######\n","\n","# 메세지 전송\n","def textResponseFormat(bot_response):\n","    response = {'version': '2.0', 'template': {\n","    'outputs': [{\"simpleText\": {\"text\": bot_response}}], 'quickReplies': []}}\n","    return response\n","\n","# 사진 전송\n","def imageResponseFormat(bot_response,prompt):\n","    output_text = prompt+\"내용에 관한 이미지 입니다\"\n","    response = {'version': '2.0', 'template': {\n","    'outputs': [{\"simpleImage\": {\"imageUrl\": bot_response,\"altText\":output_text}}], 'quickReplies': []}}\n","    return response\n","\n","# 응답 초과시 답변\n","def timeover():\n","    response = {\"version\":\"2.0\",\"template\":{\n","      \"outputs\":[\n","         {\n","            \"simpleText\":{\n","               \"text\":\"아직 제가 생각이 끝나지 않았어요??\\n잠시후 아래 말풍선을 눌러주세요?\"\n","            }\n","         }\n","      ],\n","      \"quickReplies\":[\n","         {\n","            \"action\":\"message\",\n","            \"label\":\"생각 다 끝났나요??\",\n","            \"messageText\":\"생각 다 끝났나요?\"\n","         }]}}\n","    return response\n","\n","# ChatGPT에게 질문/답변 받기\n","def getTextFromGPT(messages):\n","    messages_prompt = [{\"role\": \"system\", \"content\": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]\n","    messages_prompt += [{\"role\": \"user\", \"content\": messages}]\n","    response = client.chat.completions.create(model=\"gpt-3.5-turbo\", messages=messages_prompt)\n","    message = response.choices[0].message.content\n","    return message\n","\n","# DALLE 에게 질문/그림 URL 받기\n","def getImageURLFromDALLE(messages):\n","    response = client.images.generate(\n","    model=\"dall-e-2\",\n","    prompt=messages,\n","    size=\"512x512\",\n","    quality=\"standard\",\n","    n=1)\n","    image_url = response.data[0].url\n","    return image_url\n","\n","# 텍스트파일 초기화\n","def dbReset(filename):\n","    with open(filename, 'w') as f:\n","        f.write(\"\")"]}]}