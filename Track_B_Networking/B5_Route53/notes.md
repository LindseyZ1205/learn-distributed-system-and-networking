# B5：Route 53 DNS 和 Private Hosted Zone

## 学习目标
- 理解 DNS 的基本概念（A record, CNAME, etc.）
- 设置 Route 53 private hosted zone 用于内部服务发现
- 实践：给 VPC 内的 EC2 配置内部域名

## 费用
- **Private hosted zone**：$0.50/月（便宜！）
- **查询（DNS requests）**：前 100 万次 $0.40/月，之后线性增长
- 总体：$0.50-1.00/月（非常便宜）

## 关键概念

### DNS 101
```
DNS 的作用：域名 ↔ IP 地址 的映射

例如：
  google.com → 142.250.80.46
  
DNS 记录类型：
  A       - IPv4 地址 (example.com → 1.2.3.4)
  AAAA    - IPv6 地址 (example.com → 2001:db8::1)
  CNAME   - 别名 (www.example.com → example.com)
  MX      - 邮件服务器 (example.com → mail.example.com)
  NS      - 名字服务器（域名服务器本身）
  PTR     - 反向查询 (1.2.3.4 → example.com)
```

### Public vs Private Hosted Zone

| 特性 | Public | Private |
|------|--------|---------|
| 可见范围 | 互联网全球 | 仅 VPC 内 |
| 用途 | 公网域名（example.com） | 内部服务发现 |
| 示例 | www.google.com | mydb.internal |
| 需要购买域名 | ✓ | ✗ |
| 常见场景 | 企业官网、API | 微服务、内部工具 |

### Private Hosted Zone 的工作原理
```
VPC 内的 EC2 查询 DNS：
  1. EC2: `nslookup myserver.internal`
  2. → DNS resolver（AWS 提供，地址 169.254.169.253）
  3. → Route 53 private hosted zone
  4. → 返回 10.0.1.100 (myserver 在 VPC 内的 IP)
  5. ← EC2 与 myserver 通信

关键：私有 zone 只在关联的 VPC 内可见
VPC 外的机器无法查询 myserver.internal
```

## 操作步骤

### 1. 创建 Private Hosted Zone
- [ ] Route 53 Console → Hosted zones → Create hosted zone
  ```
  Domain name: internal  ← 注意：不是真实域名
  Type: Private hosted zone
  Associate with VPC: learning-vpc (从 B1 创建的)
  ```
- [ ] 点 Create

### 2. 创建 A Record（映射 EC2 IP）
- [ ] 进入刚创建的 hosted zone
- [ ] Create record
  ```
  Record name: myserver
  Type: A
  Value: 10.0.1.100  ← public-ec2 的 private IP
  TTL: 300  ← 5 分钟缓存
  ```
- [ ] 点 Create
- [ ] 继续创建第二条：
  ```
  Record name: db-server
  Type: A
  Value: 10.0.2.100  ← private-ec2 的 private IP
  ```

### 3. 验证 DNS 解析（从 EC2 内部）

```bash
# SSH 进 public-ec2
ssh -i key.pem ec2-user@<public-ip>

# 测试 DNS 解析
nslookup myserver.internal
# 应该返回 10.0.1.100

nslookup db-server.internal
# 应该返回 10.0.2.100

# 或用 ping
ping myserver.internal
# 应该能 ping 通
```

### 4. 创建 CNAME（别名）

在同一个 hosted zone 中：
```
Record name: api
Type: CNAME
Value: myserver.internal  ← 指向另一个记录
```

验证：
```bash
nslookup api.internal
# → myserver.internal (CNAME)
# → 10.0.1.100 (A record)
```

## 现实应用

### 场景 1：微服务发现
```
Microservices:
  - user-service.internal → 10.0.1.50
  - order-service.internal → 10.0.1.51
  - payment-service.internal → 10.0.1.52

Application code:
  user_host = "user-service.internal"
  requests.get(f"http://{user_host}/api/user/123")
  
优点：
  - 无需在代码里写 IP
  - 可以轻松切换服务器 IP（只改 DNS record）
  - 支持负载均衡（多个 IP 对应同一域名）
```

