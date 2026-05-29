Kinase Inhibitor Drug Discovery

kinase_round_1.txt(round1: main.nf, nextflow)
kinase_round_n.txt(round N: main.nf, nextflow)

#1. target, off-target data preprocessing
1.1. Off-Target 선정
KLIFS + KiSSim 활용
	•	KLIFS: 326개 kinase의 구조 데이터 (85개 공통 residue)
	•	KiSSim: 구조 유사도 계산 → Target kinase와 유사한 off-target 선정
1.2. Bioactivity 데이터 수집
PubChem에서 다운로드
	•	Target kinase: Active 화합물
	•	Off-target kinase: Inactive 화합물
	•	Canonical SMILES 추가
	•	중복/충돌 라벨 제거
1.3. 데이터 필터링
화합물 품질 관리
	•	활성 측정값: IC50, Kd, Ki, GI50, EC50, AC50
	•	분자량 < 1000 Da
	•	Heavy atom > 12개
	•	금속 원자 제외
	•	최소 2개 단백질에서 측정된 데이터


#2. M-FRAG: Substructure-Based Molecular Generation via Molecule–Fragment Representation Alignment
round2이상부터 activity cliff 기반으로 assay 값을 기반으로 generation
Drug discovery is a complex and resource-intensive process requiring the design of molecules that possess specific chemical and biological properties, such as high binding affinity and drug-likeness. Fragment-based drug discovery (FBDD) has gained prominence as a strategy for efficiently identifying lead compounds by deconstructing molecules into smaller fragments. However, existing approaches face challenges in fully leveraging the relationships between molecules and their constituent fragments, especially in optimizing molecular properties. In this paper, we introduce Molecule-Fragment Representation Alignment space for RL-based Generation (M-FRAG), a novel framework that harmonizes molecule and fragment embeddings in a shared, property-driven space. By aligning fragments with their molecular context, M-FRAG ensures that fragment selection is optimized both for chemical feasibility and the desired molecular properties. Using reinforcement learning, M-FRAG generates chemically realistic molecules optimized for target properties while also providing interpretability for individual fragments during the molecule generation process. Experimental results demonstrate that M-FRAG outperforms existing methods in terms of optimization, diversity, and chemical validity, positioning it as a powerful tool for the efficient and transparent generation of drug-like molecules.

#3. filtering by drug likeness
This script processes input CSV or TXT files containing molecular SMILES strings. It uses RDKit (and the QEPPI module) to calculate drug-like properties and performs filtering according to user-defined criteria. The filtering is divided into two stages:

아래와 같은 정해진 rule을 통해서 하기도 하고 각 property 기준을 custom하게 만들어서 filtering하기도 해
DRUG_LIKENESS_RULES  = {
    "lipinski_rule" : {
        "MW" : (None, 500),
        "HBD": (None, 5),
        "HBA": (None, 10),
        "LOGP": (None, 5)
    },
    "veber_rule" : {
        "ROTATABLE_BONDS" : (None, 10),
        "TPSA": (None, 140),
    },
    "egan_filter" : {
        "LOGP" : (None, 5.88),
        "TPSA": (None, 131.6),
    },
    "ghose_filter" : {
        "MW" : (160, 480),
        "LOGP": (-0.4, 5.6),
        "NUM_ATOM" : (20, 70),
        "MOL_REFRAC": (40, 130),
    },
    "mozziconacci" : {
        "ROTATABLE_BONDS" : (None, 15),
        "NUM_RING": (None, 6),
        "HALOGEN": (None, 7),
        "NUM_N": (1, None),
        "NUM_O": (1, None)
    },
    "muegge_rule" : {
        "MW" : (200, 600),
        "LOGP": (-2, 5),
        "TPSA": (0, 150),
        "NUM_RING": (None, 7),
        "NUM_C": (5, None),
        "HETEROATOMS": (2, None),
        "ROTATABLE_BONDS": (None, 15),
        "HBA": (None, 10),
        "HBD": (None, 5)
    },
    "rule_of_3" : {
        "MW" : (None, 300),
        "HBD": (None, 3),
        "HBA": (None, 3),
        "LOGP": (None, 3),
        "ROTATABLE_BONDS": (None, 3)
    },
    "rule_of_4" : {
        "MW" : (400, None),
        "NUM_RING": (4, None),
        "HBA": (4, None),
        "LOGP": (4, None),
    },
}

