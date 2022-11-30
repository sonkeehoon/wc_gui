import os, sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as msgbox
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

today = datetime.today().strftime("%Y.%m.%d")
start = today.split('.')
start[0] = str(int(start[0])-3)
start = '.'.join(start)
print(f"today is {today}, start is {start}")

def browse_dest_path():
    folder_selected=filedialog.askdirectory()
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
    cand_mask=np.array(Image.open(resource_path('circle.jpg')))
    # 뉴스 검색 결과 크롤링
    url=f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=\
    {words}\
    &sort=1&photo=0&field=0&pd=3&ds={start}&de={today}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:dd,p:from20190516to20220516,a:all&start=00"
    str_n=""
    for i in range(5):
        url=url[:-2]+str(i)+"1"
        res=requests.get(url)
        res.raise_for_status()
        soup=BeautifulSoup(res.text,"lxml")

        l1=soup.find_all("a",attrs={"class":"news_tit"})
        l2=soup.find_all("a",attrs={"class":"api_txt_lines dsc_txt_wrap"})
        l3=l1+l2
        for l in l3:
            str_n=str_n+l.get_text()
    # print("str is",str_n)
            
    # freq = list(zip(*freq))
    # table = pd.DataFrame({"word":freq[0],"frequency":freq[1]})
    # print(table[:20])
    wordcloud = WordCloud(
        font_path = 'malgun.ttf',
        background_color = 'white',
        colormap = 'Greens',
        mask = cand_mask
    ).generate(str_n)
    plt.figure(figsize=(5,5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    file_name = words + ".jpg"
    dest_path = os.path.join(txt_dest_path.get(),file_name)
    plt.savefig(dest_path)

def btnClick():
    if len(txt_dest_path.get())==0:
        msgbox.showwarning("경고","저장 경로를 선택하세요")
        return
    try:
        words = text.get()
        makeWC(words)
        msgbox.showinfo("생성 완료", "워드 클라우드가 생성 되었습니다\n'이미지 저장' 버튼을 누르세요")
        
    except Exception as err:
        msgbox.showerror("error",err)
    
win=tk.Tk()
win.title("WordCloud")
win.geometry('300x300')

# 제목
label=tk.Label(win, text="워드 클라우드 만들기")
label.pack(pady=5)

# 검색어 입력 후 wc만들기
frame=tk.LabelFrame(win,text="검색어 입력")
frame.pack(fill="x", padx=5, pady=5)

text=tk.Entry(frame)
text.pack(side="left",fill="x",expand=True,padx=5,pady=5,ipady=4)

btn=tk.Button(frame, text="만들기", width=5, command=btnClick)
btn.pack(side="left", padx=5, pady=5)

# 저장경로 지정
path_frame=tk.LabelFrame(win,text="저장경로")
path_frame.pack(fill="x",padx=5,pady=5,ipady=5)

txt_dest_path=tk.Entry(path_frame)
txt_dest_path.pack(side="left",fill="x",expand=True,padx=5,pady=5,ipady=4) # 높이 변경

btn_dest_path=tk.Button(path_frame,text="찾아보기",width=10,command=browse_dest_path)
btn_dest_path.pack(side="right",padx=5,pady=5)

win.protocol('WM_DELETE_WINDOW', exit_window_x)


win.mainloop()
