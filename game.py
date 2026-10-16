# =========================================================
# 잠꾸러기 꼬물이의 엄마 찾기
# 4단계: 돌발 상황 해결 - 상어 아저씨를 마주치면 3초 안에 [숨기]!
# =========================================================
# 실행 방법: 터미널에서  python game.py
#
# [처음 보는 용어]
# - tkinter : 파이썬에 기본으로 들어 있는 "창(윈도우) 만들기 도구". 따로 설치할 필요가 없다.
# - 위젯(widget) : 창 안에 들어가는 부품. 글자(Label), 버튼(Button), 그림판(Canvas), 묶음 상자(Frame) 등.
# - 함수(def) : 여러 줄의 명령을 묶어 이름을 붙인 것. 버튼을 누르면 연결된 함수가 실행된다.
# - # 기호 : 이 기호 뒤의 글은 "주석". 컴퓨터는 무시하고 사람만 읽는 설명이다.

import tkinter as tk   # tkinter를 tk라는 짧은 이름으로 불러온다
import random          # 무작위(랜덤) 도구. 판마다 단서·손님 위치를 다르게 숨기려고 쓴다 (설치 필요 없음)


# ---------------------------------------------------------
# 1) 게임 설정값과 상태 변수
# ---------------------------------------------------------
# 이름이 전부 대문자인 변수 = "게임 중에 바뀌지 않는 설정값"이라는 프로그래머들의 약속
# → 게임 규칙(숫자)을 바꾸고 싶으면 여기만 고치면 된다!
GOAL_CLUES = 3        # 엄마를 찾는 데 필요한 단서 수
START_TIME = 60       # 제한 시간(초)
MAX_TIRED = 10        # 피로도가 이 값이 되면 꼬물이가 잠든다
TIRED_PER_MOVE = 2    # 한 번 돌아다닐 때마다 오르는 피로도 (아기라서 금방 지친다)
SLEEP_PENALTY = 5     # 잠들면 잃는 시간(초)
STRETCH_RECOVER = 1   # 기지개를 켜면 내려가는 피로도
STRETCH_COST = 2      # 기지개를 켜는 데 드는 시간(초)
SWIM_COST = 3         # 한 장소로 헤엄쳐 가는 데 걸리는 시간(초)
                      # 이유: 버튼 클릭은 순식간이라 이게 없으면 60초가 너무 넉넉하다. 0으로 바꾸면 기능이 꺼진다.
HIDE_SECONDS = 3      # 상어 아저씨를 마주쳤을 때 [숨기]를 누를 수 있는 시간(초)
SHARK_PENALTY = 3     # 숨지 못하고 상어 아저씨에게서 도망칠 때 잃는 시간(초)
WHALE_TIRED = 3       # 고래 물살에 휩쓸려 오르는 피로도

FONT = "Malgun Gothic"   # 윈도우에 기본으로 있는 한글 글꼴(맑은 고딕)

# 장소 8곳: { 장소이름: 이모지 } 형태의 딕셔너리
# { } 는 "딕셔너리": 이름표(키)로 값을 찾아 쓰는 상자. PLACES["난파선"] → "🚢"
PLACES = {
    "산호숲": "🪸", "난파선": "🚢", "해초밭": "🌿", "조개밭": "🐚",
    "바위굴": "🪨", "문어집": "🐙", "거북길": "🐢", "보물상자": "💎",
}

# 8곳에 숨길 내용물 8개: 단서 3 + 꽝 3 + 손님 2 (판마다 섞어서 장소에 하나씩 나눠 준다)
# [ ] 는 "리스트": 값을 순서대로 담는 상자. ["단서"] * 3 → ["단서", "단서", "단서"]
# + 는 리스트끼리 이어 붙이기
PLACE_CONTENTS = ["단서"] * 3 + ["꽝"] * 3 + ["상어", "고래"]

# 단서를 찾을 때 순서대로 보여 줄 글 (CLUE_TEXTS[0]이 첫 번째. 번호는 0부터 센다!)
CLUE_TEXTS = [
    "엄마 지느러미에서 떨어진 반짝이 비늘을 찾았어요!",
    "엄마가 남긴 물방울 편지를 찾았어요! '꼬물아, 금방 올게~'",
    "엄마 냄새가 나는 해초를 찾았어요! 엄마가 가까이 있어요!",
]