#4. ADME-Drug-likeness filtering

Recent breakthroughs in AI-driven generative models enable the rapid design of extensive molecular libraries, creating an urgent need for fast and accurate drug-likeness evaluation. Traditional approaches, however, rely heavily on structural descriptors and overlook pharmacokinetic (PK) factors such as absorption, distribution, metabolism, and excretion (ADME). Furthermore, existing deep-learning models neglect the complex interdependencies among ADME tasks, which play a pivotal role in determining clinical viability.
We introduce ADME-DL (drug likeness), a novel two-step pipeline that first enhances diverse range of Molecular Foundation Models (MFMs) via sequential ADME multi-task learning. By enforcing an A→D→M→E flow—grounded in a data-driven task dependency analysis that aligns with established pharmacokinetic principles—our method more accurately encodes PK information into the learned embedding space.
In Step 2, the resulting ADME-informed embeddings are leveraged for drug-likeness classification, distinguishing approved drugs from negative sets drawn from chemical libraries.
Through comprehensive experiments, our sequential ADME multi-task learning achieves up to +2.4% improvement over state-of-the-art baselines, and enhancing performance across tested MFMs by up to +18.2%. Case studies with clinically annotated drugs validate that respecting the PK hierarchy produces more relevant predictions, reflecting drug discovery phases. These findings underscore the potential of ADME-DL to significantly enhance the early-stage filtering of candidate molecules, bridging the gap between purely structural screening methods and PK-aware modeling.

The official code implementation for *ADME-DL* model from our paper, "ADME-Drug-Likeness: Enriching Molecular Foundation Models via Pharmacokinetics-Guided Multi-Task Learning for Drug-likeness Prediction".

Here, we provide data and codes for Sequential ADME Multi-task learning and Drug-likeness prediction on three datasets (DrugMAP-ZINC, DrugMAP-PubChem, DrugMAP-ChEMBL)

## Model description
ADME-DL model is trained in two steps:

1. **Step 1:** Sequential ADME Multi-task learning which trains the grouped ADME endpoints in A-D-M-E sequential manner. The grouped data for ADME tasks are provided [here](data/ADME/).
2. **Step 2:** Drug-likeness prediction (DLP). This step first encodes the drug-non-drug datasets with the molecular encoder, then trains an MLP model that classifies drugs from non-drugs. The datasets for DLP tasks are provided [here](data/DLP/).
![model1](img/overview.png)

#5. Docking
protein-ligand 같은 binding affinity를 계산하여 best pose를 찾는 것
quickvina-gpu-2.1을 사용하였음

- **Description**: Run AutoDock Vina using preprocessed data in batch processing mode. Extracts the docking score from each SMILES's PDB file in the output path. A lower docking score indicates better docking. If you're unsure about the `'Ligand ID'` or `'Chain'`, please do not enter values for `'--ligand_id'` and `'--chain'`. You can select them when prompted.
Tang, Shidi, et al. "Vina-GPU 2.1: towards further optimizing docking speed and precision of AutoDock Vina and its derivatives." IEEE/ACM Transactions on Computational Biology and Bioinformatics (2024).
Ding, Ji, et al. "Vina-GPU 2.0: further accelerating AutoDock Vina and its derivatives with graphics processing units." Journal of chemical information and modeling 63.7 (2023): 1982-1998.
Tang, Shidi et al. “Accelerating AutoDock Vina with GPUs.” Molecules (Basel, Switzerland) vol. 27,9 3041. 9 May. 2022, doi:10.3390/molecules27093041
Trott, Oleg, and Arthur J. Olson. "AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading." Journal of computational chemistry 31.2 (2010): 455-461.
Hassan, N. M. , et al. "Protein-Ligand Blind Docking Using QuickVina-W With Inter-Process Spatio-Temporal Integration." Scientific Reports 7.1(2017):15451.
Amr Alhossary, Stephanus Daniel Handoko, Yuguang Mu, and Chee-Keong Kwoh. "Fast, accurate, and reliable molecular docking with QuickVina 2. " Bioinformatics (2015): 2214–2216.

