# 베이스 이미지 선택 (리눅스 OS + Python)
FROM python:3.9-slim

# 필요한 패키지 업데이트 & 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 라이브러리 설치
RUN pip install --upgrade pip
RUN pip install jupyterlab notebook pandas numpy matplotlib wordcloud requests beautifulsoup4 nltk

# Jupyter Notebook을 설치하고, Jupyter config 초기화
RUN jupyter notebook --generate-config

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 디렉토리 내 ipynb 파일을 /app 디렉토리에 복사
COPY W1M1.ipynb /app/
COPY W2M5.ipynb /app/
# 로컬 디렉토리 내 데이터 파일을 복사...
COPY mtcars.csv /app/
COPY korean_stopwords.txt /app/
COPY training.1600000.processed.noemoticon.csv /app/

# 컨테이너가 시작될 때, JupyterLab을 실행하도록 명령어 설정
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]