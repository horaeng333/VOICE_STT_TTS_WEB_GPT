# 함수 지향적 프로그래밍
# 실행 : streamlit run app.py
# 종료 : ctrl+C

import streamlit as stl
from openai import OpenAI
from audiorecorder import audiorecorder
import numpy as np
import os

# global variable(전역변수)
client = None

# --------------------------UI start---------------------------#
def make_layout_main_top():
    # 1. 페이지 기본 정보 삽입, 타이틀바(탭), 화면 스타일(wide/세팅x)
    stl.set_page_config(
        page_title='Voice AI 비서 서비스', 
        layout='wide'
        )
    # 2. 메인 페이지 제목 설정
    stl.header('Voice AI S/W')
    # 3. 구분선 -> markdown 문법
    stl.markdown('---')
    # 4. 기본 설명
    # 접기 기능
    with stl.expander('with this s/w', expanded=True):
        stl.write(
            '''
                - 프로그램 설명
                - Streamlit, STT(gpt의 Whisper 사용), 답변(GPT), TTS(구글의 Translate TTS)
            '''
        )
        stl.markdown('')
    pass

def make_layout_side_bar():
    global client # 글로벌 변수 client 불러오기 
    # 사이드바 생성
    with stl.sidebar:
        # openai key 입력, 엔터키를 입력하면 자동 이벤트 처리돼어 리턴한다.
        api_key = stl.text_input(placeholder='API 키를 입력하세요', label='OPEN API KEY', type='password')
        #print(api_key)
        if api_key.strip():
            # 정상입력
            try:
                # api 키가 틀려도 오류 발생 X, 실제 사용 때 문제됨 
                client = OpenAI(api_key=api_key)
                print('client --> ', client)
            except Exception:
                # 팝업
                print('API키가 부적절합니다. 다시 시도하세요')
            pass
        else:
            print('정확하게 입력하세요')
            pass
        
        stl.markdown('---')
        
        # GPT 모델 선택(여러 목록 중 한 개 선택 -> radio or select)
        global model_name
        model_name = stl.radio(label='GPT 모델', options=['gtp-4', 'gpt-3.5-turbo'])
        
        stl.markdown('---')
        
        # 전역 상태 변수 초기화 -> 클릭하면 처리됨 
        if stl.button(label='상태 초기화'):
            print('상태 초기화 실행')
            init_state()
            pass
        
        
        pass
    pass

def make_layout_main_bottom():
    # 보이스->질의 , 채팅데이터 구성 완료됐음을 아는 변수가 필요 (flag)
    is_stt_complete_flag = False
    # 공통
    left, right = stl.columns(2)
    # 왼쪽 : 오디오 입력 및 재생
    with left:
        # 부제목
        stl.subheader('음성 질문')
        # 음성 녹음  버튼 추가
        audio_arr = audiorecorder(record_prompt='클릭하여 녹음 시작', recording_prompt='레코딩중...')
        print(len(audio_arr), audio_arr.shape)
        # 새로운 음성 데이터가 존재하고, 기존에 저장한 음성 데이터와 다르다면
        if len(audio_arr) > 0 and not np.array_equal(audio_arr, stl.session_state['audio_check']):
            # 음성 재생 -> <audio> -> 음원 삽입(배열->바이트들) -> 재생바 생성 -> 클릭 -> 재생
            stl.audio(audio_arr.tobytes())
            # 음원 파일에서 텍스트 추출 (STT)
            question = stt(audio_arr)
            print('question -> ', question)
            # 채팅창에 내용을 넣기 위한 준비
            now_str = datetime.now().strftime('%H:%M')
            # 채팅창에 보일 내용 세팅( 전역 세션 상태 변수에 저장 )
            stl.session_state['chat'] = stl.session_state['chat'] + [('user', now_str, question)]
            # GPT 모델에 질의한 프롬프트
            stl.session_state['msg'] = stl.session_state['msg'] + [
                {
                    'role':'user',
                    'content':question
                }
            ]
            # 오디오 저장
            stl.session_state['audio_check'] = audio_arr
            # STT 저장
            is_stt_complete_flag = True
        pass
    # 오른쪽 : 채팅창
    with right:
        # 부제목
        stl.subheader('채팅창')
        # STT가 완료된 상황에서만 진행
        if is_stt_complete_flag:
            # GPT에게 질의
            response = gpt_proc(stl.session_state['msg'])
            print('GPT 응답', response)
            pass
        pass
    pass

def make_layout():
    # 메인 페이지 상단(UI 기본 연습 - 타이틀,등등..)
    make_layout_main_top()
    # 메인 페이지 하단(UI 음성 녹음, 채팅 목록)
    make_layout_main_bottom()
    # 왼쪽 사이드바(openai API key 입력, 모델 선택(gpt-3.5-turbo or 4))
    make_layout_side_bar()
    pass
# --------------------------UI end---------------------------#


# --------------------------state start---------------------------#
def init_state():
    # 스트림릿의 상태를 저장, 이벤트 발생 => 코드가 처음부터 재실행 => 입력받은 값들(키, 모델명) 모두 초기화 됨.(전역변수 제외)
    # session_state 라는 전역 관리 공간을 제공, 여기에 필요한 내용 저장해 두면 됨 
    if 'chat' not in stl.session_state:
        stl.session_state['chat'] = [] # 세션상태 저장공간에 'chat'이라는 키를 생성 
        
    if 'msg' not in stl.session_state:
        stl.session_state['msg'] = [
            {
                # 페르소나 부여
                'role':'system',
                # 영어로 부여
                'content': 'You are a thoughtful assistant. Respond to all input in 25 words and answer in Korean'
            }
        ]
        
    # audio 버퍼 체크
    if 'audio_check' not in stl.session_state:
        stl.session_state['audio_check'] = []
        
         
        pass
    pass 
# --------------------------state end---------------------------#


# --------------------------special func start---------------------------#
def stt(audio_arr):
    try:
        # 데이터 전처리
        filename = 'input_voice.mp3'
        # 파일기록
        with open(filename, 'wb') as f:
            f.write(audio_arr.tobytes())
            
        with open(filename, 'rb') as audio_file:   
            # GPT를 이용한 STT 처리
            transcript = client.audio.transcriptions.create(
                model='whisper-1',
                file= audio_file,
                response_format='text'
            )
            
        # 삭제 처리
        os.remove(filename)
        
        # 텍스트 응답 
        return transcript.strip()
    except Exception as e:
        print('STT 변환 오류', e)
        return '[E-001] STT 변환 오류'
    pass 
def tts():
    pass
def gpt_proc(prompt):
    global client
    global model_name
    response = client.chat.completions.create(
        model    = model_name,  
        messages = prompt,      
        #temperature = 0,           
    )
    return response.choices[0].message.content
    pass
# --------------------------special func end---------------------------#


def main():
    make_layout() # 레이아웃 구성(UI)
    init_state()  # 전역 관리 상태변수 초기화 
    pass

if __name__ == '__main__':
    main()