# 아래 변수들은 게임 중에 계속 바뀌는 "상태" 값이다
clues = 0                # 지금까지 모은 단서 수
time_left = START_TIME   # 남은 시간
tired = 0                # 피로도 (0 ~ 10)
playing = False          # 게임이 진행 중인지 (True = 진행 중, False = 멈춤)
place_contents = {}      # 이번 판의 { 장소이름: 숨겨진 내용물 } 예) {"산호숲": "꽝", "난파선": "상어", ...}
visited = []             # 이미 가 본 장소 이름 목록 (상어 소동이 끝난 뒤 "안 가 본 곳"만 다시 열어 주려고)
timer_id = None          # 지금 예약된 타이머의 번호표 (None = "아무것도 없음"이라는 뜻)
place_buttons = {}       # { 장소이름: 버튼 } → 나중에 특정 장소 버튼의 글자·색을 바꾸려고 모아 둔다

shark_mode = False       # 지금 상어 아저씨와 마주친 중인지 (True면 [숨기]만 누를 수 있다)
hide_left = 0            # 숨을 수 있는 남은 시간(초)
shark_timer_id = None    # 상어 카운트다운 타이머의 번호표


# ---------------------------------------------------------
# 2) 화면 표시용 함수들
# ---------------------------------------------------------
def make_bar(value, max_value):
    """수치를 ■□ 막대 글자로 바꾼다.
    이유: 숫자만 보면 감이 안 오니까, 소리 없이도 눈으로 한눈에 보이게 하려고."""
    value = min(value, max_value)               # min : 둘 중 작은 값. 최대치를 넘어도 막대가 넘치지 않게
    filled = value * 10 // max_value            # // 는 "나눈 뒤 소수점 버리기" (예: 4*10//10 = 4)
    return "■" * filled + "□" * (10 - filled)    # 문자열 * 숫자 = 그 횟수만큼 반복 ("■"*3 → "■■■")


# 알림 종류별 [앞에 붙일 표시, 배경색]
NOTICE_STYLE = {
    "info": ("📢", "#e3f2fd"),   # 안내 = 하늘색
    "good": ("✅", "#c8e6c9"),   # 성공 = 초록색
    "bad":  ("⚠", "#ffcdd2"),    # 위험/실패 = 빨간색
}


def show_notice(message, kind):
    """알림창에 글을 띄운다. 종류(kind)에 따라 표시 기호와 배경색이 바뀐다.
    이유: 소리가 없어도 '글자 + 기호 + 색' 세 가지로 무슨 일인지 알 수 있게 하려고."""
    mark, color = NOTICE_STYLE[kind]   # 두 값을 한 번에 꺼내서 mark, color에 나눠 담는다
    notice_label.config(text=f"{mark} {message}", bg=color)
    # .config(...) : 이미 만든 위젯의 글자·색 등을 바꾸는 명령
    # f"..." : f-문자열. 따옴표 안의 {변수}가 실제 값으로 바뀐다


def update_screen():
    """상태 변수(시간·단서·피로도)를 화면 글자에 반영한다.
    이유: 값이 바뀔 때마다 이 함수 하나만 부르면 화면이 최신 상태가 된다."""
    if time_left <= 10:   # 10초 이하이면 글자색을 빨갛게 + "서둘러요!" (소리 대신 눈으로 경고)
        status_label.config(text=f"⏱ 남은 시간: {time_left}초 (서둘러요!)    🔍 단서: {clues} / {GOAL_CLUES}",
                            fg="#ff8a80")
    else:
        status_label.config(text=f"⏱ 남은 시간: {time_left}초      🔍 단서: {clues} / {GOAL_CLUES}",
                            fg="white")
    tired_label.config(text=f"😴 피로도: {make_bar(tired, MAX_TIRED)} {tired} / {MAX_TIRED}")


