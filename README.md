# AWS 分布式系统与网络实战学习

**目标**：通过 8 小时的 hands-on 学习，理解分布式数据库（DynamoDB vs Aurora）和 AWS 网络架构（VPC, Security, Route 53）的核心概念。

**总费用**：< $5（如果按计划清理资源）

**总时间**：~8 小时

---

## 项目结构

```
learn_distributed_system_and_networking/
├── README.md                          # 本文件
├── SETUP_AND_COSTS.md                 # 费用和前置准备
├── aws_one_day_hands_on_guide.md      # 详细学习计划
│
├── Track_A_DynamoDB_Aurora/           # Track A：分布式数据库
│   ├── A1_DynamoDB_Console/
│   │   └── notes.md                   # 手动操作笔记
│   ├── A2_DynamoDB_Boto3/
│   │   ├── dynamodb_crud.py           # Python 代码实现
│   │   ├── requirements.txt            # 依赖
│   │   └── notes.md                   # 学习笔记
│   ├── A3_Single_Table_Design/
│   │   └── notes.md                   # 理论学习笔记
│   ├── A4_Aurora_Setup/
│   │   └── notes.md                   # 数据库设置笔记
│   ├── A5_Aurora_Architecture/
│   │   └── notes.md                   # 架构理论笔记
│   └── A6_Comparison/
│       └── notes.md                   # DynamoDB vs Aurora 对比
│
├── Track_B_Networking/                # Track B：网络架构
│   ├── B1_VPC_Setup/
│   │   └── notes.md                   # VPC 手动配置笔记
│   ├── B2_EC2_Verification/
│   │   ├── verify_vpc.py              # 网络验证脚本
│   │   └── notes.md                   # 验证笔记
│   ├── B3_Security/
│   │   └── notes.md                   # Security Group & NACL 笔记
│   ├── B4_Transit_Gateway/
│   │   └── notes.md                   # Transit Gateway 概念笔记
│   ├── B5_Route53/
│   │   └── notes.md                   # Route 53 笔记
│   └── B6_Cleanup/
│       ├── cleanup.py                 # 清理脚本
│       └── notes.md                   # 清理笔记
│
└── learning_notes/
    └── final_summary.md               # 最终汇总笔记（所有 Track 完成后生成）
```

---

## 学习路径

### Phase 1: Track A - DynamoDB & Aurora（~4.5 小时）
1. **A1**：手动在 AWS Console 创建 DynamoDB table，感受 key-value 模型
2. **A2**：**[Python boto3]** 用代码操作 DynamoDB CRUD，理解 SDK 使用
3. **A3**：研究 single-table design 模式
4. **A4**：手动创建 Aurora cluster，运行 SQL
5. **A5**：理解 Aurora 分布式架构（storage-compute 分离）
6. **A6**：写出 DynamoDB vs Aurora 对比笔记

### Phase 2: Track B - VPC & Networking（~3.5 小时）
1. **B1**：手动配置 VPC、subnet、Internet Gateway
2. **B2**：**[Python boto3]** 部署 EC2，验证网络连通性
3. **B3**：配置 Security Group 规则，理解 stateful firewall
4. **B4**：理论学习 Transit Gateway
5. **B5**：配置 Route 53 private hosted zone
6. **B6**：清理所有资源，避免持续费用

---

## 下一步

→ 进入 `SETUP_AND_COSTS.md` 查看费用清单和前置准备
