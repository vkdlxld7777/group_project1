import chromedriver_autoinstaller as AutoChrome
import os
import shutil

def chromedriver_update():
    chrome_ver      = AutoChrome.get_chrome_version().split('.')[0]
    print('제일 최신 크롬버전 : ',chrome_ver)

    current_list    = os.listdir(os.getcwd())
    print('현재 경로의 모든 객체들 : ',current_list)

     # 최신버전 폴더가 현재 경로에 없으면
    if not chrome_ver in current_list:
        print("크롬드라이버 다운로드 실행")
        AutoChrome.install(True)
        print("크롬드라이버 다운로드 완료")
    else: print("크롬드라이버 버전이 최신입니다.")
    
    chrome_list = []
    for i in current_list:
        path = os.path.join(os.getcwd(), i)
        print('현재 경로의 모든객체의 전체경로 : ',path)
        
        # 경로가 폴더일 경우
        if os.path.isdir(path):
            # 폴더면 안에 크롬드라이버가가 있는지 확인
            if 'chromedriver.exe' in os.listdir(path):
                # 있는경우 chrome_list에 추가
                chrome_list.append(i)
    #그중에 최신버전은 제외
    old_version = list(set(chrome_list)-set([chrome_ver]))
    print('오래된 버젼 리스트 : ',old_version)

    for i in old_version:
        path = os.path.join(os.getcwd(),i)
        print('구버전이 있는 폴더의 경로 : ',path)
        
        # 그 경로 삭제
        shutil.rmtree(path)
    
    return os.getcwd()+'\\'+chrome_ver+'\\chromedriver.exe'