def draw_background():
    """그림판(Canvas)에 바닷속 배경을 그린다. (프로그램 시작 때 한 번만)"""
    # 좌표: 그림판 왼쪽 위가 (0, 0). x는 오른쪽으로, y는 아래로 갈수록 커진다.
    canvas.create_rectangle(0, 200, 480, 240, fill="#e3c98b", outline="")   # 모래 바닥

    # 해초 4개: for 반복문으로 x 위치만 바꿔 가며 같은 모양을 4번 그린다
    for x in (40, 70, 400, 430):
        canvas.create_polygon(x, 200, x - 10, 150, x + 5, 110, x + 10, 160, x + 15, 200,
                              fill="#2e8b57", smooth=True)   # smooth=True : 꼭짓점을 둥글게

    # 물방울 4개: (x, y, 반지름) 묶음을 하나씩 꺼내서 원을 그린다
    for (x, y, r) in [(120, 60, 6), (140, 40, 4), (360, 80, 7), (380, 50, 5)]:
        canvas.create_oval(x - r, y - r, x + r, y + r, outline="white", width=2)


def draw_fish(awake):
    """꼬물이를 그린다. awake가 True면 눈 뜬 모습, False면 자는 모습."""
    canvas.delete("fish")   # "fish" 꼬리표(tag)가 붙은 그림만 지운다 → 배경은 그대로 남는다
    canvas.create_polygon(200, 130, 165, 105, 165, 155, fill="#ff9f43", tags="fish")   # 꼬리
    canvas.create_oval(195, 105, 285, 155, fill="#ffb74d", outline="#e67e22", width=2, tags="fish")  # 몸통
    if awake:
        canvas.create_oval(258, 118, 268, 128, fill="black", tags="fish")   # 동그란 눈
    else:
        canvas.create_line(256, 124, 270, 124, width=3, tags="fish")          # 감은 눈(가로줄)
        canvas.create_text(305, 90, text="Z z z", fill="white",
                           font=(FONT, 16, "bold"), tags="fish")
    canvas.create_text(240, 175, text="꼬물이", fill="white", font=(FONT, 11, "bold"), tags="fish")


# 상어·고래·엄마처럼 "잠깐 나왔다 사라지는 그림"에는 모두 "scene" 꼬리표를 붙인다.
# → canvas.delete("scene") 한 줄로 한꺼번에 지울 수 있다.
def clear_scene():
    canvas.delete("scene")


def draw_shark(message):
    """오른쪽 위에 상어 아저씨를 그린다. message는 상어 아래에 쓸 글자."""
    clear_scene()
    # 몸통: 점 여러 개를 이어 만든 다각형(polygon). smooth=True로 매끈한 곡선이 된다
    canvas.create_polygon(315, 75, 360, 48, 440, 55, 452, 75, 440, 95, 360, 102,
                          fill="#78909c", outline="#455a64", width=2, smooth=True, tags="scene")
    canvas.create_polygon(378, 54, 398, 18, 416, 56, fill="#78909c", tags="scene")      # 등지느러미
    canvas.create_polygon(446, 75, 476, 45, 466, 75, 476, 105, fill="#78909c", tags="scene")  # 꼬리
    canvas.create_oval(338, 63, 348, 73, fill="black", tags="scene")                     # 눈
    canvas.create_line(322, 84, 328, 90, 334, 84, 340, 90, 346, 84,
                       fill="white", width=2, tags="scene")                              # 뾰족한 이빨
    canvas.create_text(395, 125, text=message, fill="#ffcdd2",
                       font=(FONT, 13, "bold"), tags="scene")