#6. plip
Analyze noncovalent protein-ligand interactions in 3D structures with ease.
# Interaction Filter 사용법

## 필터 조건 설명

- `"min_count"`: 해당 열에 `|`로 구분된 항목이 최소 몇 개 이상 존재해야 하는지를 지정합니다.
- `"max_count"`: 최대 항목 수
- `"residue"`: 항목이 특정 아미노산 이름으로 시작해야 합니다. 문자열 하나 또는 문자열 리스트로 지정할 수 있습니다. (예: `"ARG265_I"`)
- `"chain_type"`: 체인 타입 필터 조건입니다. 항목이 `_SC`(Side chain) 또는 `_BB`(Back bone)로 끝나야 필터에 통과합니다.  
  ※ 이 조건은 `"Hydrogen Bonds"`와 `"Halogen Bonds"` 항목에서만 사용 가능합니다.

---
---

## 지원 상호작용 목록 및 조건

| Interaction Type         | min_count | residues | chain_type (SC/BB) |
|--------------------------|-----------|----------|---------------------|
| Hydrophobic Interactions | ✅        | ✅       | ❌                  |
| Hydrogen Bonds           | ✅        | ✅       | ✅                  |
| Water Bridges            | ✅        | ✅       | ❌                  |
| Salt Bridges             | ✅        | ✅       | ❌                  |
| pi-Stacking              | ✅        | ✅       | ❌                  |
| pi-Cation Interactions   | ✅        | ✅       | ❌                  |
| Halogen Bonds            | ✅        | ✅       | ✅                  |
| Metal Complexes          | ✅        | ✅       | ❌                  |

---

## 각 상호작용 항목별 조건 예시

### Hydrogen Bonds
```python
"Hydrogen Bonds": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I",
    "chain_type": "SC"
}
```

### Halogen Bonds
```python
"Halogen Bonds": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I",
    "chain_type": "SC"
}
```

### Hydrophobic Interactions
```python
"Hydrophobic Interactions": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

### Water Bridges
```python
"Water Bridges": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

### Salt Bridges
```python
"Salt Bridges": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

### pi-Stacking
```python
"pi-Stacking": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

