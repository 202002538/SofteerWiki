# 학습 목표
##### 웹사이트에서 데이터를 가져와서 요구사항에 맞게 가공하는 ETL 파이프라인을 만듭니다.
##### - Web Scraping에 대한 이해
##### - Pandas DataFrame에 대한 이해
##### - ETL Process에 대한 이해
##### - Database & SQL 기초

# 사전지식
##### 시나리오
##### 당신은 해외로 사업을 확장하고자 하는 기업에서 Data Engineer로 일하고 있습니다. 경영진에서 GDP가 높은 국가들을 대상으로 사업성을 평가하려고 합니다.
##### 이 자료는 앞으로 경영진에서 지속적으로 요구할 것으로 생각되기 때문에 자동화된 스크립트를 만들어야 합니다.


# 라이브러리 사용
##### web scaping은 BeautifulSoup4 라이브러리를 사용하세요.
##### 데이터 처리를 위해서 pandas 라이브러리를 사용하세요.
##### 로그 기록 시에 datetime 라이브러리를 사용하세요.
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import requests
import re

# ETL 프로세스 기록용 로그파일 생성
def create_logfile():
    # 시간 기록 - 'Year-Monthname-Day-Hour-Minute-Second'
    try:
        log_file = open('missions/W1/M3/etl_project_log.txt', 'x') #파일 없으면 생성, 있으면 에러 발생
        print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "로그 파일 생성", file=log_file)
        return log_file
    except:
        log_file = open('missions/W1/M3/etl_project_log.txt', 'a') #파일 있으면 이어쓰기
        return log_file

#----------------------------------------------------------------
# Extract
### 국가별 GDP 추출 함수
def get_gdp_by_country():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"

    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "웹에서 HTTP응답 받음", file=log_file)
    else:
        print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "웹에서 HTTP응답 받지 못함. 응답 코드: {0}".format(response.status_code), file=log_file)
        print(response.status_code)

    response = requests.get(url).text #응답 성공 시 html 텍스트(문자열 형태) 가져롬
    soup = BeautifulSoup(response, "html.parser") #파싱된 soup객체로 변환

    table = soup.select_one('table.wikitable') #선택자로 table찾기
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all(['th', 'td']) #헤더와 데이터 모두 가져오기
        cols = [col.text.strip() for col in cols][:3] #텍스트만 추출하여 리스트로 변환
        data.append(cols[:3])
        
    df = pd.DataFrame(data[3:], columns=['Country', 'GDP_USD_billion', 'year'])
    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "(Extract) raw gdp 데이터 추출", file=log_file)

    return df

### 국가별 Region 추출 함수
def get_region_by_country(df):
    # Country와 Region이 mapping된 csv파일 
    # 출처 - https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes
    # 한계점 - 다른 이름 표기법을 사용하거나 데이터 부족으로 맵핑되지 않은 나라가 있을 수 있다.
    region_data = pd.read_csv("missions/W1/M3/region.csv") 
    region_data = region_data.rename(columns={'name':'Country'})
    df = pd.merge(df, region_data[['Country', 'region']], how='left', on='Country') #국가별 GDP 데이터프레임에 나라에 맞는 region맵핑

    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "(Extract) raw region 데이터 추출", file=log_file)
    return df

### 추출한 raw데이터 json파일로 저장
def save_rawfile():
    json_file_path = "missions/W1/M3/Countries_by_GDP.json"
    df.to_json(json_file_path, orient='records', force_ascii=False)

    print(f"Data has been saved to {json_file_path}")
    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "raw 데이터 로드", file=log_file)

#----------------------------------------------------------------
# Transform

# '-' 처리 함수
def remove_bar(df):
    for i in range(len(df)):
        if df.loc[i]['GDP_USD_billion'] == '—': # GDP가 '-'라면 GDP와 year은 None으로 처리
            df.loc[i, 'GDP_USD_billion'] = None
            df.loc[i, 'year'] = None
    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "(Tansform) 데이터 결측치 처리", file=log_file)
    return df

#위키피디아 주석 제거 함수
def remove_wiki_annotations(df):
    def remove(text):
        if pd.isna(text):
            return text
        return re.sub(r'\[.*?\]', '', text).strip()  # [...] 형태의 주석 제거
    df = df.applymap(remove)
    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "(Tansform) 불필요한 주석 제거", file=log_file)       
    return df

#단위 변경 함수(million -> billion)
def million_to_billion(gdp):
    def remove(gdp):
        try:
            gdp = gdp.replace(',', '')
            gdp = round(int(gdp) / 1000, 2) #소수점 2자리까지
            return gdp 
        except Exception:
            return gdp
    df['GDP_USD_billion'] = df['GDP_USD_billion'].apply(remove)
    print(datetime.datetime.now().strftime('%Y-%B-%d-%H-%M-%S,'), "(Tansform) 데이터 단위 변경", file=log_file)       
    return df

#---------------------------------------------------------------
#메인
if __name__ == '__main__':
    log_file = create_logfile()
    df = get_gdp_by_country()
    df = get_region_by_country(df) #E
    save_rawfile()
    df = remove_bar(df)
    df = remove_wiki_annotations(df)
    df = million_to_billion(df) #T

    log_file.close()

#----------------------------------------------------------------
# 화면 출력
##### GDP가 100B USD이상이 되는 국가만을 구해서 화면에 출력해야 합니다.
print(df[df['GDP_USD_billion'] >= 100])

##### 각 Region별로 top5 국가의 GDP 평균을 구해서 화면에 출력해야 합니다.
region_top5 = df.sort_values(by=['GDP_USD_billion'], ascending=False).groupby('region').head(5)
print(region_top5.groupby('region')['GDP_USD_billion'].mean())