def draw_whale():
    """오른쪽 위에 커다란 고래와 물살을 그린다."""
    clear_scene()
    canvas.create_oval(300, 25, 455, 110, fill="#3f51b5", outline="#1a237e", width=2, tags="scene")  # 몸통
    canvas.create_polygon(450, 68, 478, 38, 470, 68, 478, 98, fill="#3f51b5", tags="scene")          # 꼬리
    canvas.create_oval(325, 58, 335, 68, fill="white", tags="scene")                                  # 눈
    canvas.create_line(375, 25, 365, 5, fill="#b3e5fc", width=3, tags="scene")                        # 물 뿜기
    canvas.create_line(385, 25, 395, 5, fill="#b3e5fc", width=3, tags="scene")
    # 물살(물결 무늬) 3줄
    for y in (130, 145, 160):
        canvas.create_line(300, y, 320, y - 6, 340, y, 360, y - 6, 380, y,
                           fill="#b3e5fc", width=2, smooth=True, tags="scene")
    canvas.create_text(395, 185, text="🐋 고래 물살~!", fill="white", font=(FONT, 12, "bold"), tags="scene")


def draw_mom():
    """성공 장면: 꼬물이 오른쪽에 엄마 물고기와 하트를 그린다."""
    clear_scene()
    canvas.create_polygon(405, 125, 445, 92, 445, 158, fill="#f06292", tags="scene")      # 꼬리 (오른쪽)
    canvas.create_oval(300, 88, 415, 162, fill="#f48fb1", outline="#ad1457", width=2, tags="scene")  # 몸통
    canvas.create_oval(318, 110, 330, 122, fill="black", tags="scene")                    # 눈 (꼬물이를 바라봄)
    canvas.create_text(300, 70, text="♥  ♥", fill="#ff80ab", font=(FONT, 20, "bold"), tags="scene")
    canvas.create_text(358, 182, text="엄마", fill="white", font=(FONT, 11, "bold"), tags="scene")


def reset_place_buttons():
    """장소 버튼 8개를 처음 모습(아직 안 가 본 상태)으로 되돌린다."""
    # .items() : 딕셔너리에서 (이름, 값) 쌍을 하나씩 꺼낸다 → name="산호숲", icon="🪸" ...
    for name, icon in PLACES.items():
        place_buttons[name].config(text=f"{icon} {name}\n?", bg="#fff8e1", state="normal")
        # state="normal" : 누를 수 있는 상태 / state="disabled" : 회색으로 잠겨서 못 누르는 상태


def lock_places(locked):
    """장소 버튼을 잠그거나(locked=True) 풀어 준다(False). 이미 가 본 곳은 계속 잠가 둔다.
    이유: 상어 아저씨와 마주친 동안에는 다른 곳으로 못 가고 [숨기]에만 집중하게 하려고."""
    for name in PLACES:
        if locked or name in visited:   # or : 둘 중 하나라도 맞으면
            place_buttons[name].config(state="disabled")
        else:
            place_buttons[name].config(state="normal")


# ---------------------------------------------------------
# 3) 게임 규칙 함수들
# ---------------------------------------------------------
def lose_time(seconds):
    """남은 시간을 seconds초만큼 줄이고, 0이 되면 게임 오버.
    이유: 타이머·헤엄·잠·기지개·상어 모두 시간을 깎으므로 한 곳에서 처리해야 실수가 없다."""
    global time_left
    time_left = max(0, time_left - seconds)   # max(0, x) : x가 음수가 되면 0으로 (-3초 같은 이상한 표시 방지)
    update_screen()
    if time_left == 0 and playing:   # == 는 "같은가?" 비교 (= 하나는 값 넣기라서 다르다!)
        game_over()


def tick():
    """1초마다 실행되는 타이머. 시간을 1초 줄이고, 1초 뒤에 자기 자신을 다시 예약한다."""
    global timer_id
    if not playing:   # 게임이 끝났으면 더 이상 예약하지 않는다 → 타이머 멈춤
        return
    lose_time(1)
    if playing:
        # window.after(1000, tick) : "1000밀리초(=1초) 뒤에 tick을 한 번 실행해 줘"라는 예약.
        # 예약할 때 받은 번호표를 timer_id에 보관해 둔다 (나중에 취소하려고)
        timer_id = window.after(1000, tick)