### pi-Cation Interactions
```python
"pi-Cation Interactions": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

### Metal Complexes
```python
"Metal Complexes": {
    "min_count": 3,
    "max_count": 10,
    "residue": "ARG265_I"
}
```

#7. affinity prediction
#7.1. mixingDTA
Overview of MixingDTA; a. Two DT pairs are input, and the mixing ratio is sampled from a Beta distribution for training like C-Mixup; b. The default backbone model of MixingDTA is MEETA. It utilizes embeddings from pretrained language models. Cross-AFA efficiently processes through AFA from a computational cost perspective; c. Edges between DT pairs are connected based on the criteria for defining neighbors. Neighbors with similar labels are closer, following the C-Mixup method. For each view, new nodes are augmented between DT nodes, creating mixed embeddings that are then trained; d. This is a step of multi-view integration. The embeddings are extracted from encoders trained on each GBA scenario and fed into the FC layers of MEETA.

#7.2. cheapnet
Accurately predicting protein-ligand binding affinity is a critical challenge in drug discovery, crucial for understanding drug efficacy. While existing models typically rely on atom-level interactions, they often fail to capture the complex, higher-order interactions, resulting in noise and computational inefficiency. Transitioning to modeling these interactions at the cluster level is challenging because it is difficult to determine which atoms form meaningful clusters that drive the protein-ligand interactions. To address this, we propose CheapNet, a novel interaction-based model that integrates atom-level representations with hierarchical cluster-level interactions through a cross-attention mechanism. By employing differentiable pooling of atom-level embeddings, CheapNet efficiently captures essential higher-order molecular representations crucial for accurate binding predictions. Extensive evaluations demonstrate that CheapNet not only achieves state-of-the-art performance across multiple binding affinity prediction tasks but also maintains prediction accuracy with reasonable computational efficiency. The code of CheapNet is available at https://github.com/hyukjunlim/CheapNet.
This is the official repository for "CheapNet: Cross-attention on Hierarchical representations for Efficient protein-ligand binding Affinity Prediction".

We propose CheapNet, a novel interaction-based model that integrates atom-level representations with hierarchical cluster-level interactions through a cross-attention mechanism. By employing differentiable pooling of atom-level embeddings, CheapNet efficiently captures essential higher-order molecular representations crucial for accurate binding predictions. Extensive evaluations demonstrate that CheapNet not only achieves state-of-the-art performance across multiple binding affinity prediction tasks but also maintains prediction accuracy with reasonable computational efficiency.

CheapNet: Cross-attention on Hierarchical representations for Efficient protein-ligand binding Affinity Prediction
Hyukjun Lim, Sun Kim, and Sangseon Lee† († indicates corresponding author)
Published in The Thirteenth International Conference on Learning Representations, 2025. (ICLR 2025)

#8. ensemble Ranking
# Ensemble affinity values with assay data

This tool analyzes assay data with affinity values from MixingDTA and CHEAPNET, performs data splitting for model training, and generates evaluation results using Autogluon models (with optional scatter plots).

#9. Activity Cliff learning

Activity cliff를 실험하면 "어떤 구조가 활성에 핵심인지" 정확히 알 수 있기 때문입니다.
예시:
Round 1 결과:
* 분자 A: benzene-CH3 → 활성도 90%
* 분자 B: benzene-OH → 활성도 10%
→ Activity cliff 발견! (구조 거의 같은데 활성 8배 차이)
이제 알게 된 것:
* "아, -CH3가 붙으면 활성이 높고, -OH가 붙으면 떨어지는구나!"
* 메틸기(-CH3)가 활성의 핵심
Round 2 전략:
* -CH3 유지하면서 다른 부분만 변형
* benzene-CH3-F 시도
* benzene-CH3-Cl 시도
* → 활성 유지하면서 다른 물성 개선 가능
반대로 activity cliff 없이 랜덤 실험하면:
* 분자 C, D, E, F... 다 비슷비슷한 활성
* 뭘 바꿔야 좋아지는지 힌트가 없음
* 운으로 찾아야 함
→ Activity cliff = SAR의 핵심 정보 = 다음 설계의 명확한 방향


실제 실험우리가 round1에서 시뮬레이션으로 아래 2개 분자가 나옴
* 분자 A: benzene-CH3
* 분자 B: benzene-OH

이걸 가지고 실험해보니 activity가

* 분자 A: benzene-CH3 → 활성도 90%
* 분자 B: benzene-OH → 활성도 10% 
이렇게 나옴 이걸 우리는 assay 데이터라고 부름

그래서 round2에서
이걸 그대로 넣고 돌리면이제 mfrag는 이거 분자들의 substructure 기반으로 돌려서 새로운 molecule들을 생성해주고
activity_cliff(acactive알고리즘)은 이 assay 값을 기반으로 score를 매겨서 ranking을 줌
Acactive 알고리즘 현재 방식:결론부터 말하면, “benzene‑CH3는 상위, benzene‑OH는 하위”처럼 특정 치환기를 직접 판단해서 정렬하는 방식은 아닙니다. 코드상으로는 다음 기준으로 점수가 만들어집니다.
* score = 예측 활성도 × (1 + cliff_score)
* ranking은 이 score를 내림차순으로 정렬한 결과
즉, 모델이 예측 활성도가 높고, 동시에 라벨드 화합물과 유사한 구조 안에서 “활성 절벽 가능성”이 크다고 판단한 분자가 상위로 올라갑니다.그래서 benzene‑CH3가 실제로 높은 활성로 예측되고 cliff_score도 높게 나오면 상위에 갈 가능성이 크지만, 이건 규칙 기반이 아니라 모델 예측 기반입니다.
 


한번 돌리는게 Round1이고, Round n(2,3,4,…)을 돌리는데, round2부터는 저기서 생성된 후보 molecule들을 실험하고 그 실험한 assay data들을 activity cliff 기반으로 다시 input에 함께 넣어서 molecule generation을 하는 mfrag 툴로 activity가 높았던 substructure를 기반으로 분자를 재생성해서 다시 workflow를 돌리겠다 하는 취지야


# Kinase Inhibitor Drug Discovery 워크플로우

## Kinase Inhibitor 설계의 도전 과제

Kinase는 세포 신호전달의 핵심 단백질로, 약물 개발의 주요 타겟입니다. 인간 몸에는 약 518개의 kinase가 존재하며, 이들은 서로 구조가 매우 유사합니다.[1]

### 왜 어려운가?

**Selectivity 문제**:
- 모든 kinase는 ATP를 인산화 반응에 사용
- ATP binding site 구조가 서로 매우 유사
- Target kinase만 억제하고 다른 kinase는 억제하지 않아야 함

**부작용 위험**:
```
예시: 암 치료용 kinase 억제제
- Target: EGFR (암세포 증식 관여)
- Off-target: SRC, ABL 등 (정상 세포 기능 관여)
- 비선택적 억제 → 심각한 부작용
```

***

## 핵심 아이디어: Selectivity 중심 설계

### 전략

**Target kinase**에서는 **강하게 결합**하고, **Off-target kinase**에서는 **약하게 결합**하는 분자를 찾습니다.

```
Target kinase (EGFR):     강한 억제
Off-target kinase (SRC):  약한 억제
→ 높은 Selectivity
```

### 어떻게 구분하는가?

구조적으로 유사하지만 미묘한 차이가 존재합니다:
- Gatekeeper residue의 크기 차이
- Hinge region의 아미노산 변이
- DFG motif의 입체구조 차이

이러한 **작은 차이를 활용**하는 것이 핵심입니다.

***

## Round 1: 데이터베이스 기반 초기 설계

### 1. Target과 Off-target 선정

**구조 유사도 기반 자동 선정**:[1]
- KLIFS: Kinase 구조 데이터베이스
- KiSSim: 구조 유사도 계산

**자동 선정 과정**:
```
Target: EGFR 입력
  ↓
