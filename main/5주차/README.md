## **등장한 개념들**

- 원 핫 인코딩
    - 범주형(Categorical) 데이터를 컴퓨터가 처리하기 쉬운 **이진 벡터(Binary Vector)**로 변환하는 기법
    - 이미지 처리, 자연어 처리 등에 쓰임

## **잘 정리된 표현**

> 딥러닝 모델은 본질적으로 입력 데이터 $x$를 타겟 값 $y$로 매핑하는 함수 $f(x)$를 찾는 과정입니다. 레이어를 쌓는다는 것은 함수를 합성($f_3(f_2(f_1(x)))$)하는 행위입니다.

## **손실함수와 경사하강법**

손실함수: 피드백을 주기 위해 도출한 오차
경사하강법: 가중치를 기반으로 내리막길을 찾아가는 점진적 업데이트

```python
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",   # one-hot이면 categorical_crossentropy
    metrics=["accuracy"]
)
```

- `model.compile`은 학습할 때 이 손실함수를 기준으로 삼겠다는 선언