def start_game():
    """[핵심 기능 1] 시작/다시 시작: 모든 상태를 처음 값으로 되돌리고 단서·손님을 새로 숨긴다."""
    # global : "함수 밖에 있는 변수를 이 함수 안에서 바꾸겠다"는 선언.
    #          이게 없으면 함수 안에서 바꾼 값이 함수가 끝나면 사라져 버린다.
    global clues, time_left, tired, playing, place_contents, visited, timer_id

    # 이전 판의 타이머가 아직 예약돼 있으면 취소한다.
    # 이유: 안 하면 [다시 시작]을 누를 때마다 타이머가 하나씩 늘어나 시간이 2배, 3배로 빨리 줄어드는 버그가 생긴다!
    if timer_id is not None:
        window.after_cancel(timer_id)
    stop_shark_event()   # 상어 소동 중에 다시 시작해도 깨끗하게 정리

    clues = 0
    time_left = START_TIME
    tired = 0
    playing = True
    visited = []

    # 내용물 8개를 섞은 뒤, 장소 8곳에 순서대로 하나씩 나눠 준다
    contents = PLACE_CONTENTS.copy()   # .copy() : 원본(설정값)은 그대로 두고 복사본을 만든다
    random.shuffle(contents)           # random.shuffle : 리스트 순서를 무작위로 섞는다 (카드 섞기)
    place_contents = {}
    for i, name in enumerate(PLACES):  # enumerate : 꺼낼 때마다 순서 번호(i = 0, 1, 2 ...)도 같이 준다
        place_contents[name] = contents[i]
    print("[테스트용] 이번 판 배치:", place_contents)   # 시험할 때 정답을 터미널에서 확인하려고 (화면엔 안 보임)

    reset_place_buttons()
    clear_scene()
    draw_fish(awake=True)
    update_screen()
    start_button.config(text="🔄 다시 시작")
    show_notice("꼬물이가 낮잠에서 깼어요! 그런데 엄마가 안 보여요... 8곳 중 단서 3개를 찾아보세요!", "info")

    timer_id = window.after(1000, tick)   # 1초 뒤부터 타이머 시작


def explore(name):
    """[핵심 기능 2] 장소 버튼을 누르면: 피로도 +2, 숨겨진 내용물 확인(단서·꽝·손님), 피곤하면 잠들기."""
    global clues, tired
    if not playing:   # 게임이 진행 중이 아니면
        show_notice("지금은 게임 중이 아니에요. [시작] 버튼을 눌러 주세요!", "bad")
        return        # return : 함수를 여기서 끝낸다 (아래 줄은 실행하지 않음)

    tired = tired + TIRED_PER_MOVE   # 아기라서 돌아다닐 때마다 피로도가 오른다
    cost = SWIM_COST                 # 이번 행동으로 잃을 시간
    button = place_buttons[name]     # 방금 누른 장소의 버튼을 꺼낸다
    content = place_contents[name]   # 이 장소에 숨겨진 내용물: "단서" / "꽝" / "상어" / "고래"
    visited.append(name)             # .append : 리스트 맨 뒤에 하나 추가 → "가 본 곳" 목록에 기록
    button.config(state="disabled")  # 이미 가 본 장소는 잠가서 같은 곳을 또 누르는 실수를 막는다

    # if / elif / else : "만약 ~이면 / 아니고 ~이면 / 그것도 아니면" 차례대로 검사해서 맞는 하나만 실행
    if content == "상어":
        # ── 돌발 상황: 예상하지 못한 손님 ① 상어 아저씨 → 3초 안에 [숨기]로 해결!
        button.config(text=f"🦈 {name}\n상어!", bg="#ef9a9a")    # 빨강 + "상어!" 글자
        lose_time(cost)
        if playing:   # 헤엄치다 시간이 다 돼서 게임 오버가 됐을 수도 있으니 확인
            start_shark_event()
        return        # 결과는 [숨기]를 눌렀는지에 따라 end_shark_event에서 정해진다
    elif content == "단서":
        clues = clues + 1
        message = f"[{name}] {CLUE_TEXTS[clues - 1]} ({clues}/{GOAL_CLUES})"
        kind = "good"
        button.config(text=f"🔍 {name}\n단서!", bg="#a5d6a7")    # 초록 + "단서!" 글자
    elif content == "고래":
        # ── 예상하지 못한 손님 ② 고래 (숨기 없이 물살 효과만)
        tired = tired + WHALE_TIRED
        message = f"[{name}] 🐋 앗! 거대한 고래가 지나가며 물살이 몰아쳐요! 휩쓸려서 피로도 +{WHALE_TIRED}!"
        kind = "bad"
        button.config(text=f"🐋 {name}\n고래!", bg="#90caf9")    # 파랑 + "고래!" 글자
        draw_whale()
        window.after(1500, hide_guest)   # 1.5초 뒤에 고래 그림 치우기
    else:   # 나머지 = "꽝"
        message = f"[{name}]에는 아무것도 없었어요..."
        kind = "info"
        button.config(text=f"✖ {name}\n꽝", bg="#b0bec5")        # 회색 + "꽝" 글자

    # 단서를 다 모았으면 바로 성공!
    if clues == GOAL_CLUES:
        update_screen()
        win()
        return

    show_notice(message, kind)
    lose_time(cost)                # 시간이 0이 되면 이 안에서 게임 오버 장면으로 바뀐다
    if playing:
        sleep_if_tired(message)    # 피로도가 다 찼으면 잠든다


