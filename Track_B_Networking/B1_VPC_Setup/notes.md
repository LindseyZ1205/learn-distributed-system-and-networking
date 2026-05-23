# B1：手动配置 VPC、Subnet、Internet Gateway、NAT Gateway、Route Table

## 学习目标
- 理解 VPC 的核心概念：public / private subnet 的区别
- 手动配置网络基础设施，感受 AWS 网络的分层设计
- 为后续 EC2、Route 53 打基础

## 费用提醒 ⚠️
- **VPC 本身**：免费
- **Internet Gateway**：免费
- **NAT Gateway** ⚠️：$0.045/小时（这是费用陷阱！）
- **Elastic IP**（NAT 使用）：如果不用每月 $0.005，用中 $0.045/小时
- **建议**：完成测试后立即删除 NAT Gateway，防止持续扣费

## 关键概念

### VPC、Subnet、AZ 的关系
```
AWS Region (例如 us-east-1)
│
├─ AZ-1a
│  └─ Subnet-1 (10.0.1.0/24) ← VPC 内的子网
│
├─ AZ-1b
│  └─ Subnet-2 (10.0.2.0/24) ← 另一个 AZ 的子网
│
└─ Internet Gateway（连接 VPC 与互联网）
```

### Public vs Private Subnet
| 特性 | Public | Private |
|------|--------|---------|
| 可分配 Public IP | ✓ | ✗ |
| 可访问互联网 | ✓ 直接 | ✓ 通过 NAT |
| 外部可访问 | ✓ | ✗ |
| 用途 | Web 服务器 | 数据库、内部服务 |
| 最小化安全风险 | ✗ | ✓ |

## 操作步骤

### 1. 创建 VPC
- [ ] VPC Console → Create VPC
- [ ] VPC settings:
  ```
  Name: learning-vpc
  CIDR block: 10.0.0.0/16  ← 可容纳 65536 IP
  ```

### 2. 创建 Subnet（Public）
- [ ] 在 learning-vpc 中创建子网
- [ ] Public Subnet:
  ```
  Name: public-subnet-1a
  Availability Zone: (选一个，如 us-east-1a)
  CIDR block: 10.0.1.0/24  ← 该子网 256 个 IP
  ```
- [ ] 标记为 public：
  - Subnet settings → "Enable auto-assign public IPv4 address"

### 3. 创建 Subnet（Private）
- [ ] Private Subnet:
  ```
  Name: private-subnet-1b
  Availability Zone: (选另一个 AZ，如 us-east-1b)
  CIDR block: 10.0.2.0/24
  ```

### 4. 创建 Internet Gateway
- [ ] VPC → Internet Gateways → Create IGW
- [ ] Name: learning-igw
- [ ] Attach to VPC: learning-vpc

### 5. 配置 Route Table（Public）
- [ ] Create Route Table:
  ```
  Name: public-rt
  VPC: learning-vpc
  ```
- [ ] 添加路由：
  ```
  Destination: 0.0.0.0/0（所有流量）
  Target: Internet Gateway → learning-igw
  ```
- [ ] 关联子网：public-subnet-1a → public-rt

### 6. 创建 NAT Gateway（可选，费用贵）
- [ ] 如果要让 private subnet 也能出网，创建 NAT Gateway：
  ```
  Subnet: public-subnet-1a  ← NAT 必须在 public subnet
  Elastic IP: Allocate new
  ```
- [ ] ⚠️ 记住：NAT 用完后要立即删除

### 7. 配置 Route Table（Private）
- [ ] Create Route Table:
  ```
  Name: private-rt
  VPC: learning-vpc
  ```
- [ ] 如果创建了 NAT，添加路由：
  ```
  Destination: 0.0.0.0/0
  Target: NAT Gateway → (选刚创建的 NAT)
  ```
- [ ] 关联子网：private-subnet-1b → private-rt

## 验证配置

打开 AWS Console 检查：
```
VPC Console → Your VPCs
  learning-vpc ✓
  
  Subnets
    public-subnet-1a (10.0.1.0/24) ✓
    private-subnet-1b (10.0.2.0/24) ✓
  
  Internet Gateways
    learning-igw ✓ (attached to learning-vpc)
  
  NAT Gateways
    learning-nat (in public-subnet-1a) ✓
  
  Route Tables
    public-rt: 0.0.0.0/0 → IGW ✓
    private-rt: 0.0.0.0/0 → NAT ✓
```

## 关键概念补充

### CIDR 表示法
```
10.0.0.0/16   = 从 10.0.0.0 到 10.0.255.255（65536 个 IP）
10.0.1.0/24   = 从 10.0.1.0 到 10.0.1.255（256 个 IP）
10.0.1.0/25   = 从 10.0.1.0 到 10.0.1.127（128 个 IP）

后面的数字 = 掩码，越大子网越小
/32 = 1 个 IP（主机路由）
/24 = 256 个 IP（常见子网）
/16 = 65536 个 IP（整个 VPC）
```

### Route Table 的匹配规则
```
Route Table:
  0.0.0.0/0 → IGW（所有流量都去 IGW）
  10.0.0.0/16 → local（同 VPC 内流量本地处理）

查询流程：
  发送给 10.0.5.1（VPC 内）→ local → 直接 L2 转发
  发送给 8.8.8.8（互联网）→ 0.0.0.0/0 → IGW → 互联网
```

## 完成标志
- [ ] 创建了 VPC (10.0.0.0/16)
- [ ] 创建了 public subnet (10.0.1.0/24) 和 private subnet (10.0.2.0/24)
- [ ] 创建了 Internet Gateway 并 attach 到 VPC
- [ ] 配置了 public route table (0.0.0.0/0 → IGW)
- [ ] 配置了 private route table (0.0.0.0/0 → NAT，可选)
- [ ] 理解了 CIDR、public/private 的区别

## 笔记空间

### VPC 的网络设计思想
（记录为什么要分 public/private subnet...）

### Route Table 的工作原理
（理解数据包如何通过 route table 路由...）

### 费用陷阱
（记住 NAT Gateway 的按小时计费...）
