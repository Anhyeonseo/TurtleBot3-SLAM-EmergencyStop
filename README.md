# SetROS TurtleBot3 Autonomous Driving Project

## 프로젝트 소개

SetROS 프로젝트는 ROS2 기반 TurtleBot3 Burger를 활용하여 실물 환경에서 자율주행 시스템을 구현한 프로젝트입니다.

LiDAR 센서를 이용해 실내 환경을 SLAM으로 매핑하고, 저장된 지도를 기반으로 Navigation2를 실행하여 목표 지점까지 자율주행을 수행했습니다. 또한 주행 중 맵에 없는 정적 장애물을 실시간으로 회피하고, 전방에 갑작스럽게 등장하는 장애물에 대해서는 Emergency Stop 기능을 적용하여 로봇을 즉시 정지시키는 안전 제어 구조를 구현했습니다.

## 개발 환경

| 구분 | 내용 |
|---|---|
| OS | Ubuntu 24.04 |
| ROS | ROS2 Jazzy |
| Robot | TurtleBot3 Burger |
| Control Board | OpenCR |
| Sensor | LDS-01 LiDAR |
| SLAM | Cartographer |
| Navigation | Navigation2 |
| Language | Python |

## 시스템 구조

본 프로젝트는 ROS2 Navigation2와 직접 구현한 setros_safety 패키지를 결합한 구조입니다.

기본적인 자율주행은 Nav2가 담당하고, 긴급 정지 상황은 Safety Node가 최종 속도 명령을 제어하는 방식으로 처리했습니다.

전체 데이터 흐름은 다음과 같습니다.

LiDAR /scan  
→ SLAM / Localization  
→ Nav2 Path Planning  
→ Nav2 Controller  
→ setros_safety_node  
→ TurtleBot3 Motor Control  

Nav2는 목적지까지의 경로를 생성하고 주행 명령을 출력합니다. 이후 Safety Node가 LiDAR 데이터를 기반으로 전방 장애물 여부를 판단한 뒤, 정상 상황에서는 Nav2 명령을 그대로 전달하고 위험 상황에서는 속도 명령을 차단합니다.

## 주요 기능

### SLAM 및 지도 생성

Cartographer를 사용하여 실물 주행 환경의 지도를 생성했습니다.

TurtleBot3를 수동으로 조작하며 LiDAR 데이터를 수집했고, 외곽 벽면과 주행 공간이 반영된 지도를 저장했습니다.

### Nav2 기반 자율주행

저장된 지도를 기반으로 AMCL Localization을 수행하고, Navigation2를 통해 목표 지점까지 자율주행을 구현했습니다.

RViz2에서 Goal을 지정하면 로봇이 현재 위치를 추정하고, 목적지까지의 경로를 생성한 뒤 주행합니다.

### 정적 장애물 회피

주행 경로상에 맵에 없는 장애물을 배치하여 실시간 회피 성능을 검증했습니다.

LiDAR로 감지된 장애물은 Local Costmap에 반영되고, Nav2 Controller가 충돌 없는 경로를 다시 선택하여 우회 주행합니다.

### Emergency Stop

자율주행 중 로봇 전방에 갑자기 등장하는 장애물을 감지하면 Safety Node가 최종 속도 명령을 차단합니다.

전방 ±25도 영역에서 0.28m 이내 장애물이 감지되면 로봇은 즉시 정지하고, 장애물이 제거되면 1초간 대기한 뒤 기존 경로를 따라 자율주행을 재개합니다.

상태 흐름은 다음과 같습니다.

NORMAL  
→ SUDDEN_OBSTACLE_STOP  
→ WAIT_AFTER_SUDDEN_STOP  
→ NORMAL  

## 프로젝트 진행 과정

1. TurtleBot3 기본 세팅
2. Gazebo 환경에서 SLAM 및 Nav2 사전 테스트
3. 실물 주행 환경 설계
4. TurtleBot3 실물 하드웨어 Bringup
5. Cartographer 기반 실물 SLAM 수행
6. 지도 저장 및 AMCL Localization
7. Nav2 기반 자율주행 테스트
8. 맵에 없는 정적 장애물 회피 테스트
9. Emergency Stop 테스트
10. 장애물 제거 후 주행 복귀 검증

