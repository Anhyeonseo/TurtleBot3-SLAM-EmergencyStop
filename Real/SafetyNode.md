## 1. 패키지 구조

```
~/setros_ws/src/setros_safety
├── launch
│   └── setros_nav2_safety.launch.py
├── package.xml
├── setup.py
└── setros_safety
    ├── __init__.py
    └── safety_cmd_vel_node.py
```

---

## 2. Safety Node

경로:

```
~/setros_ws/src/setros_safety/setros_safety/safety_cmd_vel_node.py
```

역할:

```
Nav2의 /cmd_vel_nav를 받아 최종 /cmd_vel로 전달한다.
단, LiDAR /scan 기준으로 전방 갑툭튀 장애물이 감지되면 /cmd_vel을 0으로 차단한다.
```


확인 결과:

```
distance=0.292 m | raw_angle=358.0 deg | normalized_angle=-2.0 deg
distance=0.293 m | raw_angle=0.0 deg | normalized_angle=0.0 deg
distance=0.293 m | raw_angle=1.0 deg | normalized_angle=1.0 deg
```

해석:

```
로봇 정면 장애물이 0도 근처에서 정상 감지됨.
따라서 전방 기준은 0도가 맞고, safety_node 문제는 /scan QoS 문제였음.
```

---

## 7. 최종 코드 구조 요약

```
Nav2 controller_server
        ↓
/cmd_vel_nav
        ↓
setros_safety_node
        ↓
/cmd_vel
        ↓
turtlebot3_node
        ↓
모터 제어
```

```
LiDAR /scan
        ↓
setros_safety_node
        ↓
전방 ±25도, 0.28m 이내 장애물 판단
        ↓
정상: /cmd_vel_nav 그대로 전달
위험: /cmd_vel = 0으로 차단
```

## 8. 최종 구현 요약

```
1. safety_cmd_vel_node.py
   - /cmd_vel_nav 구독
   - /scan 구독
   - 갑툭튀 장애물 감지
   - 위험 시 /cmd_vel 0 출력
   - /safety_state 상태 출력

2. setros_nav2_safety.launch.py
   - Nav2 실행
   - 저장된 지도 setros_map_new.yaml 적용
   - 튜닝 파라미터 setros_nav2_params.yaml 적용
   - safety node 자동 실행

3. setup.py 수정
   - safety_cmd_vel_node 실행 등록
   - launch 파일 설치 등록
```



---

