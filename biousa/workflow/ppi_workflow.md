PPI Inhibitor Drug Discovery

ppi_round_1.txt(round1: main.nf, nextflow)
ppi_round_n.txt(round N: main.nf, nextflow)

#1-1. hotspot guided molecule generation
This code is based on the methodology described in "Target-specific design of drug-like PPI inhibitors via hot-spot-guided generative deep learning". 

Protein–protein interactions (PPIs) are vital therapeutic targets. However, the large and flat PPI interfaces pose challenges for the development of small-molecule inhibitors. Traditional computer-aided drug design approaches typically rely on pre-existing libraries or expert knowledge, limiting the exploration of novel chemical spaces needed for effective PPI inhibition. To overcome these limitations, we introduce Hot2Mol, a deep learning framework for the de novo design of drug-like, target-specific PPI inhibitors. Hot2Mol generates small molecules by mimicking the pharmacophoric features of hot-spot residues, enabling precise targeting of PPI interfaces without the need for bioactive ligands. 

#1-2. M-FRAG: Substructure-Based Molecular Generation via Molecule–Fragment Representation Alignment
round2이상부터 activity cliff 기반으로 assay 값을 기반으로 generation
Drug discovery is a complex and resource-intensive process requiring the design of molecules that possess specific chemical and biological properties, such as high binding affinity and drug-likeness. Fragment-based drug discovery (FBDD) has gained prominence as a strategy for efficiently identifying lead compounds by deconstructing molecules into smaller fragments. However, existing approaches face challenges in fully leveraging the relationships between molecules and their constituent fragments, especially in optimizing molecular properties. In this paper, we introduce Molecule-Fragment Representation Alignment space for RL-based Generation (M-FRAG), a novel framework that harmonizes molecule and fragment embeddings in a shared, property-driven space. By aligning fragments with their molecular context, M-FRAG ensures that fragment selection is optimized both for chemical feasibility and the desired molecular properties. Using reinforcement learning, M-FRAG generates chemically realistic molecules optimized for target properties while also providing interpretability for individual fragments during the molecule generation process. Experimental results demonstrate that M-FRAG outperforms existing methods in terms of optimization, diversity, and chemical validity, positioning it as a powerful tool for the efficient and transparent generation of drug-like molecules.

#2. filtering by drug likeness
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

#3. ADME-Drug-likeness filtering

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

#4. Docking
protein-ligand 같은 binding affinity를 계산하여 best pose를 찾는 것
quickvina-gpu-2.1을 사용하였음

- **Description**: Run AutoDock Vina using preprocessed data in batch processing mode. Extracts the docking score from each SMILES's PDB file in the output path. A lower docking score indicates better docking. If you're unsure about the `'Ligand ID'` or `'Chain'`, please do not enter values for `'--ligand_id'` and `'--chain'`. You can select them when prompted.
Tang, Shidi, et al. "Vina-GPU 2.1: towards further optimizing docking speed and precision of AutoDock Vina and its derivatives." IEEE/ACM Transactions on Computational Biology and Bioinformatics (2024).
Ding, Ji, et al. "Vina-GPU 2.0: further accelerating AutoDock Vina and its derivatives with graphics processing units." Journal of chemical information and modeling 63.7 (2023): 1982-1998.
Tang, Shidi et al. “Accelerating AutoDock Vina with GPUs.” Molecules (Basel, Switzerland) vol. 27,9 3041. 9 May. 2022, doi:10.3390/molecules27093041
Trott, Oleg, and Arthur J. Olson. "AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading." Journal of computational chemistry 31.2 (2010): 455-461.
Hassan, N. M. , et al. "Protein-Ligand Blind Docking Using QuickVina-W With Inter-Process Spatio-Temporal Integration." Scientific Reports 7.1(2017):15451.
Amr Alhossary, Stephanus Daniel Handoko, Yuguang Mu, and Chee-Keong Kwoh. "Fast, accurate, and reliable molecular docking with QuickVina 2. " Bioinformatics (2015): 2214–2216.

#5. plip
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

