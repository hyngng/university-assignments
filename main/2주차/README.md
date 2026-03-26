- 더 작성 예정중

## 공통

- 기본적으로 둘 다 seen 데이터를 통해 unseen 데이터의 추세를 예측하는 것
- `classification`, `regression`의 차이는 이산적이냐, 연속적이냐임
- 에 대해서도 설명함.
- train/test를 나누는 것은 모델의 일반화<sup>generalization</sup>를 위해서.
    - 일반화란 일관성을 달성하는 것.
    - seen data와 unseen data. 레이더 밖 영역의 데이터에 대한 예측을 위해 '모델의 일반화'를 잘 하기 위함에 핵심이 있음.
    - 파라미터를 늘리고, 훈련 데이터를 늘리고, 이런 것은 모두 마찬가지.
    - 보통 train : test = 8 : 2 정도로 나눈다고 함.
- 평가방법은, 회귀는 mse, 분류는 정확도<sup>accuracy</sup>임.
    - 여기까지가 최소기준치.

## classification

- 분류<sup>classification</sup>란 데이터 영역 범주화를 통해 미래 데이터의 성격을 예측하는 것.

## regression

- 회귀<sup>regression</sup>란 ax + b 형태로 추세를 예측하는 것이며, 좀 더 추상도를 낮춰 설명하면, 곧 기울기와 절편을 확인하는 것.

---

## 과제 검토 관련 지적

- `path = '../../data/diabetes.csv'
    -[x] 여러 번 로드하지 않아도 된다.
    -[x] `../../`로도 잘 동작하냐.