### 场景 2：Database 访问
```
在 B4 创建的 Aurora cluster 自动有了 endpoint：
  music-db.c9akciq32.us-east-1.rds.amazonaws.com
  
可以在 Route 53 中简化：
  db.internal → music-db.c9akciq32.us-east-1.rds.amazonaws.com (CNAME)
  
应用连接：
  host = "db.internal"  ← 简短易记
```

### 场景 3：跨 VPC 服务发现
```
Private Hosted Zone 可以关联多个 VPC
  VPC-1, VPC-2, VPC-3 都可以查询 internal zone
  
这样：
  VPC-1 的 web → 查询 db-server.internal → 得到 VPC-2 的 DB IP
  自动跨 VPC 通信！
  
需要配合：Transit Gateway（B4 概念）
```

## DNS 记录最佳实践

### A Record（最常用）
```
myserver.internal → 10.0.1.100

支持加权路由（Weighted routing policy）：
  myserver.internal → 10.0.1.100 (weight 70%)
  myserver.internal → 10.0.1.101 (weight 30%)
  
查询时，Route 53 按权重返回 IP（实现负载均衡）
```

### CNAME（别名）
```
api.internal → myserver.internal

注意：
  ✓ 可以指向同 zone 的其他记录
  ✓ 可以指向 Route 53 之外的域名（如外部 API）
  ✗ 不能在 zone apex（internal）上使用 CNAME
  
zone apex 应该用 A record 或 alias record
```

### Alias Record（AWS 特有）
```
mysite.internal → <ELB endpoint>

特点：
  ✓ 类似 CNAME，但不占用 DNS 查询次数（免费）
  ✓ 可以在 zone apex 使用
  ✓ 自动健康检查
```

## 思考题

### 问题 1：为什么应用应该使用 DNS 而不是硬编码 IP？
```
IP 硬编码的问题：
  1. 无法灵活切换服务器
  2. 负载均衡困难（需要改代码）
  3. 宕机转移需要重新部署

DNS 的优势：
  1. 改个 record，所有应用自动生效
  2. 支持多 IP 的负载均衡
  3. 宕机可以快速切换（改 DNS TTL 和 record）
```

### 问题 2：TTL (Time To Live) 有什么作用？
```
TTL = 300 (5 分钟)
  
客户端缓存：
  查询一次 myserver.internal → 得到 10.0.1.100
  后续 5 分钟内再查，不请求 DNS，直接用缓存
  5 分钟后缓存过期，重新查询
  
作用：
  ✓ 降低 DNS 查询负担
  ✓ 加快应用响应（本地缓存）
  
权衡：
  TTL 太长 → 改 IP 后需要等待生效
  TTL 太短 → 频繁 DNS 查询，性能下降
  
常见策略：
  稳定服务：TTL = 3600 (1 小时)
  经常变化：TTL = 300 (5 分钟)
  需要快速切换：TTL = 60
```

### 问题 3：Route 53 和 Kubernetes DNS 的区别？
```
Route 53（AWS DNS）：
  - 跨 VPC、跨账户
  - 支持负载均衡、故障转移
  - 需要 Route 53 服务

Kubernetes DNS（如 CoreDNS）：
  - 仅在集群内
  - 自动服务发现（基于标签）
  - 随 Kubernetes 自带

现实中：
  K8s 集群在 VPC 内
  应该用 K8s DNS for internal services
  用 Route 53 for external endpoints 或跨 K8s 集群
```

## 完成标志
- [ ] 创建了 private hosted zone（internal）
- [ ] 创建了至少 2 个 A record（指向 EC2）
- [ ] 从 EC2 内部成功用 nslookup 查询
- [ ] 创建了至少 1 个 CNAME record
- [ ] 理解了 A record / CNAME / Alias 的区别
- [ ] 理解了 TTL 的作用
- [ ] 知道什么场景用 private hosted zone

## 笔记空间

### Private Hosted Zone 的价值
（记录为什么应用应该用内部域名...）

### DNS 在微服务中的作用
（分析服务发现的重要性...）

### 你会如何设计一个 3 层应用的 DNS 结构？
（设计 web, app, db 的域名...）
