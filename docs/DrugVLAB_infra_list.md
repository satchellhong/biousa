# [최종] DrugVLAB-IaC 전체 AWS 서비스 리스트
 
1. 네트워킹 (Networking)
    * VPC: 네트워크 격리, 퍼블릭/프라이빗 서브넷, 가용 영역 구성.
    * ALB (Application Load Balancer): HTTP/HTTPS 트래픽 분산 및 라우팅.
    * VPC Endpoints (VPCE): 프라이빗 통신용 인터페이스 (Secrets Manager, RDS 등).
    * WAF (Web Application Firewall): 보안 필터링 및 로그 기록.

2. 컴퓨팅 (Compute)
    * AWS Batch: 대규모 데이터 처리용 배치 연산 환경.
    * EC2: 백엔드 및 웹 프론트엔드 인스턴스.
    * Lambda: 비동기 작업 및 Billing 관련 서버리스 로직.

3. 데이터베이스 및 스토리지 (DB & Storage)
    * DynamoDB: NoSQL 데이터 저장 (이메일 인증, Billing).
    * RDS / RDS Data API: 관계형 데이터베이스 및 API 접근.
    * S3: 로그(ALB, WAF) 및 데이터 스토리지.
    * EFS (Elastic File System): 컴퓨팅 노드 간 공유 파일 시스템.

4. 보안 및 인증 (Security & Identity)
    * IAM: 리소스 접근 제어 및 권한 관리.
    * Cognito: 사용자 로그인 및 ID 관리.
    * Secrets Manager: 민감한 보안 정보(비밀번호 등) 암호화 저장.
    * KMS: 데이터 암호화 키 관리.
    * ACM: SSL/TLS 인증서 관리.

5. 메시징 및 통신 (Messaging)
    * SQS: 비동기 메시지 큐 (메시지 대기열).
    * SNS: 시스템 알림 서비스.
    * SES: 이메일 발송 서비스.

6. 관리 및 모니터링 (Management & Monitoring)
    * SSM (Systems Manager): 파라미터 저장 및 설정 관리.
    * CloudWatch: 로그 기록, 모니터링 및 이벤트 알람.
    * EventBridge: 시스템 이벤트 처리.
    * STS: 임시 자격 증명 관리.