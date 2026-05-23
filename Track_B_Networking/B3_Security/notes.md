# B3：Security Group 和 NACL 规则

## 学习目标
- 理解 AWS 的两层防火墙：Security Group（有状态）和 NACL（无状态）
- 实际配置 SG 规则，体验 stateful firewall 的概念
- 了解 AWS 默认安全最佳实践

## 费用
- 免费（仅配置规则，无额外费用）

## 关键概念

### Security Group（实例级防火墙）
```
特点：
  ✓ Stateful（有状态）
  ✓ 默认 deny all inbound（白名单制）
  ✓ 默认 allow all outbound（黑名单制）
  
工作原理：
  入站流量：
    检查 SG 规则 → 如果允许 → 通过
    返回流量（即使 rule 删除）：仍然通过（stateful）
  
  出站流量：
    检查 SG 规则 → 默认全部允许（outbound rule）
```

### NACL（Network ACL，子网级防火墙）
```
特点：
  ✗ Stateless（无状态）
  ✓ 顺序处理规则（从小到大）
  ✓ 有明确的 rule number 和 priority
  
工作原理：
  入站流量：检查所有规则，第一个匹配即停止
  出站流量：同样逐个检查
  
  返回流量不会自动通过 → 需要明确的出站规则！
```

### 对比

| 特性 | SG | NACL |
|------|----|----|
| 作用范围 | 实例 | 子网 |
| 有状态 | ✓ | ✗ |
| 默认规则 | Deny inbound, Allow outbound | Deny all |
| 性能 | 快 | 较慢（逐个检查） |
| 规则匹配 | 允许or拒绝 | 允许or拒绝，有 priority |
| 复杂性 | 简单 | 复杂 |
| 典型用途 | 大多数场景 | 子网间隔离 |

## 操作步骤

### 1. Security Group 规则管理（从 B2）

查看你创建的 security groups：
```
EC2 Console → Security Groups
```

观察：
- [ ] public-ec2 的 SG：
  - Inbound：SSH (22) from 0.0.0.0/0
  - Outbound：All traffic to 0.0.0.0/0
  
- [ ] private-ec2 的 SG：
  - Inbound：SSH (22) from <public-ec2-sg>
  - Outbound：All traffic to 0.0.0.0/0

### 2. 测试 Stateful 特性

```bash
# 场景：在 public-ec2 上，SSH 进 private-ec2
ssh -i key.pem ec2-user@10.0.2.100

# 即使你删除了 SSH inbound rule，已建立的连接仍然有效
# 这就是 stateful 防火墙的特性
```

### 3. 配置 NACL（可选练习）

如果想深入了解 NACL：
```
VPC Console → Network ACLs → (选 public subnet 的 NACL)
```

观察默认规则：
```
Inbound:
  Rule 100: ALL traffic from 10.0.0.0/16 (VPC 内) → ALLOW
  Rule 32767: ALL traffic from 0.0.0.0/0 → DENY（默认）

Outbound:
  Rule 100: ALL traffic to 10.0.0.0/16 → ALLOW
  Rule 32767: ALL traffic to 0.0.0.0/0 → DENY
```

添加 SSH 规则（如果当前 NACL 太严格）：
```
Inbound rule:
  Rule number: 110
  Type: SSH (22)
  Protocol: TCP
  Port: 22
  CIDR: 0.0.0.0/0
  Action: ALLOW
```

### 4. 最佳实践检查

在生产环境中：
- [ ] Security Group 应该按最小权限原则：只开放必要端口
- [ ] 不应该 allow all (0.0.0.0/0) to critical ports（除了 HTTP/HTTPS）
- [ ] 应该按 service role 分组（例如 web-sg, db-sg, cache-sg）
- [ ] NACL 通常保持默认（allow VPC 内 + internet）

## 常见规则模式

### Web 服务器 SG
```
Inbound:
  HTTP (80) from 0.0.0.0/0
  HTTPS (443) from 0.0.0.0/0
  SSH (22) from 203.0.113.0/24  ← 仅允许你的办公网络
Outbound:
  All traffic to 0.0.0.0/0
```

### 数据库 SG
```
Inbound:
  MySQL (3306) from web-server-sg  ← 仅允许 web 层
  (不允许任何其他流量)
Outbound:
  None（或仅允许必要出站）
```

### Jump Host / Bastion SG
```
Inbound:
  SSH (22) from 0.0.0.0/0  ← public-facing
  (没有其他 inbound)
Outbound:
  SSH (22) to web-server-sg, db-sg  ← 能进入内部
  (没有互联网访问)
```

## 思考题

### 问题 1：Stateful vs Stateless
```
场景：我在 public-ec2 上 SSH 到 private-ec2，传输文件

Private-ec2 的 NACL：
  Inbound: SSH (22) ALLOW
  Outbound: ALL DENY  ← 问题！

会发生什么？
  SSH 连接建立 ✓（SCP 初始 SSH）
  然后？Stateless NACL 不知道这是"回复"
  必须显式加 outbound rule → ALLOW high ephemeral ports (1024-65535)
  
有了 Stateful SG：
  inbound SSH ALLOW ✓
  outbound 自动知道这是"回复" → ALLOW
  无需显式配置
```

### 问题 2：Security Group 的 All traffic 规则
```
出站 rule：All traffic to 0.0.0.0/0（默认）

这是否安全？
  通常可以，因为：
    1. 入站经过严格过滤
    2. 出站对内部威胁较小（但可能会泄露数据）
  
生产建议：
    配置显式出站规则（如 DNS, HTTPS 到 API, DB port 等）
    避免默认的 All outbound
```

## 完成标志
- [ ] 理解 Security Group 的 stateful 特性
- [ ] 理解 NACL 的 stateless 和 rule priority
- [ ] 观察了你创建的 EC2 的 SG 规则
- [ ] 理解了 ingress vs egress（inbound vs outbound）
- [ ] 回答了 2 个思考题
- [ ] 知道生产环境中的最佳实践

## 笔记空间

### Stateful vs Stateless 防火墙的区别
（用一个例子解释...）

### 为什么 SG 是最常用的，而 NACL 很少配置？
（分析复杂度和实用性...）

### 你会如何给一个数据库实例配置 SG？
（设计一个现实的规则...）
