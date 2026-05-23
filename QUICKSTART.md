# 🚀 快速开始指南

## 项目已准备完毕！

你现在有了一个完整的、结构化的学习项目，包含：

✅ **目录结构**：按学习顺序组织（A1 → A6, B1 → B6）
✅ **详细 notes.md**：每个任务都有完整的学习指南
✅ **完整代码**：A2 的 boto3 实现（可即时运行）
✅ **费用预警**：每个步骤都标注了费用
✅ **最终总结模板**：学完后用来汇总笔记

---

## 📋 开始之前

### 1. 准备工作

```bash
# 验证 AWS 凭证已配置
aws sts get-caller-identity
# 应该看到：Account, UserId, Arn

# 安装 Python 依赖
cd Track_A_DynamoDB_Aurora/A2_DynamoDB_Boto3
pip3 install -r requirements.txt
```

### 2. 理解项目结构

```
你的项目根目录
├── README.md                          # 项目总览
├── SETUP_AND_COSTS.md                 # 费用详解
├── QUICKSTART.md                      # 本文件
├── aws_one_day_hands_on_guide.md      # 原始学习计划
│
├── Track_A_DynamoDB_Aurora/           # 轨道 A：数据库
│   ├── A1_DynamoDB_Console/           # 手动操作
│   │   └── notes.md
│   ├── A2_DynamoDB_Boto3/             # 编程实操 ← 推荐从这里开始！
│   │   ├── dynamodb_crud.py           # 完整代码（有详细注释）
│   │   ├── requirements.txt
│   │   └── notes.md
│   ├── A3_Single_Table_Design/        # 理论学习
│   ├── A4_Aurora_Setup/               # 数据库配置
│   ├── A5_Aurora_Architecture/        # 架构理论
│   └── A6_Comparison/                 # 对比总结
│
├── Track_B_Networking/                # 轨道 B：网络
│   ├── B1_VPC_Setup/
│   ├── B2_EC2_Verification/
│   ├── B3_Security/
│   ├── B4_Transit_Gateway/            # 概念学习（不部署）
│   ├── B5_Route53/
│   └── B6_Cleanup/                    # 清理资源（重要！）
│
└── learning_notes/
    └── final_summary.md               # 最终总结（完成后填写）
```

---

## 🎯 推荐学习路径

### Phase 1：DynamoDB 速成（~2 小时）

```
Step 1: 理解概念
  → 读 A1_DynamoDB_Console/notes.md 的"关键概念"部分
  
Step 2: 实践编程 ⭐ 推荐从这里开始！
  → cd Track_A_DynamoDB_Aurora/A2_DynamoDB_Boto3
  → python3 dynamodb_crud.py
  → 观察输出，理解每个操作
  
Step 3: 修改代码实验
  → 修改 dynamodb_crud.py
  → 尝试不同的查询
  → 观察费用变化
  
Step 4: 动手在 Console 操作
  → 到 AWS Console 手动创建表（A1）
  → 验证代码中创建的数据
  
Step 5: 理论深化
  → 读 A3_Single_Table_Design 的 notes
  → 浏览 Mac 老师的 repo
```

### Phase 2：Aurora 和对比（~2 小时）

```
Step 1: 创建 Aurora Serverless cluster（A4）
  → 参考 A4_Aurora_Setup/notes.md
  → 记录 endpoint 和连接信息
  
Step 2: 运行 SQL 对比
  → 在 Query Editor 运行所有示例 SQL
  → 对比与 DynamoDB 的差异
  
Step 3: 理解架构（A5）
  → 读 A5_Aurora_Architecture/notes.md
  → 理解 storage-compute 分离
  
Step 4: 写对比笔记（A6）
  → 回答 A6 中的场景选择题
  → 写出你自己的对比笔记
  
⚠️ 别忘了删除 Aurora cluster！(防止持续扣费)
```

### Phase 3：网络架构（~3-4 小时）

```
Step 1: VPC 基础（B1）
  → 在 Console 手动配置 VPC、subnet、IGW
  → 参考 B1_VPC_Setup/notes.md
  
Step 2: 部署和验证（B2）
  → 启动 public 和 private EC2
  → SSH 进入验证网络连通性
  → 理解 NAT Gateway 的作用
  
Step 3: 安全规则（B3）
  → 配置 Security Group
  → 观察 stateful firewall 的行为
  
Step 4: 企业网络设计（B4）
  → 读 B4_Transit_Gateway/notes.md
  → 不需要实际部署
  
Step 5: DNS 和服务发现（B5）
  → 创建 Route 53 private hosted zone
  → 配置 A record 和 CNAME
  → 从 EC2 验证 DNS 解析
  
Step 6: 清理（B6）
  → 按顺序删除所有资源 ⚠️ 很重要！
  → 检查费用已停止
```

---

## 💻 立即运行代码

### 快速体验 A2（5 分钟）

```bash
# 1. 进入目录
cd Track_A_DynamoDB_Aurora/A2_DynamoDB_Boto3

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 运行代码
python3 dynamodb_crud.py

# 预期输出（看起来像这样）：
# ========================================
# DynamoDB CRUD 操作演示
# ========================================
# 
# ✓ 已连接到 AWS DynamoDB (区域: us-east-1)
# 
# 【1】创建表...
# ✓ 表 'MusicLibrary' 已创建
# 
# 【2】插入数据...
#   ✓ 插入：The Beatles - Hey Jude ...
# ...
```