## 트러블슈팅

### Nav2 Lifecycle 활성화 문제

RViz2에서 Goal을 지정했을 때 navigate_to_pose action server가 활성화되지 않는 문제가 발생했습니다.

Nav2 주요 노드의 lifecycle 상태를 확인하고, 필요한 노드를 활성화하여 action server가 정상적으로 동작하도록 해결했습니다.

### cmd_vel 제어 명령 연결 문제

Nav2는 cmd_vel_nav로 속도 명령을 생성했지만, 실제 TurtleBot3가 구독하는 cmd_vel로 명령이 전달되지 않아 로봇이 움직이지 않는 문제가 있었습니다.

이를 해결하기 위해 cmd_vel_nav와 cmd_vel 사이에 Safety Node를 삽입하여 최종 속도 명령을 제어하도록 구조를 개선했습니다.

### Costmap 및 주행 파라미터 튜닝

좁은 실물 주행 환경에서 로봇이 안정적으로 움직이도록 속도, 가속도, inflation radius 등을 조정했습니다.

이를 통해 급가속을 줄이고 장애물 회피 안정성을 높였습니다.

## 최종 결과

| 기능 | 결과 |
|---|---|
| 실물 환경 SLAM | 성공 |
| 지도 저장 | 성공 |
| AMCL Localization | 성공 |
| Nav2 자율주행 | 성공 |
| 맵에 없는 정적 장애물 회피 | 성공 |
| Emergency Stop | 성공 |
| 장애물 제거 후 주행 재개 | 성공 |

## Demo Video

### SLAM & Navigation

실물 환경에서 SLAM을 수행하고, 저장된 지도를 기반으로 자율주행하는 과정입니다.

Link: [Demo Video](https://drive.google.com/file/d/1xn91RC35yV6Mh0GOAZe12CxJn1X1upzC/view)

### Static Obstacle Avoidance

맵에 없는 장애물을 Local Costmap에 반영하고, 로봇이 실시간으로 우회 주행하는 과정입니다.

Link: [Demo Video](https://drive.google.com/file/d/1nY7ErL9Y-BqyfT8hbNzv7Bwl8ZVAxig5/view)

### Emergency Stop

전방 근거리 장애물 감지 시 로봇이 즉시 정지하고, 장애물 제거 후 주행을 재개하는 과정입니다.

Link: [Demo Video](https://drive.google.com/file/d/1aCCeBX-2uWAHyxEKOkwqwYk4OQHJBeyI/view)
Link: [Demo Video](https://drive.google.com/file/d/1WdGiZJUMF5BkIpwKpo1OEWq0tMjJSx-p/view)

## 프로젝트 의의

이 프로젝트는 단순히 ROS2 명령어를 실행하는 것이 아니라, 실물 로봇에서 SLAM, Localization, Navigation, Obstacle Avoidance, Emergency Stop까지 이어지는 전체 자율주행 파이프라인을 직접 구현했다는 점에 의미가 있습니다.

특히 Nav2 기본 기능만 사용하는 데서 끝나지 않고, cmd_vel_nav와 cmd_vel 사이에 직접 구현한 Safety Node를 삽입하여 Emergency Stop 기능을 추가했습니다. 이를 통해 ROS2 시스템을 목적에 맞게 확장하고, 실제 로봇 주행에서 필요한 안전 제어 구조를 설계할 수 있었습니다.

## 향후 개선 방향

향후에는 LiDAR뿐만 아니라 Camera 기반 객체 인식을 추가하여 장애물의 종류를 구분하는 방향으로 확장할 수 있습니다.

사람, 동물, 일반 장애물 등 장애물 유형에 따라 감속, 정지, 대기 정책을 다르게 적용하면 더 정교한 자율주행 안전 시스템으로 발전시킬 수 있습니다.

또한 launch 파일과 파라미터 파일을 더 정리하여 bringup부터 Nav2, Safety Node 실행까지 한 번의 명령으로 안정적으로 실행되는 구조로 개선할 수 있습니다.
