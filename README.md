# 감정 분석 기반 AI 책 추천 시스템

### 1. 프로젝트 개요

+ 프로젝트 주제 및 선정 배경
  + 사용자 감정에 따른 책 추천시스템 부재
  + 읽고싶은 책 선정의 불편함을 해결하고자 감정분석 기반 AI 책 추천 시스템 개발
  
+ 사용데이터
  + 알라딘의 책 100자 리뷰 및 키워드 데이터, BERT 사전훈련모델을 사용하여 알고리즘 개발

+ 활용 라이브러리 및 사전데이터 확보 기술
  + Colab
  + python - Crawling, Scraping
  + tensorflow, scikit-learn
  + server - Flask
  + DB - postgreSQL

### 2. 데이터 및 모델

+ 감정분석 데이터
  + 한국어 단발성 대화 데이터셋
+ 훈련데이터 수
  + 감정 데이터셋 : 38,594
+ 테스트데이터 수
  + 책 데이터 : 3,090
  + 리뷰 데이터 : 17,256

+ 데이터셋
  + isbn : 책 고유의 번호(key)
  + item_id : 알라딘에서의 책 id
  + category
  + title
  + author
  + publisher
  + p_date : 출판일
  + price
  + page
  + avg_score : 책 평점
  + description

+ 사용 모델
  + SentenceTransformer : sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens(SBERT)

### 3. 프로젝트 진행 및 결과

+ 키워드 추출
  + 데이터셋 전처리 진행
  + 입력받은 문장의 태깅 작업 후 n-gram을 통해 1개의 단어로 구성된 keyword 5개 추출
  + 입력받은 문장과 사전학습된 BERT모델(SBERT)에서 학습된 단어들의 임베딩 벡터 빈도와 Cosine-Similarity를 통해 5개의 키워드 반환

+ 모델 학습 및 labeling
  + BERT 모형에 한국어 단발성 대화 데이터셋 Fine-Tunning
  + 크롤링 데이터 Category에 맞춰 Labeling 진행
  + 감정분석에 Labeling 하여 Category 분류

+ 추천 알고리즘
  + 장르 유사도, 작가 유사도 : 전처리 후 같으면 1, 다르면 0
  + 키워드 유사도 : 5개의 임베딩 벡터를 mean pooling 후 코사인 유사도 계산
  + 감정 유사도 : 사용자가 선택한것과 같은 감정 1, 아니면 0
  + 평균 평점 :  0-10 사이의 평점을 MinMaxScaler를 이용하여 0-1 사이로 반환

+ 문제점
1. 사용자 감정을 책 평가들을 통해 분석하기 때문에 만약 책평가가 존재하지 않는다면 더미데이터가 됨.
2. 신규책의 경우도 추천 불가.

### 4. 한계점 및 해결방안
1.유저의 데이터가 존재하지 않아 기존의 유저가 읽고 느꼈던 책의 리뷰나 데이터들이 없어 해당 프로젝트는 직접 사용자에게 책을 읽었는지 물어보고 웹에서 선택하여야지 결과가 반환되도록 개발이 됨.

2. 유저의 데이터 정보가 존재한다면 사용자의 로그데이터를 활용한 추천 시스템이 가능.

3. 책의 줄거리를 이용하여 키워드 유사도로 대체하여 계산하였지만, 만약 책의 내용데이터를 가지고 있는 곳이라면 책 내용을 통해 스토리의 유사성으로 책을 추천해준다면 더 좋은 결과물을 얻지 않을까 생각함. 

-> 이러한 생각을 하게 된 기사 : http://www.aitimes.com/news/articleView.html?idxno=140791
