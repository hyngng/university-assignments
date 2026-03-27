## **수업 중 메모**

> `titanic.csv`는 feature 선별 및 관련없는 노이즈 데이터 제거의 필요성과 관련된 실습이었음.

- 일부로 기존의 방식대로 동작하지 않는 데이터를 줬다고 함.
    - 데이터가 `float`이 아닌 `int`인 경우.
    - 데이터가 누락되어 `NaN`으로 인식되는 경우.
- test 데이터는 문자열도 상관없으나, train 데이터는 `float` 자료형만 됨.
- 정확히는 feature가 숫자여야 함. 숫자가 아니면 바꿔줘야 한다고.
    - `LabelEncoder`를 이용한다고 함.
    - 다음과 같이 사용함  
        ```python
        import pandas as pd
        from sklearn.preprocessing import LabelEncoder

        le=LabelEncoder()
        df['Name_encoded'] =le.fit_transform(df['Name'])
        ```

- 결측치 체크: `df.isnull().sum()`
- 결측치 행 제거: `df_clean = df.dropna()`
- `titanic.csv` 행 개수는 900개가 조금 안 되는데, 교수님 말씀으로는 10만개 이상은 있어야 한다고 함.
    - `age` 열중 결측치 있는 행이 177개인데 177/900은 굉장히 큼. => 다소 부정확할 수 있더라도 Age의 평균값으로 대신 복붙해서 처리하는 것이 177개 데이터를 모두 날리는 것보다 합리적임.

- `ML_classification_breast_cancar.ipynb`에 모든 과정이 있음.