def sleep_if_tired(message):
    """피로도가 최대치면 잠든다. 앞의 알림 글(message) 뒤에 잠든 사실을 덧붙여 보여 준다.
    이유: 장소 이동 뒤에도, 상어 소동이 끝난 뒤에도 똑같이 검사해야 해서 함수로 따로 뺐다."""
    global tired
    if tired < MAX_TIRED:   # 아직 견딜 만하면 아무것도 안 한다
        return
    tired = 0               # 푹 자고 일어나서 피로도는 0으로
    fall_asleep()
    show_notice(message + f"\n💤 너무 피곤해서 잠들어 버렸어요... {SLEEP_PENALTY}초가 지나갔어요!", "bad")
    lose_time(SLEEP_PENALTY)


def hide_guest():
    """고래 그림을 치운다. 단, 게임이 끝났거나(엄마·게임오버 장면) 상어 소동 중이면 지우지 않는다."""
    if playing and not shark_mode:
        clear_scene()


def fall_asleep():
    """꼬물이를 잠든 모습으로 그리고, 1.5초 뒤에 깨운다 (눈으로 '잠들었다'는 걸 보여 주려고)."""
    draw_fish(awake=False)
    window.after(1500, wake_up)   # 1500밀리초(1.5초) 뒤에 wake_up 실행 예약


def wake_up():
    if playing:   # 그 사이 게임이 끝났으면 깨우지 않는다
        draw_fish(awake=True)


def stretch():
    """기지개: 피로도 -1, 대신 시간 -2초."""
    global tired
    if not playing:
        show_notice("지금은 게임 중이 아니에요. [시작] 버튼을 눌러 주세요!", "bad")
        return
    if shark_mode:   # 상어 아저씨 앞에서 기지개는 안 된다!
        return
    if tired == 0:   # 안 피곤한데 기지개를 켜서 시간만 날리는 일을 막는다
        show_notice("꼬물이는 지금 하나도 안 피곤해요! 기지개는 아껴 두세요.", "info")
        return
    tired = tired - STRETCH_RECOVER
    show_notice(f"🙆 쭈욱~ 기지개! 피로도 -{STRETCH_RECOVER}, 대신 시간 -{STRETCH_COST}초", "info")
    lose_time(STRETCH_COST)


# ---------------------------------------------------------
# 4) 돌발 상황: 예상하지 못한 손님, 상어 아저씨!
# ---------------------------------------------------------
# [문제(재현)] 3단계에서는 상어를 만나면 피할 방법 없이 무조건 시간을 잃었다.
# [해결] 상어 아저씨를 마주치면
#   ① 장소 버튼을 잠그고 [숨기] 버튼만 켠다 → 무엇을 눌러야 할지 헷갈리지 않게
#   ② 남은 숨기 시간을 알림창(글자 + ●●●)과 버튼 글자 두 곳에 보여 준다 → 소리 없이도 급한 걸 알 수 있게
#   ③ 시간 안에 숨으면 손해 없음, 놓치면 도망치느라 3초 차감
def start_shark_event():
    """상어 아저씨 등장! 숨기 카운트다운을 시작한다."""
    global shark_mode, hide_left
    shark_mode = True
    hide_left = HIDE_SECONDS
    lock_places(True)                                  # 장소 버튼 전부 잠그기
    hide_button.config(state="normal", bg="#ffeb3b")   # [숨기] 버튼 켜기 (노란색으로 눈에 띄게)
    draw_shark("🦈 상어 아저씨다!")
    shark_countdown()


