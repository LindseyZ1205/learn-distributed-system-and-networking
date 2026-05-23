# AWS 分布式系统与网络实战学习 - 最终总结

**学习时间**：~8 小时
**完成日期**：_________________ (你填)
**目标**：理解分布式数据库和 AWS 网络架构的核心概念

---

## 🎯 学习成果概览

### Track A：分布式数据库（DynamoDB vs Aurora）

#### 概念理解
- [ ] 理解了 key-value 和关系型数据库的区别
- [ ] 理解了 DynamoDB 的 partition key / sort key 概念
- [ ] 理解了 single-table design 的必要性和好处
- [ ] 理解了 Aurora 的 storage-compute 分离架构
- [ ] 理解了 DynamoDB 和 Aurora 在 CAP theorem 上的选择

#### 实践操作
- [ ] 在 AWS Console 手动创建 DynamoDB table（A1）
- [ ] 用 Python boto3 实现 CRUD 操作（A2）
- [ ] 在 RDS 创建 Aurora cluster 并运行 SQL（A4）
- [ ] 对比了两个数据库的查询能力和性能（A6）

#### 核心收获
**你现在知道**：
- _________________ (DynamoDB 的最大优势)
- _________________ (Aurora 适用的场景)
- _________________ (单表设计为什么重要)
- _________________ (一致性 vs 可用性的 trade-off)

### Track B：AWS 网络架构（VPC + Networking）

#### 概念理解
- [ ] 理解了 VPC 的隔离和多层网络设计
- [ ] 理解了 public / private subnet 的区别和用途
- [ ] 理解了 Internet Gateway / NAT Gateway 的作用
- [ ] 理解了 Security Group（stateful）vs NACL（stateless）
- [ ] 理解了 Transit Gateway 的 hub-spoke 架构
- [ ] 理解了 Route 53 在服务发现中的角色

#### 实践操作
- [ ] 手动配置 VPC、subnet、IGW、route table（B1）
- [ ] 在 public/private subnet 各部署 EC2（B2）
- [ ] 验证 EC2 的网络连通性和 NAT 工作原理（B2）
- [ ] 配置了 Security Group 规则（B3）
- [ ] 创建了 private hosted zone 和 DNS 记录（B5）

#### 核心收获
**你现在知道**：
- _________________ (为什么要分 public/private subnet)
- _________________ (NAT Gateway 如何让私有实例出网)
- _________________ (Stateful 和 stateless 防火墙的区别)
- _________________ (如何用 DNS 进行服务发现)
- _________________ (为什么企业多用 Transit Gateway)

---

## 📊 DynamoDB vs Aurora 对比总结

| 维度 | DynamoDB | Aurora |
|------|----------|--------|
| 数据模型 | ________________ | ________________ |
| 扩展性 | ________________ | ________________ |
| 一致性 | ________________ | ________________ |
| 查询能力 | ________________ | ________________ |
| 成本 | ________________ | ________________ |

**选择建议**：
- 用 DynamoDB 当：
  1. _________________
  2. _________________
  3. _________________

- 用 Aurora 当：
  1. _________________
  2. _________________
  3. _________________

---

## 🌐 AWS Networking 分层设计

```
第 4 层：应用层服务发现
    ↑ Route 53 (DNS) ← B5
    
第 3 层：多 VPC 互联
    ↑ Transit Gateway (hub-spoke) ← B4
    
第 2 层：子网隔离和安全
    ↑ VPC, Security Group, NACL ← B1, B3
    
第 1 层：单 VPC 网络设计
    ↑ Public/Private Subnet, IGW, NAT ← B1, B2
```

**你的理解**：
这个分层设计的目的是：
_________________

---

## 💡 与分布式系统的联系

### CAP Theorem 应用

**DynamoDB**：
- 选择：_______
- 原因：_________________

**Aurora**：
- 选择：_______
- 原因：_________________

### 分布式系统原则

1. **Locality（数据本地性）**
   - 如何应用在 DynamoDB？_________________
   - 如何应用在 VPC 网络设计？_________________

2. **Replication（复制）**
   - DynamoDB 的复制策略：_________________
   - Aurora 的复制策略：_________________

3. **Consistency Model（一致性模型）**
   - DynamoDB 是什么模式？_________________
   - Aurora 是什么模式？_________________
   - 为什么选择不同？_________________

---

## 🔧 实践中学到的最有价值的东西

### 最大的惊喜
_________________

### 最大的挑战
_________________

### 改进的地方
_________________

### 下次会做的不同的事
_________________

---

## 📈 费用总结

| 项目 | 预计费用 | 实际费用 | 笔记 |
|------|---------|---------|------|
| DynamoDB | $0-0.50 | _______ | _______ |
| Aurora | $0-1.00 | _______ | _______ |
| VPC/EC2 | $0-1.00 | _______ | _______ |
| NAT Gateway | _______ | _______ | 最容易超支！ |
| Route 53 | $0-0.50 | _______ | _______ |
| **总计** | **< $3** | _______ | _______ |

**学到的费用管理教训**：
1. _________________
2. _________________
3. _________________

---

## 🎓 与 Mac 老师讨论的要点

看完 Mac 老师的 `dynamodb_modeler-project` 后，你想讨论的话题：

1. **Single-Table Design**
   - 问题：_________________
   - 潜在的应用：_________________

2. **Key Design 的重要性**
   - 观察：_________________
   - 后续改进：_________________

3. **DynamoDB 在企业中的应用**
   - 问题：_________________
   - 你的理解：_________________

---

## 📚 推荐的后续学习

### 深入 DynamoDB
- [ ] 学习 Global Secondary Index (GSI) 和 Local Secondary Index (LSI)
- [ ] 理解 Hot Partition 问题和解决方案
- [ ] 学习 DynamoDB Streams 和 Lambda 集成
- [ ] 研究 Time-series 数据在 DynamoDB 的建模

### 深入 AWS Networking
- [ ] 实践 VPC Flow Logs 和网络故障排查
- [ ] 学习 AWS Network Firewall
- [ ] 理解 AWS Direct Connect 和混合云架构
- [ ] 学习 AWS Organizations 的多账户网络设计

### 扩展到 Kubernetes
- [ ] 学习 Kubernetes 网络模型（Flannel, Calico）
- [ ] 理解 Service Mesh（Istio, Linkerd）
- [ ] 实践 EKS（Elastic Kubernetes Service）

---

## 🏆 项目成就

**你已经完成了**：

- [x] 理解了两种主要的分布式数据库范式
- [x] 实践了云基础设施的网络设计
- [x] 学会了用代码操作 AWS 服务
- [x] 理解了 enterprise-grade 网络架构
- [x] 深化了对分布式系统 trade-off 的认识

---

## 📝 最终的话

### 这 8 小时对你的意义

_________________

_________________

_________________

### 下一步行动

1. _________________
2. _________________
3. _________________

### 感谢的对象
- Mac 老师：_________________
- AWS 文档：_________________
- 你自己：_________________

---

**签名**：_________________ **日期**：_________________

