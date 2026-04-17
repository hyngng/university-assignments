`car_evalutation_pytorch`에 기반해 `wine_evaluation_pytorch`를 만들 때의 수정사항

## **Gemini 3.1 Pro**

```md
방금 수정한 부분들은 `car_evaluation` 데이터에 맞춰져 있던 코드를 `wine` 데이터의 특성(입력 피처 13개, 결과 클래스 3개, 타겟 컬럼명 'Wine')에 맞게 변경한 것입니다. 

총 7개의 셀을 수정했으며, 주요 변경 내역은 다음과 같습니다.

**1. 파이 차트 시각화 셀**
*   수정 전: `data.output.value_counts().plot(..., colors=[4개], explode=(4개))`
*   수정 후: `data['Wine'].value_counts().plot(..., colors=['lightblue', 'lightgreen', 'orange'], explode=(0.05, 0.05, 0.05))` (클래스가 3개이므로 3개로 축소)

**2. LabelEncoder 적용 대상 셀**
*   수정 전: `columns = ['price', 'maint', 'doors', 'persons', 'lug_capacity', 'safety','output']`
*   수정 후: `columns = ['Wine']` (Wine 데이터는 피처들이 이미 수치형이므로, 1/2/3으로 되어 있는 타겟 레이블만 0/1/2로 변환하도록 설정)

**3. 데이터와 타겟 분리 셀 (2곳)**
*   수정 전: `X = data.drop('output', axis=1).values`, `y = data['output'].values`
*   수정 후: `X = data.drop('Wine', axis=1).values`, `y = data['Wine'].values`

**4. Dense 모델 정의 셀**
*   `self.fc1 = nn.Linear(6, 64)` $\rightarrow$ `nn.Linear(13, 64)` (입력 피처 13개)
*   `self.fc3 = nn.Linear(32, 4)` $\rightarrow$ `nn.Linear(32, 3)` (출력 클래스 3개)

**5. 1D CNN 모델 정의 셀**
*   `self.conv1 = nn.Conv1d(6, 16, kernel_size=3, padding=1)` $\rightarrow$ `nn.Conv1d(13, 16, ...)`
*   `self.fc2 = nn.Linear(64, 4)` $\rightarrow$ `nn.Linear(64, 3)`

**6. 모델 Summary 모델 확인 셀**
*   수정 전: `summary(model, input_size=(6, 5))`
*   수정 후: `summary(model, input_size=(13, 5))`
```