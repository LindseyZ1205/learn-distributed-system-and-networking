# AWS 一日 Hands-on 指南：DynamoDB + Aurora & Networking

> **原则：80/20 法则，一天完成，只抓核心。**
> **预计总时间：~8 小时 | 预计费用：< $5**

---

## Track A：DynamoDB + Aurora（分布式数据库的两种哲学）

预计时间：~4.5 小时

---

### A1 · Create DynamoDB table + CRUD（30 min）

`hands-on` `core`

在 AWS Console 创建一张 table，手动 put / get / query item，感受 key-value 模型。

```
Table name: MusicLibrary
Partition key: artist (String)
Sort key: song_title (String)

→ Create table → Items tab → Create item
→ 手动加 3-5 条数据 → 用 Query 按 artist 查询
```

> **为什么做这一步：** DynamoDB 的核心是 partition key 决定数据分布。这一步让你直觉感受"没有 JOIN，只能按 key 查"的 trade-off。

- [ ] 完成

---

### A2 · Python boto3 script 操作 DynamoDB（45 min）

`hands-on`

用代码做 put_item / get_item / query / scan，体验 SDK 交互。

```
pip install boto3
# create_table / put_item / get_item / query
# 重点：感受 KeyConditionExpression 的写法
# 试一下 scan vs query 的区别（scan 是全表扫描，慢且贵）
```

> **为什么做这一步：** Mac老师的 dynamodb_modeler-project 就是用 Python 建模的。这一步是你后续跟他讨论的基础。

- [ ] 完成

---

### A3 · 理解 single-table design（看 Mac老师的 repo）（30 min）

`theory` `core`

浏览 github.com/MacHu-GWU/dynamodb_modeler-project，理解为什么 DynamoDB 推荐把多种 entity 放进同一张 table。

> **为什么做这一步：** Single-table design 是 DynamoDB 最反直觉也最重要的 pattern。理解它 = 理解了 NoSQL 的核心思维。这也是你跟 Mac老师讨论时最有价值的话题。

- [ ] 完成

---

### A4 · Create Aurora cluster + SQL 操作（45 min）

`hands-on` `core`

在 RDS Console 创建 Aurora Serverless v2（省钱），连接后跑几条 SQL。

```
RDS → Create database → Aurora (PostgreSQL-compatible)
→ Serverless v2 → 最小 ACU = 0.5
→ 用 RDS Query Editor 连接（免费，不需要 EC2）
→ CREATE TABLE, INSERT, SELECT, JOIN
```

> **为什么做这一步：** Aurora 保留了完整的 SQL 能力（JOIN, transaction, 复杂 query），但底层 storage 是分布式的。跟 A1 对比：同样是数据库，设计哲学完全不同。

- [ ] 完成

---

### A5 · Aurora 架构核心概念（30 min）

`theory`

理解 storage-compute 分离、6 copies across 3 AZs、read replica share storage。

> **为什么做这一步：** 这是 Aurora 相对传统 RDS 的核心创新。能讲出"Aurora 的 storage layer 是独立的分布式系统，compute 只发 redo log 给 storage node"就够了。

- [ ] 完成

---

### A6 · DynamoDB vs Aurora 对比总结（30 min）

`theory` `core`

写出自己的对比笔记：什么场景用哪个？trade-off 是什么？

对比维度参考：data model, scalability, consistency, cost, 适用场景，联系 CAP theorem。

> **为什么做这一步：** 这就是 Mac老师说的"经典分布式成功案例"的核心。能讲清楚 trade-off = 面试和技术讨论的硬通货。

- [ ] 完成

---

## Track B：VPC + Transit Gateway + Route 53（AWS networking 三层递进）

预计时间：~3.5 小时

---

### B1 · 手动搭建 VPC：public + private subnet（45 min）

`hands-on` `core`

从零创建 VPC，配置 public / private subnet、Internet Gateway、NAT Gateway、route table。

```
VPC Console → Create VPC (10.0.0.0/16)
→ Create subnet: public (10.0.1.0/24), private (10.0.2.0/24)
→ Create Internet Gateway → attach to VPC
→ Public route table: 0.0.0.0/0 → IGW
→ (Optional) NAT Gateway in public subnet
→ Private route table: 0.0.0.0/0 → NAT GW
```

> **为什么做这一步：** VPC 是 AWS networking 的地基。Quick Suite 的所有 backend service 都跑在某个 VPC 的 subnet 里。这一步让你理解"public 能被外部访问，private 只能出不能进"。

- [ ] 完成

---

### B2 · 在 VPC 里启动 EC2 验证网络（30 min）

`hands-on`

在 public subnet 和 private subnet 各放一个 EC2，验证连通性。

```
EC2 → Launch (t2.micro free tier)
→ Public subnet 的 EC2：assign public IP → SSH 进去 → curl google.com ✓
→ Private subnet 的 EC2：no public IP → 通过 public EC2 SSH 跳板进入
→ 验证 private EC2 能通过 NAT 访问外网，但外部不能直接访问它
```

> **为什么做这一步：** 没有比"SSH 进去 ping 一下"更直觉的方式来理解 public vs private subnet 了。

- [ ] 完成

---

### B3 · Security Group + NACL 规则（30 min）

`hands-on`

配置 Security Group 只允许 SSH (22) 和 HTTP (80)，理解 stateful vs stateless。

> **为什么做这一步：** Security Group 是 instance 级别的 firewall（stateful），NACL 是 subnet 级别的（stateless）。实际工作中 90% 的 networking 问题都跟 SG 规则有关。

- [ ] 完成

---

### B4 · Transit Gateway 概念理解（20 min）

`theory`

不需要 hands-on（需要多个 VPC，成本高）。理解它解决的问题和 hub-spoke 模型就够了。

> **为什么做这一步：** 企业环境里 VPC 数量很多，Transit Gateway 是中心 hub。你 intern 的 team 大概率用到了它。理解概念 > 亲手搭建。

- [ ] 完成

---

### B5 · Route 53 DNS 基础（30 min）

`hands-on`

在 Route 53 创建一个 private hosted zone，给你 VPC 里的 EC2 配一个内部域名。

```
Route 53 → Hosted zones → Create (private, associate with your VPC)
→ Create A record: myserver.internal → EC2 private IP
→ SSH 到 EC2 → ping myserver.internal → 验证 resolve
```

> **为什么做这一步：** DNS 是 networking 最基础的概念。Private hosted zone 是企业内部 service discovery 的常用手段，不需要花钱买域名就能练。

- [ ] 完成

---

### B6 · 清理资源！（15 min）

`core`

删除所有创建的资源，避免产生费用。

```
顺序：EC2 instances → NAT Gateway → Elastic IP
→ Route 53 records → Hosted Zone
→ Aurora cluster → DynamoDB table
→ Subnets → Route Tables → IGW → VPC
```

> **为什么做这一步：** NAT Gateway 按小时计费（~$0.045/hr），Aurora Serverless 停了也可能有 storage 费。一定要清理。

- [ ] 完成