#6. affinity prediction
#6.1. mixingDTA
Overview of MixingDTA; a. Two DT pairs are input, and the mixing ratio is sampled from a Beta distribution for training like C-Mixup; b. The default backbone model of MixingDTA is MEETA. It utilizes embeddings from pretrained language models. Cross-AFA efficiently processes through AFA from a computational cost perspective; c. Edges between DT pairs are connected based on the criteria for defining neighbors. Neighbors with similar labels are closer, following the C-Mixup method. For each view, new nodes are augmented between DT nodes, creating mixed embeddings that are then trained; d. This is a step of multi-view integration. The embeddings are extracted from encoders trained on each GBA scenario and fed into the FC layers of MEETA.

#6.2. cheapnet
Accurately predicting protein-ligand binding affinity is a critical challenge in drug discovery, crucial for understanding drug efficacy. While existing models typically rely on atom-level interactions, they often fail to capture the complex, higher-order interactions, resulting in noise and computational inefficiency. Transitioning to modeling these interactions at the cluster level is challenging because it is difficult to determine which atoms form meaningful clusters that drive the protein-ligand interactions. To address this, we propose CheapNet, a novel interaction-based model that integrates atom-level representations with hierarchical cluster-level interactions through a cross-attention mechanism. By employing differentiable pooling of atom-level embeddings, CheapNet efficiently captures essential higher-order molecular representations crucial for accurate binding predictions. Extensive evaluations demonstrate that CheapNet not only achieves state-of-the-art performance across multiple binding affinity prediction tasks but also maintains prediction accuracy with reasonable computational efficiency. The code of CheapNet is available at https://github.com/hyukjunlim/CheapNet.
This is the official repository for "CheapNet: Cross-attention on Hierarchical representations for Efficient protein-ligand binding Affinity Prediction".

We propose CheapNet, a novel interaction-based model that integrates atom-level representations with hierarchical cluster-level interactions through a cross-attention mechanism. By employing differentiable pooling of atom-level embeddings, CheapNet efficiently captures essential higher-order molecular representations crucial for accurate binding predictions. Extensive evaluations demonstrate that CheapNet not only achieves state-of-the-art performance across multiple binding affinity prediction tasks but also maintains prediction accuracy with reasonable computational efficiency.

CheapNet: Cross-attention on Hierarchical representations for Efficient protein-ligand binding Affinity Prediction
Hyukjun Lim, Sun Kim, and Sangseon Lee† († indicates corresponding author)
Published in The Thirteenth International Conference on Learning Representations, 2025. (ICLR 2025)

#7. Ranking
# Ensemble affinity values with assay data

This tool analyzes assay data with affinity values from MixingDTA and CHEAPNET, performs data splitting for model training, and generates evaluation results using Autogluon models (with optional scatter plots).

#8. Activity Cliff learning

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

# PPI Inhibitor Drug Discovery 워크플로우
 
## PPI Inhibitor 설계의 도전 과제
 
단백질-단백질 상호작용(PPI)을 억제하는 것은 약물 개발에서 가장 어려운 과제 중 하나입니다.[1]
 
### 왜 어려운가?
 
**일반적인 단백질 약물 타겟**:
- 깊고 좁은 결합 포켓 (예: kinase ATP binding site)
- 작은 분자로 효과적으로 결합 가능
- 명확한 활성 화합물 데이터 존재
 
**PPI Interface**:
- 넓고 평평한 표면 (~1,500-3,000 Ų)
- 깊은 포켓 없음
- 대부분의 영역은 결합 에너지 기여도 낮음
- 기존 억제제 데이터 부족
 
***
 
## 핵심 아이디어: Hot-spot 기반 설계
 
### Hot-spot이란?
 
PPI interface 중 **결합 에너지 기여도가 매우 큰 소수의 residue**를 hot-spot이라고 합니다. 전체 interface의 ~10%만이 결합 에너지의 ~80%를 담당합니다.
 
**예시**: MDM2-p53 상호작용
- Interface 전체: 약 20개 residue 접촉
- Hot-spot: PHE19, TRP23, LEU26 (p53 측) 3개만
- 이 3개가 결합 에너지의 대부분을 담당
 
### 전략
 
전체 PPI interface를 막으려고 하지 말고, **hot-spot residue가 하는 역할을 소분자로 모방**합니다.
 
```
Hot-spot: TRP23 (큰 소수성 aromatic)
    ↓
소분자: Naphthalene, Indole (작지만 유사한 특성)
```
 
***
 
## Round 1: Hot-spot을 모방하는 분자 만들기
 
### 1. Hot-spot 약리활성단 추출
 