구조적으로 유사한 kinase 자동 검색
  ↓
Off-targets: ERBB2, ERBB4, SRC, ABL... 선정
```

### 2. 공개 데이터 수집

**PubChem BioAssay** 활용:[1]
- Target kinase에 대한 **active** 화합물 수집 (억제제)
- Off-target kinase에 대한 **inactive** 화합물 수집 (억제하지 않는 것)

**데이터 라벨링**:
```
분자 A → EGFR: Active, SRC: Inactive  ✓ 이상적
분자 B → EGFR: Active, SRC: Active    ✗ 비선택적
분자 C → EGFR: Inactive, SRC: Active  ✗ 잘못된 타겟
```

검증된 화합물 데이터 확보

### 3. 분자 생성: Fragment 기반

**Fragment 기반 접근**:[1]
- Active 화합물들을 작은 조각(fragment)으로 분해
- 고활성 fragment를 학습
- Fragment를 새롭게 조합하여 신규 분자 생성

**생성 원리**:
```
Active 화합물에서 자주 등장하는 fragment:
- Quinazoline core (EGFR 선택적)
- Aniline 치환기
- Morpholine side chain

→ 이들을 새로운 방식으로 조합
```

다수의 후보 분자 생성

### 4. 약물성 필터링

**Lipinski's Rule of 5** 등 적용:[1]
- 분자량 제한
- 수소결합 공여체/수용체 개수
- LogP (소수성)

**ADME 예측**:
- 흡수(Absorption): 경구 투여 시 흡수 가능한가?
- 분포(Distribution): 몸 전체로 잘 분포되는가?
- 대사(Metabolism): 간에서 너무 빨리 분해되지 않는가?
- 배설(Excretion): 적절히 배출되는가?

### 5. 도킹

생성된 분자를 **target kinase와 모든 off-target kinase**에 각각 도킹합니다.[1]

**결합 패턴 분석**:
```
분자 X:
- EGFR(target): 강한 결합 예측
- SRC(off-target): 약한 결합 예측
→ Selectivity 있음 ✓