def shark_countdown():
    """1초마다 숨기 남은 시간을 1씩 줄인다. 0이 되면 숨기 실패."""
    global hide_left, shark_timer_id
    if not shark_mode or not playing:   # 그 사이 숨었거나 게임이 끝났으면 멈춘다
        return
    if hide_left == 0:
        end_shark_event(hidden=False)
        return
    show_notice(f"🦈 상어 아저씨를 마주쳤어요! 빨리 [🪨 숨기]를 눌러요!\n"
                f"남은 시간 {hide_left}초  {'●' * hide_left}", "bad")
    hide_button.config(text=f"🪨 숨기! ({hide_left}초)")
    hide_left = hide_left - 1
    shark_timer_id = window.after(1000, shark_countdown)   # 1초 뒤에 다시 실행 예약


def hide():
    """[숨기] 버튼을 눌렀을 때."""
    if shark_mode:
        end_shark_event(hidden=True)


def stop_shark_event():
    """상어 소동을 정리한다: 카운트다운 취소, [숨기] 버튼 끄기."""
    global shark_mode
    shark_mode = False
    if shark_timer_id is not None:
        window.after_cancel(shark_timer_id)
    hide_button.config(state="disabled", bg="#cfd8dc", text="🪨 숨기 (상어 아저씨를 만났을 때만)")


def end_shark_event(hidden):
    """상어 소동 끝. hidden이 True면 숨기 성공, False면 실패."""
    stop_shark_event()
    lock_places(False)   # 안 가 본 장소 버튼 다시 열기
    clear_scene()        # 상어 그림 치우기
    if hidden:
        message = "🪨 바위 뒤에 쏙! 상어 아저씨가 꼬물이를 못 보고 지나갔어요. 시간 손해 없음!"
        show_notice(message, "good")
    else:
        message = f"😱 너무 늦었어요! 상어 아저씨에게서 도망치느라 {SHARK_PENALTY}초를 잃었어요!"
        show_notice(message, "bad")
        lose_time(SHARK_PENALTY)
    if playing:
        sleep_if_tired(message)


# ---------------------------------------------------------
# 5) 성공 / 실패 판정
# ---------------------------------------------------------
def win():
    """[핵심 기능 3-1] 성공 판정: 단서 3개를 다 모으면 엄마가 나타난다."""
    global playing
    playing = False   # 게임 멈춤 → 타이머도 다음 tick에서 스스로 멈춘다
    draw_fish(awake=True)
    draw_mom()
    show_notice(f"🎉 단서 {GOAL_CLUES}개를 모두 모았어요! 엄마를 찾았어요! (남은 시간 {time_left}초)\n"
                "다시 하려면 [다시 시작]을 누르세요.", "good")


def game_over():
    """[핵심 기능 3-2] 실패 판정: 시간이 0이 되면 엄마 대신 상어 아저씨가 나타난다."""
    global playing
    playing = False
    stop_shark_event()   # 상어 소동 중에 시간이 다 됐을 수도 있으니 정리
    draw_fish(awake=True)
    draw_shark("으앙! 엄마~!")
    show_notice(f"⏰ 시간이 다 됐어요... 엄마를 못 찾은 꼬물이가 🦈 상어 아저씨를 마주쳤어요! 게임 오버!\n"
                f"(찾은 단서 {clues}/{GOAL_CLUES}) 다시 하려면 [다시 시작]을 누르세요.", "bad")