---

## 📖 每个文件的用途

### notes.md 文件
- **用途**：学习指南 + 思考题 + 完成检查清单
- **如何用**：
  1. 先读"学习目标"和"关键概念"
  2. 按"操作步骤"实践
  3. 回答"思考题"
  4. 打钩"完成标志"

### dynamodb_crud.py
- **用途**：完整的可运行代码示例
- **特点**：
  - 每个方法都有详细的 docstring
  - 包含了所有 7 个 CRUD 操作
  - 有性能对比和费用分析
- **修改建议**：
  - 改变 table schema
  - 实现更复杂的查询
  - 添加错误处理

---

## ⚠️ 费用快速提醒

| 项目 | 费用 | 关键提醒 |
|------|------|---------|
| DynamoDB | $0-0.50 | 按需计费，很便宜 |
| Aurora | $0-1.00 | **最贵！** 用完立即删除 cluster |
| VPC/EC2 | $0-1.00 | t2.micro 免费层，但 NAT 按小时 |
| NAT Gateway | ~$0.045/小时 | **最容易超支！** 完成后立即删除 |
| Route 53 | $0.50/月 | Private zone 便宜 |

**成本控制三原则**：
1. ✅ 立即删除：Aurora cluster、NAT Gateway
2. ✅ 监控费用：Billing Dashboard 每天看一遍
3. ✅ 按顺序清理：B6 的删除顺序很重要

---

## 🎓 学习不同阶段的目标

### 初级（理解概念）
- [ ] 能解释 DynamoDB 和 Aurora 的区别
- [ ] 能画出 VPC 的网络图
- [ ] 能列举 public/private subnet 的特点

### 中级（动手实践）
- [ ] 能写 Python 代码操作 DynamoDB
- [ ] 能在 Console 创建 VPC 和配置路由
- [ ] 能设计一个简单的 key schema

### 高级（架构设计）
- [ ] 能为实际场景选择合适的数据库
- [ ] 能设计多 VPC 的网络拓扑（用 TGW）
- [ ] 能优化成本和性能

---

## 🤔 常见问题

### Q1: 代码运行报错 "NoCredentialsError"
```
A: AWS 凭证未配置
解决：
  1. aws configure
  2. 输入 Access Key 和 Secret Key
  3. 验证：aws sts get-caller-identity
```

### Q2: 代码运行报错 "table not exists"
```
A: DynamoDB table 还没创建
解决：
  代码会自动创建表，如果报错：
  1. 检查 AWS 权限
  2. 确保区域设置正确（默认 us-east-1）
```

### Q3: 为什么 Aurora 这么贵？
```
A: Aurora Serverless 按 ACU-hour 计费
  最小 0.5 ACU = ~$0.22/小时
  如果运行 1 小时 = $0.22
  
解决：用完立即删除！
  - 不是停止，是完全删除 cluster
  - 删除前：Actions → Delete
  - 勾选：Delete automated backups（省钱）
```

### Q4: 我想跳过某些步骤
```
建议顺序：
  必做：A2 (boto3), B1 (VPC), B2 (EC2), B5 (Route 53)
  可选：A1 (手动操作), B3 (详细 SG), B4 (理论)
  不要跳过：B6 (清理！)
```

---

## 📊 预计时间表

| Phase | 任务 | 时间 | 说明 |
|-------|------|------|------|
| 🔴 红 | 准备工作 | 15 min | 配置凭证、安装依赖 |
| 🟡 黄 | Track A | 2-3 hours | DynamoDB + Aurora |
| 🟢 绿 | Track B | 3-4 hours | VPC + Networking |
| 🔵 蓝 | 总结笔记 | 1-2 hours | 填写 final_summary.md |
| **总计** | | **~8 小时** | |

---

## ✅ 完成后的成就

- [x] 理解了 2 个分布式数据库系统
- [x] 实践了云基础设施配置
- [x] 体验了 trade-off decision 的现实意义
- [x] 学到了企业级网络设计
- [x] 有了和 Mac 老师讨论的话题

---

## 🚀 下一步建议

**短期（1 周内）**：
- 写笔记总结：填写 `final_summary.md`
- 分享给 Mac 老师：讨论 single-table design

**中期（1 个月）**：
- 深入 DynamoDB：学 GSI, DynamoDB Streams
- 学习 Kubernetes：k8s 网络模型
- AWS 认证：考虑 SAA (Solutions Architect)

**长期（3 个月）**：
- 参与开源项目
- 在实际工作中应用学到的知识
- 教别人（最好的学习方式！）

---

## 💬 需要帮助？

### 代码问题
→ 检查 notes.md 中的"常见问题"部分

### AWS 操作问题
→ 查看 AWS 官方文档或 Console 的帮助

### 概念不清楚
→ 重新阅读对应 notes.md 的"关键概念"

### 费用问题
→ 检查 SETUP_AND_COSTS.md

---

**祝学习愉快！🎉**

有任何问题，随时回到这个文件查看。
