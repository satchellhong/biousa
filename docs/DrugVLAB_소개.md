# DrugVLAB SaaS 플랫폼 소개

## 플랫폼 개요
DrugVLAB은 AI 기반 신약개발 워크플로우를 SaaS 형태로 제공하기 위해 설계된 웹 플랫폼이다. 연구용 파이프라인 orchestration에는 Nextflow와 Airflow 계열 구조가 활용되며, API 계층은 Django와 Nginx, 프론트엔드는 React.js 기반으로 구성되어 있다.

## 인프라 아키텍처
플랫폼은 AWS 중심으로 설계되어 있으며 Batch, Lambda, ECS, ECR, SQS와 같은 실행·오케스트레이션 서비스와 EC2, VPC, ALB, WAF, Secrets Manager, Cognito를 포함한 보안·애플리케이션 계층을 사용한다. 데이터 계층에는 EFS, S3, DynamoDB, DataSync가 포함되어 있어 연구 데이터 저장, 파이프라인 실행, 결과 전달을 분리된 형태로 운영할 수 있다.

## 핵심 기능
DrugVLAB은 표적과 과제 특성에 맞춰 분자 생성, 물성 필터링, ADME 평가, 도킹, 상호작용 분석, 결합친화도 예측, 랭킹, 액티브러닝까지 이어지는 end-to-end 계산 신약개발 흐름을 지원한다. 설정 파일에는 Hot2Mol, M-FRAG, PLIP, AutoDock Vina, MixingDTA, CheapNet, AutoGluon, ACActive 등 다수의 모듈이 연결되어 있어 단일 플랫폼 안에서 후보물질 탐색과 우선순위화를 자동화할 수 있다.

## 파이프라인 운영 방식
플랫폼의 워크플로우는 Nextflow DSL2 기반으로 작성되어 있으며, PPI 저해제 생성 파이프라인은 pharmacophore extraction, molecule generation, property filtering, docking, interaction profiling, affinity prediction, ranking, active learning 단계를 순차적으로 수행한다. 로컬 실행 스크립트 역시 사용자명, 워크플로우명, 실행 키, 특정 step, resume 여부를 받아 반복 실험과 재실행이 가능하도록 설계되어 있다.

## 적용 영역
DrugVLAB은 PPI 저해제 탐색뿐 아니라 kinase inhibitor 생성 워크플로우도 별도로 운영할 수 있도록 확장되어 있다. kinase 파이프라인은 bioactivity estimation으로 시작해 오프타깃까지 함께 고려하는 구조를 포함하고 있어, 후보물질 생성 이후 선택성 검토와 랭킹 통합까지 수행할 수 있다.

## 제공 가치
이 플랫폼은 개별 연구자가 서로 다른 오픈소스와 내부 모델을 수작업으로 연결하지 않아도 되도록, 분자 생성부터 실험 우선순위 선정까지를 하나의 운영 환경으로 통합한다. 그 결과 연구팀은 인프라 구축보다 가설 검증과 후보물질 해석에 더 많은 시간을 투입할 수 있고, 반복 가능한 파이프라인 실행을 통해 신약개발 초기 탐색 효율을 높일 수 있다.

## 소개 문구 예시
> DrugVLAB은 AI 모델, 구조기반 해석, 대규모 워크플로우 자동화를 결합한 신약개발 SaaS 플랫폼이다. 연구자는 웹 기반 환경에서 후보물질 생성, 필터링, 도킹, 결합친화도 예측, 랭킹, 액티브러닝까지 연결된 파이프라인을 실행하며 더 빠르게 실험 우선순위를 도출할 수 있다.