분자 Y:
- EGFR: 강한 결합 예측
- SRC: 강한 결합 예측
→ 비선택적 ✗
```

### 6. 상호작용 분석

**핵심 질문**: 어떤 residue와 상호작용하는가?[1]

**Target kinase 분석**:
```
EGFR의 핵심 residue:
- MET793 (gatekeeper): 수소결합 형성?
- THR790: 수소결합?
- CYS797: 공유결합 가능?
```

**필터링**:
- Target의 핵심 residue와 상호작용 필수
- Off-target의 핵심 residue와 상호작용 최소화

### 7. 결합 친화도 정밀 예측

**딥러닝 기반 예측**:[1]

여러 관점의 모델을 사용:
- 서열 기반 모델: 단백질 서열과 분자 구조의 상호작용 학습
- 구조 기반 모델: 3D 단백질-리간드 복합체 학습

**Ensemble**: 여러 모델을 결합하여 더 정확한 예측

### 8. Selectivity 기반 최종 순위

**Selectivity Score 계산**:[1]
```
Selectivity = (Target 활성) / (가장 높은 Off-target 활성)
```

**순위 결정**:
- Target 활성이 높을수록 좋음
- Off-target 활성이 낮을수록 좋음
- Selectivity가 높은 순서로 정렬

상위 후보 선정

***

## 실험실 검증

선정된 분자를 실제 실험으로 검증합니다:

```
실험 결과 예시:
분자 A: EGFR 강한 억제, SRC 약한 억제  ✓ 선택적
분자 B: EGFR 강한 억제, SRC 강한 억제  ✗ 비선택적
분자 C: EGFR 약한 억제, SRC 약한 억제  ✗ 비활성
```

이제 **실제 활성도 데이터**가 확보되었습니다.

***

## Round 2+: 학습과 최적화

Round 1의 실험 결과를 활용하여 더 나은 분자를 설계합니다.[1]

### 핵심 통찰: Activity Cliff 발견

```
분자 A (quinazoline-NH-phenyl):    강한 EGFR 억제
분자 B (quinazoline-NH-pyridine):  약한 EGFR 억제
```

**구조는 거의 같은데(phenyl vs pyridine) 활성도는 큰 차이!**

이것을 **Activity Cliff**라고 합니다:
- Phenyl이 소수성 포켓과 잘 맞음
- Pyridine의 질소가 오히려 방해
- **Phenyl 구조가 활성의 핵심**

### Selectivity Activity Cliff도 발견

```
분자 A: EGFR 강한 억제, SRC 약한 억제  (선택적)
분자 B: EGFR 강한 억제, SRC 강한 억제  (비선택적)
```

**미묘한 구조 차이가 selectivity를 결정합니다**:
- EGFR의 작은 gatekeeper에 맞는 크기
- SRC의 큰 gatekeeper에는 입체장애

### Fragment 기반 최적화

실험으로 검증된 분자의 핵심 구조를 유지하면서 최적화합니다.[1]

**생성 전략**:
```
검증된 구조: quinazoline-NH-phenyl (EGFR selective)
  ↓
