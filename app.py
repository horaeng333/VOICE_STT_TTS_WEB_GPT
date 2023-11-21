# 함수 지향적 프로그래밍
# 실행 : streamlit run app.py

import streamlit as stl

# --------------------------UI start---------------------------#
def make_layout_main_top():
    # 1. 페이지 기본 정보 삽입, 타이틀바(탭), 화면 스타일(wide/세팅x)
    stl.set_page_config(
        page_title='Voice AI 비서 서비스', 
        layout='wide')
    pass

def make_layout_main_bottom():
    pass

def make_layout_side_bar():
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
    pass 
# --------------------------state end---------------------------#


# --------------------------special func start---------------------------#
def stt():
    pass
def tts():
    pass
def gpt_proc():
    pass
# --------------------------special func end---------------------------#


def main():
    make_layout() # 레이아웃 구성(UI)
    init_state()  # 전역 관리 상태변수 초기화 
    pass

if __name__ == '__main__':
    main()