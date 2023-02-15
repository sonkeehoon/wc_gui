import os, sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as msgbox
import tkinter.ttk as ttk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.request
import urllib.parse
from konlpy.tag import Okt
from collections import Counter


def update_progress_bar(state):
    p_var.set(state)
    progress_bar.update()
    
def naver_view_scrap(words):
    str_n = ""
    # 시작년도와 끝 년도를 계산(start, today)
    today = datetime.today().strftime("%Y.%m.%d")
    start = today.split('.')
    today = today.split('.')
    year = 3 # 몇년치 결과를 검색할지
    start[0] = str(int(start[0]) - year)
    start = ''.join(start)
    today = ''.join(today)
    
    # 입력한 단어(words) 검색 결과를 스크래핑
    word = urllib.parse.quote_plus(words)
    url = f'''https://search.naver.com/search.naver?where=view&sm=tab_viw.blog&query={word}&nso=so%3Ar%2Cp%3Afrom{start}to{today}'''
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html,'html.parser')
    title = soup.find_all(class_ = "api_txt_lines total_tit")
    content = soup.find_all(class_ = "api_txt_lines dsc_txt")
    # 스크래핑 해온 텍스트를 str_n 변수에 저장
    for t in title:
        str_n += t.get_text()
    for c in content:
        str_n += c.get_text()
        
    return str_n

def naver_news_scrap(words):
    today = datetime.today().strftime("%Y.%m.%d")
    start = today.split('.')
    year = 3
    start[0] = str(int(start[0]) - year)
    start = '.'.join(start)
    url = f"""https://search.naver.com/search.naver?where=news&sm=tab_pge&query={words}
    &sort=1&photo=0&field=0&pd=3&ds={start}&de={today}&mynews=0&office_type=0&office_section_code=0
    &news_office_checked=&nso=so:dd,p:from20190516to20220516,a:all&start=00"""
    str_n = ""
    for i in range(5):
        url = url[:-2] + str(i) + "1"
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text,"lxml")

        l1 = soup.find_all("a",attrs={"class":"news_tit"})
        l2 = soup.find_all("a",attrs={"class":"api_txt_lines dsc_txt_wrap"})
        l3 = l1 + l2
        for l in l3:
            str_n = str_n + l.get_text()
            
    return str_n

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를때
        print("폴더 선택 취소")
        return
    # print(folder_selected)
    txt_dest_path.delete(0,tk.END)
    txt_dest_path.insert(0,folder_selected)

def exit_window_x(): # x버튼을 눌러도 종료되지 않던 버그를 수정하기 위한 함수
    print("프로그램을 종료합니다.")
    win.quit() 

def makeWC(words):
    cand_mask = np.array(Image.open(resource_path('./circle.jpg'))) # 동그란 워드클라우드를 만들기 위한 판
    txt = ""
    now_state = 0
    # 뉴스 검색 결과 크롤링
    txt += naver_news_scrap(words)
    now_state += 33
    update_progress_bar(now_state)

    txt += naver_view_scrap(words)
    now_state += 34
    update_progress_bar(now_state)
    
    
    nlpy = Okt()
    nouns = nlpy.nouns(txt)
    count = Counter(nouns)
    tag_count = []
    tags = []

    for n, c in count.most_common(50):
        
        dics = {'tag': n, 'count': c}

        if len(dics['tag']) >= 2 and len(tags) <= 49:

            tag_count.append(dics)

            tags.append(dics['tag'])
            
            
            
    freq_file_name = words + "_frequency.txt"
    freq_dest_path = os.path.join(txt_dest_path.get(),freq_file_name)
    f = open(freq_dest_path,"w",encoding="utf-8")

    for tag in tag_count:
        
        s = f" {tag['tag']:<14}"
        f.write(str(s)+'\t'+str(tag['count'])+'\n')
    
    
            
    wordcloud = WordCloud(
        font_path = 'malgun.ttf',
        background_color = 'white',
        mask = cand_mask
    ).generate(txt)
    
    plt.figure(figsize = (10,8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    file_name = words + ".jpg"
    dest_path = os.path.join(txt_dest_path.get(),file_name)
    plt.savefig(dest_path)
    now_state += 33
    update_progress_bar(now_state)

def btnClick():
    if len(text.get()) == 0:
        msgbox.showwarning("경고", "검색어를 입력하세요")
        return
    elif len(txt_dest_path.get()) == 0:
        msgbox.showwarning("경고", "저장 경로를 선택하세요")
        return
        
    try:
        words = text.get()
        makeWC(words)
        msgbox.showinfo("생성 완료", "워드 클라우드 생성과 빈도수 분석이 완료되었습니다\n저장 경로를 확인하세요")
        
    except Exception as err:
        msgbox.showerror("error",err)
    
win = tk.Tk()
win.title("WordCloud")
win.geometry('300x300')

# 제목
label = tk.Label(win, text="워드 클라우드 만들기")
label.pack(pady = 5)

# 검색어 입력 프레임
frame = tk.LabelFrame(win,text="검색어 입력")
frame.pack(fill = "x", padx = 5, pady = 5)

text = tk.Entry(frame)
text.pack(side = "left", fill = "x", expand = True, padx = 5, pady = 5, ipady = 4)

btn = tk.Button(frame, text = "만들기", width = 5, command = btnClick)
btn.pack(side = "left", padx = 5, pady = 5)

# 저장경로 지정
path_frame = tk.LabelFrame(win, text = "저장경로")
path_frame.pack(fill = "x", padx = 5, pady = 5, ipady = 5)

txt_dest_path = tk.Entry(path_frame)
txt_dest_path.pack(side = "left", fill = "x", expand = True, padx = 5, pady = 5, ipady = 4) # 높이 변경

btn_dest_path = tk.Button(path_frame, text = "찾아보기", width = 10, command = browse_dest_path)
btn_dest_path.pack(side = "right", padx = 5, pady = 5)

# 진행상황
frame_progress=tk.LabelFrame(win, text = "진행상황")
frame_progress.pack(fill="x", padx = 5, pady = 5, ipady = 5)

p_var=tk.DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum = 100, variable = p_var)
progress_bar.pack(fill = "x", padx = 5, pady = 5)

win.protocol('WM_DELETE_WINDOW', exit_window_x)
win.mainloop()
