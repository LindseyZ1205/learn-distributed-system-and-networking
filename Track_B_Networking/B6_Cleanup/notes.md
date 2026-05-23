# B6：清理资源

## 学习目标
- 学会正确清理 AWS 资源，避免持续扣费
- 理解资源间的依赖关系（删除顺序很重要）

## 重要提示 ⚠️
按照指定顺序删除！否则会出错。

## 删除顺序和检查清单

### 第 1 步：停止 EC2 实例
```
EC2 Console → Instances
  - [ ] 选择 public-ec2
  - [ ] Instance State → Terminate
  - [ ] 确认删除
  
  - [ ] 选择 private-ec2
  - [ ] Instance State → Terminate
  - [ ] 确认删除
  
等待：~1-2 分钟
```

### 第 2 步：删除 NAT Gateway（最重要！）
```
VPC Console → NAT Gateways
  - [ ] 选择你创建的 NAT Gateway
  - [ ] Actions → Delete NAT Gateway
  - [ ] 确认删除（会提示需要释放关联的 Elastic IP）

等待：~1 分钟

⚠️ 关键：NAT 是费用陷阱！
如果在这一步之前已经花费了 N 小时的费用，
现在删除它可以停止后续费用。
```

### 第 3 步：释放 Elastic IP
```
VPC Console → Elastic IPs
  - [ ] 如果有未关联的 Elastic IP（来自被删除的 NAT）
  - [ ] 选中 → Release address
  - [ ] 确认

（如果 NAT 删除后 IP 自动释放了，这一步可跳过）
```

### 第 4 步：删除 Route 53 记录和 Hosted Zone

先删除记录：
```
Route 53 Console → Hosted zones → internal
  - [ ] 删除你创建的 A record (myserver, db-server, etc.)
  - [ ] 删除你创建的 CNAME record
  
  注意：自动生成的 NS 和 SOA record 无法删除（允许）
```

然后删除 Hosted Zone：
```
Route 53 Console → Hosted zones
  - [ ] 选择 internal zone
  - [ ] Delete hosted zone
  - [ ] 确认
  
（如果删除失败，说明还有其他 record，检查 DNS 记录）
```

### 第 5 步：删除 VPC（最后一步）

VPC 包含：subnets, route tables, IGW, NACL 等

```
VPC Console → Your VPCs
  - [ ] 选择 learning-vpc
  - [ ] Actions → Delete VPC
  
AWS 会自动删除关联的：
  - [ ] Subnets (public-subnet-1a, private-subnet-1b)
  - [ ] Route Tables (public-rt, private-rt)
  - [ ] Internet Gateway (learning-igw)
  - [ ] NACL
  - [ ] Security Groups（除了默认的）
  
这是个原子操作 → 一次删除所有依赖资源
```

如果删除失败，可能是某些资源还有依赖：
```
常见原因：
  1. EC2 还在运行 → 先停止 EC2
  2. ENI（Elastic Network Interface）还在使用 → 手动删除
  3. VPC endpoint 还在 → 手动删除
```

## 删除后验证

```bash
# 检查 VPC 是否已删除
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=learning-vpc"
# 应该返回空列表

# 检查 NAT 是否已删除
aws ec2 describe-nat-gateways --filter "Name=tag:Name,Values=learning-nat"
# 应该返回空列表

# 检查 Route 53 zone 是否已删除
aws route53 list-hosted-zones-by-name
# 应该没有 internal zone
```

## 费用验证

在 AWS Billing Dashboard 检查：
```
Billing Dashboard → Estimated charges
  查看：
    - EC2：应该降到 $0（t2.micro 停用了）
    - RDS：应该没有（Aurora cluster 已删除）
    - NAT Gateway：应该没有（已删除）
    - Route 53：应该没有（hosted zone 已删除）
    - VPC 本身：免费，无需担心
```

通常清理后，24 小时内 estimated charges 会降到接近 $0。

## 常见问题

### Q1：删除 VPC 时出错 "has dependencies"
```
A: 检查是否有：
  1. ENI 还在使用 → aws ec2 describe-network-interfaces
  2. 安全组有循环引用 → 删除循环引用后再试
  3. VPC endpoint → 手动删除
```

### Q2：NAT Gateway 删除后还有费用？
```
A: 可能原因：
  1. Elastic IP 还没释放 → Route 53 Console 释放
  2. 服务器还没完全停止 → 等待 1-2 分钟
  3. 费用是前小时的 → 新小时没有了
```

### Q3：Route 53 zone 删除不了？
```
A: 原因：zone 中还有非默认 record
  1. Delete all A/CNAME/MX records
  2. Keep NS and SOA (系统自动)
  3. Then delete zone
```

## 学习总结

你已经完成了 8 小时的学习：

**Track A - DynamoDB & Aurora**
- [ ] 理解了 key-value vs 关系型数据库
- [ ] 理解了分布式数据库的 trade-off
- [ ] 学到了 single-table design 的概念
- [ ] 体验了 DynamoDB 和 Aurora 的优缺点

**Track B - VPC & Networking**
- [ ] 理解了 VPC 的网络设计
- [ ] 理解了 public/private subnet 的区别
- [ ] 体验了 EC2 在不同 subnet 的行为
- [ ] 学到了 security group 和 NACL
- [ ] 理解了企业级网络设计（TGW）
- [ ] 实践了 DNS 和服务发现

## 完成标志
- [ ] 按顺序删除了所有资源
- [ ] 验证了费用已停止
- [ ] 理解了为什么删除顺序很重要

## 费用总结

```
预期实际费用：< $3

分布：
  DynamoDB: $0-0.50
  Aurora: $0-1.00（最贵）
  VPC/EC2/NAT: $0-1.00
  Route 53: $0-0.50
  
如果发现实际费用超过 $5：
  1. 检查是否有资源没完全删除
  2. 查看 Cost Explorer 详细分析
  3. 联系 AWS Support（有时可以申请返还）
```

## 下一步

清理完成后，你已经完成了这个 learning project！

建议：
1. 写一份最终的学习总结（见 learning_notes/final_summary.md）
2. 分享学习笔记给 Mac 老师，他会欣赏的！
3. 考虑继续学习：
   - Kubernetes（容器编排）
   - Advanced DynamoDB patterns
   - AWS SAA (Solutions Architect Associate) certification