# ---------------------------------------------------------
# 6) 화면(창과 위젯) 만들기
# ---------------------------------------------------------
window = tk.Tk()                                   # 창 하나를 만든다
window.title("잠꾸러기 꼬물이의 엄마 찾기")         # 창 맨 위 제목
window.geometry("600x760")                         # 창 크기: 가로 600 x 세로 760 (픽셀)
window.configure(bg="#0b2e4f")                     # 창 배경색: 깊은 바다색

# 위쪽 상태 표시: 남은 시간, 단서
status_label = tk.Label(window, font=(FONT, 14, "bold"), bg="#0b2e4f", fg="white")
status_label.pack(pady=(15, 5))   # .pack() : 위젯을 위에서부터 차례로 쌓아 배치. pady = 위아래 여백

# 피로도 막대
tired_label = tk.Label(window, font=(FONT, 13), bg="#0b2e4f", fg="#ffe082")
tired_label.pack(pady=5)

# 바닷속 그림판
canvas = tk.Canvas(window, width=480, height=240, bg="#1e6fa8", highlightthickness=0)
canvas.pack(pady=10)

# 사건 알림창 (wraplength : 글이 이 너비를 넘으면 자동 줄바꿈)
notice_label = tk.Label(window, font=(FONT, 12), fg="#0b2e4f", wraplength=440,
                        width=52, height=4, justify="center")
notice_label.pack(pady=10)

# [숨기] 버튼: 평소에는 꺼져 있다가(disabled) 상어 아저씨를 만났을 때만 켜진다
hide_button = tk.Button(window, font=(FONT, 13, "bold"), width=30, command=hide)
hide_button.pack(pady=5)

# 장소 버튼 8개를 바둑판처럼(2줄 x 4칸) 놓기 위한 묶음 상자(Frame)
place_frame = tk.Frame(window, bg="#0b2e4f")
place_frame.pack(pady=5)

for i, name in enumerate(PLACES):
    # lambda : "이름 없는 짧은 함수". 버튼을 누를 때 explore(장소이름)을 부르려고 쓴다.
    # lambda n=name : "지금 이 순간의 name 값을 n에 따로 저장해 둬"라는 뜻.
    #   그냥 lambda: explore(name) 이라고 쓰면, 반복문이 끝난 뒤의 마지막 name("보물상자")만 기억해서
    #   8개 버튼이 전부 "보물상자"로 가 버리는 함정이 있다!
    button = tk.Button(place_frame, font=(FONT, 11), width=10, height=2,
                       command=lambda n=name: explore(n))
    # .grid(row=줄, column=칸) : 바둑판 배치. i // 4 → 0~3번은 0번 줄, 4~7번은 1번 줄
    #                                         i % 4  → 4로 나눈 나머지 = 몇 번째 칸인지 (0~3)
    button.grid(row=i // 4, column=i % 4, padx=5, pady=4)
    place_buttons[name] = button   # 나중에 글자·색을 바꾸려고 이름표를 붙여 보관

# 아래쪽 버튼 줄: 기지개 + 시작
bottom_frame = tk.Frame(window, bg="#0b2e4f")
bottom_frame.pack(pady=10)

tk.Button(bottom_frame, text=f"🙆 기지개 (피로 -{STRETCH_RECOVER}, 시간 -{STRETCH_COST}초)",
          font=(FONT, 12), bg="#b3e5fc", command=stretch).pack(side="left", padx=8)
# side="left" : 왼쪽부터 가로로 쌓기

start_button = tk.Button(bottom_frame, text="▶ 시작", font=(FONT, 13, "bold"), width=12,
                         bg="#ffca28", command=start_game)
start_button.pack(side="left", padx=8)


# ---------------------------------------------------------
# 7) 처음 화면 준비 후 실행
# ---------------------------------------------------------
draw_background()
draw_fish(awake=False)   # 처음에는 자고 있는 꼬물이
reset_place_buttons()
stop_shark_event()       # [숨기] 버튼을 꺼진 모습으로 준비
update_screen()
show_notice("쿨쿨... 꼬물이가 낮잠을 자고 있어요. [시작]을 눌러 깨워 주세요.", "info")

window.mainloop()   # 창을 계속 띄워 두고 버튼 클릭을 기다린다. 이 줄이 없으면 창이 바로 꺼진다.