핵심 유지:
- Quinazoline core (hinge binding)
- NH linker (수소결합)
- Phenyl (소수성 포켓)

변형 시도:
- Phenyl에 F, Cl, CF3 치환
- 위치 변경 (ortho, meta, para)
- Side chain 추가/변경
```

**효과**:
- 검증된 활성 scaffold 유지
- Selectivity 패턴 유지
- 미세 조정으로 개선

### 데이터베이스와 실험 데이터 통합

**Round 1**: PubChem 데이터만 사용
**Round 2+**: PubChem + 실험 assay 데이터 병합[1]

**효과**:
```
PubChem 데이터:     일반적 SAR (다수 화합물)
실험 assay 데이터:  프로젝트 특화 SAR (실험 검증)
  ↓
통합 학습 → 더 정확한 예측
```

### 예측 모델 재보정

실험 데이터로 예측 모델의 정확도를 평가하고 보정합니다.[1]

**보정 과정**:
1. 실험한 분자들을 다시 도킹 및 예측
2. 예측값 vs 실험값 비교
3. 모델의 가중치 조정
4. 신규 분자 예측에 적용

**효과**: 반복할수록 예측 정확도 향상

### Activity Cliff 기반 최종 선별

수천 개의 후보 중 다음 실험할 분자를 선택할 때, 단순히 예측값만 보지 않습니다.[1]

**Activity Cliff 기반 선별**:
```
새로운 분자가 검증된 고활성 분자와 얼마나 유사한가?
구조는 유사하지만 selectivity가 더 좋을 가능성은?
```

**선정 전략**:
- 검증된 선택적 구조와 유사하면서 새로운 변형 우선
- 완전히 새로운 scaffold도 일부 포함
- 탐색과 최적화 균형

**예시**:
```
검증된 분자: quinazoline-NH-phenyl (EGFR selective)

최적화 방향:
- quinazoline-NH-phenyl-F (매우 유사)
- quinazoline-NH-phenyl-Cl (매우 유사)
→ EGFR selectivity 유지하면서 활성 개선 기대

탐색 방향:
- pyridopyrimidine-NH-phenyl (다른 core)
- quinazoline-O-phenyl (다른 linker)
→ 새로운 selectivity 패턴 발견 가능
```

**효과**:
- 실험 효율 극대화
- 명확한 구조-활성 관계(SAR) 학습
- Selectivity 개선

***

## 전체 플로우 요약

### Round 1: 초기 발견
```
Target + Off-target 선정
    ↓
공개 데이터 수집 (PubChem)
    ↓
Fragment 기반 분자 생성
    ↓
약물성 필터링 (Lipinski + ADME)
    ↓
도킹: Target + Off-targets
    ↓
상호작용 분석
    ↓
결합 친화도 예측 (ensemble)
    ↓
Selectivity 기반 순위
    ↓
상위 후보 선정
    ↓
실험 검증 → Activity Cliff 발견
```

### Round 2+: 학습과 최적화
```
공개 데이터 + 실험 데이터 통합
    ↓
Fragment 기반 최적화:
  - 검증된 선택적 구조 중심
  - 새로운 scaffold 탐색
    ↓
약물성 필터링
    ↓
도킹: Target + Off-targets
    ↓
상호작용 분석
    ↓
결합 친화도 예측
  └─ 실험 데이터로 모델 재보정
    ↓
Selectivity 기반 순위
    ↓