PPI complex 구조에서 hot-spot residue의 화학적 특성을 추출합니다:[1]
- **위치**: 3차원 좌표
- **특성**: 소수성, 수소결합 공여/수용, 방향성, 전하 등
 
### 2. 분자 생성: Pharmacophore 기반
 
Transformer 기반 생성 모델이 hot-spot의 약리활성단을 학습하여 이를 모방하는 소분자를 생성합니다.[1]
 
**생성 원리**:
```
Hot-spot TRP23 (indole + 소수성)
  → 생성 분자: Indole 유도체, 나프탈렌 유도체
 
Hot-spot ARG265 (양이온 + H-bond donor)
  → 생성 분자: Guanidinium, Amidine 구조 포함
```
 
수천~수만 개의 후보 분자 생성
 
### 3. 약물성 필터링
 
**일반 약물 규칙**과 **PPI 특화 규칙** 적용:[1]
 
- Lipinski Rule of 5: 기본 약물성
- Rule of 4 (PPI 특화): 더 큰 분자량, 더 많은 aromatic ring 허용
- ADME 예측: 흡수, 분포, 대사, 배설 특성 평가
 
### 4. 도킹
 
생성된 분자를 PPI interface에 도킹합니다:[1]
- Hot-spot residue 주변에 결합할 수 있는지 확인
- 결합 pose와 친화도 예측
 
### 5. 상호작용 분석
 
**핵심 질문**: 정말 hot-spot과 제대로 상호작용하는가?[1]
 
분석 항목:
- ARG265와 수소결합 형성?
- TYR103와 π-π stacking?
- PHE87의 소수성 포켓 채움?
 
**필터링**: Hot-spot과 필수 상호작용이 없는 분자 제거
 
### 6. 결합 친화도 정밀 예측
 
딥러닝 모델로 결합 친화도를 정밀하게 예측합니다:[1]
 
- Cross-attention 기반 모델: 단백질 서열과 분자 구조의 상호작용 학습
- 3D 구조 기반 모델: 단백질-리간드 복합체의 공간적 상호작용 학습
 
여러 모델을 결합(ensemble)하여 신뢰도 높은 예측값 산출
 
### 7. 최종 순위
 
예측된 결합 친화도 기준으로 순위를 매겨 상위 후보 선정[1]
 
***
 
## 실험실 검증
 
선정된 분자를 실제 실험으로 검증합니다:
 
```
실험 결과 예시:
분자 A (indole-OH): IC50 = 10 nM   ✓ 강한 억제
분자 B (indole-NH2): IC50 = 500 nM  △ 약한 억제
분자 C (phenyl-F): IC50 = 1000 nM   ✗ 매우 약함
```
 
이제 **실제 활성도 데이터**가 확보되었습니다.
 
***
 
## Round 2+: 학습과 최적화
 
Round 1의 실험 결과를 활용하여 더 나은 분자를 설계합니다.[1]
 
### 핵심 통찰: Activity Cliff 발견
 
```
분자 A (indole-OH):  IC50 = 10 nM
분자 B (indole-NH2): IC50 = 500 nM
```
 
**구조는 거의 같은데 활성도는 50배 차이!**
 
이것을 **Activity Cliff**라고 합니다. 이는 매우 중요한 정보입니다:
- OH가 ARG265와 강한 수소결합 형성
- NH2는 수소결합 약함
- **OH 구조가 활성의 핵심**
 
### 두 가지 병행 전략
 
Round 2부터는 두 가지 접근을 동시에 사용합니다:[1]
 
#### 전략 1: 계속 탐색하기
- Round 1과 동일하게 hot-spot 모방 분자 생성
- 새로운 화학 구조 계속 발견
- 탐색(Exploration) 유지
 
#### 전략 2: 검증된 구조 최적화하기
- 실험으로 검증된 고활성 분자(indole-OH)를 기반
- Fragment 기반 생성: 이 분자의 핵심 구조는 유지
- 다른 부분만 변형
 
**생성 예시**:
```
검증된 구조: indole-OH
  ↓
새로운 변형들:
- indole-OH + CF3 치환
- indole-OH + 추가 aromatic ring
- indole-OH + Cl 치환 (위치 변경)
```
 
### Activity Cliff를 활용한 최종 선별
 
수천 개의 후보 중 다음 실험할 분자를 선택할 때, 단순히 예측 활성도만 보지 않습니다.[1]
 