Activity Cliff 기반 선별:
  - 검증된 선택적 구조 주변 우선
  - 예측 정확도 점진적 향상
    ↓
상위 후보 선정
    ↓
실험 검증 → 더 많은 Activity Cliff 발견
    ↓
반복...
```

***

## 핵심 원리

### 1. Data-Driven Design
공개 데이터베이스를 활용하여 시작부터 검증된 SAR을 학습합니다:[1]
- PubChem: 대량의 kinase inhibitor 데이터
- KLIFS: 다수의 kinase 구조 데이터
- 처음부터 "알려진 것"에서 출발

### 2. Selectivity-Centric Approach
Target 활성만이 아닌 **selectivity**를 핵심 지표로 사용합니다:[1]
- Off-target 예측을 필수로 수행
- Selectivity score로 최종 순위 결정
- 부작용 최소화

### 3. Multi-level Filtering
다단계 필터링으로 고품질 후보만 선별:[1]
1. Drug-likeness: 기본 약물성
2. ADME: 약동학 특성
3. Docking: 결합 가능성
4. Interaction profiling: 필수 상호작용 확인

### 4. Ensemble Prediction
여러 관점의 모델 결합:[1]
- 서열 기반 접근
- 구조 기반 접근
- 상호 보완으로 정확도 향상

### 5. Iterative Learning
실험 데이터가 축적될수록 설계가 정교해집니다:[1]
- Round 1: 공개 데이터 기반 (broad exploration)
- Round 2+: 공개 + 실험 데이터 (탐색과 최적화 병행)
- 점점 더 정확한 예측과 선택적 설계

### 6. Activity Cliff as Selectivity Guide
구조가 비슷한데 활성/selectivity가 크게 다른 경우는 매우 중요합니다:
```
분자 A: EGFR 강한 억제, SRC 약한 억제  (선택적)
분자 B: EGFR 강한 억제, SRC 강한 억제  (비선택적)
→ 미묘한 차이가 selectivity 결정
→ 이 차이를 학습하여 더 선택적인 분자 설계
```

***

## PPI Inhibitor와의 차이점

| 측면 | Kinase Inhibitor | PPI Inhibitor |
|------|------------------|---------------|
| **타겟 구조** | 깊은 ATP binding site | 넓고 평평한 interface |
| **초기 데이터** | 풍부 (PubChem, KLIFS) | 부족 (hot-spot 기반) |
| **핵심 과제** | Selectivity (off-target) | 결합력 (binding affinity) |
| **필터링 기준** | 엄격 | 상대적으로 완화 |
| **설계 전략** | Data-driven | Structure-driven |

***

## 실제 적용 예시

### EGFR Kinase Inhibitor 개발 (Gefitinib, Erlotinib)

**Round 1**:
- KLIFS에서 EGFR 구조 및 유사 kinase 수집
- PubChem에서 EGFR active, ERBB2 inactive 화합물 학습
- Quinazoline core가 EGFR selective함을 발견

**Round 2-3**:
- Quinazoline-aniline 구조 최적화
- 치환기가 selectivity 결정
- Gefitinib 개발 (EGFR selective)

**Round 4+**:
- EGFR T790M 돌연변이 출현 (내성)
- Activity cliff 학습으로 3세대 억제제 개발
- Osimertinib (T790M selective)

***

## 결론

Kinase inhibitor 발견은 **공개 데이터 기반 설계 → 실험 검증 → activity cliff 학습 → selectivity 최적화**의 반복 과정입니다.[1]

초기에는 풍부한 공개 데이터를 활용하여 검증된 SAR로부터 시작하고, 실험 데이터가 축적되면 selectivity를 중심으로 최적화합니다. 이 과정에서 발견되는 activity cliff(특히 selectivity cliff)는 미묘한 구조 차이가 어떻게 선택성을 결정하는지 이해하는 핵심 단서가 되며, 점점 더 정확하고 선택적인 설계를 가능하게 합니다.