**Activity Cliff 기반 선별**:
```
새로운 분자가 검증된 고활성 분자와 얼마나 유사한가?
구조는 유사하지만 활성이 더 좋을 가능성은?
```
 
**선정 전략**:
- 검증된 고활성 구조와 유사하면서 새로운 변형 우선
- 완전히 새로운 scaffold도 일부 포함
- 실험 효율 극대화
 
**효과**:
- 명확한 구조-활성 관계(SAR) 학습
- 점진적 개선
- Local minimum 회피
 
***
 
## 전체 플로우 요약
 
### Round 1: 초기 발견
```
Hot-spot 분석
    ↓
Hot-spot 모방 분자 생성
    ↓
필터링 (약물성 + ADME)
    ↓
도킹 + 상호작용 분석
    ↓
결합 친화도 예측
    ↓
상위 후보 선정
    ↓
실험 검증 → Activity Cliff 발견
```
 
### Round 2+: 학습과 최적화
```
Hot-spot 분석 (동일)
    ↓
이중 생성 전략:
  ├─ Pharmacophore 기반: 새로운 구조 탐색
  └─ Fragment 기반: 검증된 구조 최적화
    ↓
필터링 + 도킹 + 상호작용 분석
    ↓
결합 친화도 예측
  └─ 실험 데이터로 모델 재보정
    ↓
Activity Cliff 기반 선별:
  - 검증된 고활성 구조 주변 우선
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
 
### 1. Structure-Based Design without Prior Ligands
기존 활성 화합물이 없어도 시작 가능합니다. Hot-spot residue 정보만으로 설계를 시작하기 때문에 novel target에도 적용할 수 있습니다.[1]
 
### 2. Hot-spot-Centric Approach
PPI interface 전체가 아닌 hot-spot만 집중합니다. 이는 현실적이고 효율적인 전략입니다.
 
### 3. Iterative Learning
실험 결과가 축적될수록 설계가 정교해집니다:[1]
- Round 1: 완전 탐색 (blind search)
- Round 2+: 탐색과 최적화 병행
- 점점 더 정확한 예측
 
### 4. Activity Cliff as Knowledge
구조가 비슷한데 활성이 크게 다른 경우(activity cliff)는 매우 중요한 정보입니다. 이를 통해:
- 어떤 구조가 활성에 필수인지 학습
- 어떤 변형이 유망한지 예측
- 실험 효율 극대화
 
### 5. Exploration and Exploitation Balance
- 탐색: 새로운 화학 구조 발견
- 최적화: 검증된 구조 개선
- 두 전략을 병행하여 local minimum 회피
 
***
 
## Kinase Inhibitor와의 차이점
 
| 측면 | Kinase Inhibitor | PPI Inhibitor |
|------|------------------|---------------|
| **타겟 구조** | 깊은 ATP binding site | 넓고 평평한 interface |
| **초기 설계** | 공개 데이터베이스 활용 | Hot-spot 기반 de novo |
| **분자 크기** | 상대적으로 작음 | 상대적으로 큼 |
| **Selectivity** | 매우 중요 (off-target) | 상대적으로 단순 |
| **난이도** | 높음 | 매우 높음 |
 
***
 
## 실제 적용 예시
 
### MDM2-p53 PPI 억제제 개발
 
**Hot-spot 분석**:
- p53의 PHE19, TRP23, LEU26 3개 residue
- MDM2의 소수성 포켓과 상호작용
 
**Round 1 결과**:
- Indole 기반 분자 발견
- Hot-spot TRP23을 indole로 모방
 
**Round 2-3 최적화**:
- Indole 구조 유지 + 치환기 최적화
- 활성도 점진적 개선
- 임상 시험 진입
 
***
 
## 결론
 
PPI inhibitor 발견은 **hot-spot 중심 설계 → 실험 검증 → activity cliff 학습 → 최적화**의 반복 과정입니다.[1]
 
초기에는 hot-spot을 모방하는 다양한 분자를 생성하여 탐색하고, 실험 데이터가 축적되면 검증된 고활성 구조를 중심으로 최적화합니다. 이 과정에서 발견되는 activity cliff는 구조-활성 관계를 이해하는 핵심 단서가 되며, 점점 더 정확하고 효율적인 설계를 가능하게 합니다.
