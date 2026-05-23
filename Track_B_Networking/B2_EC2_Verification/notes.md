# B2：在 VPC 中部署 EC2，验证网络连通性

## 学习目标
- 在 public 和 private subnet 各启动一个 EC2 实例
- 通过 SSH 进入实例，验证网络连接
- 理解 public IP / security group / NAT 的实际作用

## 费用
- **EC2 t2.micro**：完全免费（AWS 免费层）
- **Elastic IP**（如果分配）：不用时免费，用中 $0.005/小时
- **Data transfer**：通常免费（同 AZ 或 VPC 内）

## 前置
- 完成 B1（VPC 配置）
- 有 EC2 key pair 用于 SSH
  - 如果没有：EC2 Console → Key Pairs → Create key pair

## 操作步骤

### 1. 启动 Public Subnet 的 EC2
- [ ] EC2 Console → Instances → Launch instances
  ```
  Name: public-ec2
  AMI: Amazon Linux 2 (free tier eligible)
  Instance type: t2.micro
  Network: learning-vpc
  Subnet: public-subnet-1a
  Auto-assign public IP: Enable  ← 关键！
  Security group: 新建
    - Allow SSH (port 22) from Anywhere (0.0.0.0/0)
    - Allow ICMP from Anywhere (用于 ping)
  Key pair: 选你的 key pair
  ```
- [ ] 等待 instance 启动（~1 分钟）

### 2. 启动 Private Subnet 的 EC2
- [ ] 类似上面，但改为：
  ```
  Name: private-ec2
  Subnet: private-subnet-1b
  Auto-assign public IP: Disable  ← 不需要 public IP
  Security group: 新建，允许 SSH 来自 public-ec2 的 security group
  ```

### 3. 从本地 SSH 进入 Public EC2
```bash
# 1. 下载 key pair（如果还没下载）
# 设置权限
chmod 600 ~/path/to/key.pem

# 2. SSH 进入 public EC2
ssh -i ~/path/to/key.pem ec2-user@<public-ec2-public-ip>

# 3. 验证网络
curl https://www.google.com  # 应该能访问互联网
ping 8.8.8.8                 # 应该能 ping 通
```

### 4. 从 Public EC2 SSH 进入 Private EC2（Jump Host）
```bash
# 从你的本地机器

# 方法 1：SSH ProxyJump（推荐）
ssh -i ~/path/to/key.pem \
    -J ec2-user@<public-ec2-public-ip> \
    ec2-user@<private-ec2-private-ip>

# 方法 2：手动中转
# 第一个 Terminal 中：
ssh -i ~/path/to/key.pem ec2-user@<public-ec2-public-ip>

# 第二个 Terminal 中（把 private key 复制到 public EC2）：
scp -i ~/path/to/key.pem ~/path/to/key.pem ec2-user@<public-ec2-public-ip>:~/

# 进入 public EC2 后：
ssh -i ~/key.pem ec2-user@<private-ec2-private-ip>
```

### 5. 验证 Private EC2 的网络
```bash
# 在 private EC2 上运行

# 可以出网吗？（通过 NAT Gateway）
curl https://www.google.com  # 应该能访问

# 反过来，外部能访问你吗？
# 在你的本地尝试直接 SSH 到 private-ec2（使用 private IP）
ssh -i ~/path/to/key.pem ec2-user@10.0.2.100
# 这应该会超时！因为 private IP 无法从互联网访问
```

## 文件：verify_vpc.py（可选）

如果想用 Python 验证，见 `verify_vpc.py`

## 观察和思考

### 观察 1：Public EC2 的行为
```
Public EC2：
  ✓ 有 public IP（例如 54.123.45.67）
  ✓ 可以 SSH 进去（从互联网）
  ✓ 可以访问互联网
  ✓ 外部可以访问它
```

### 观察 2：Private EC2 的行为
```
Private EC2：
  ✗ 没有 public IP
  ✓ 可以通过 jump host 进去（从 public EC2）
  ✓ 可以访问互联网（通过 NAT Gateway）
  ✗ 外部无法直接访问
  ✓ 对于数据库、内部服务很安全
```

### 观察 3：Security Group 的作用
```
Public EC2 的 SG：
  允许：SSH from 0.0.0.0/0（全世界）
  → 意味着任何 IP 都可以尝试 SSH
  → 但还需要 key pair，所以安全
  
Private EC2 的 SG：
  允许：SSH from <public-ec2-sg>（只从 public EC2）
  → 外部 IP 即使有 public IP 也进不了
  → 必须从 public EC2 跳转进入
```

### 思考题 1：为什么 Private EC2 能访问互联网？
```
路由：
  Private EC2 查看 route table → 0.0.0.0/0 → NAT Gateway
  NAT 把出站流量的源 IP 改为 NAT 的 elastic IP
  → 互联网看到的是来自 NAT 的请求，回复也发回 NAT
  NAT 再转发给 Private EC2
  
一句话：NAT 是代理，对外假扮 private EC2
```

### 思考题 2：为什么不能直接 SSH 进 Private EC2？
```
互联网 → Private EC2 的数据包：
  根本没办法路由到 private IP（10.0.2.x）
  
AWS 只在 IGW 那里分配 public IP
Private EC2 没有 public IP → 无法接收互联网流量
→ 必须从 VPC 内部（例如 public EC2）进入
```

## 完成标志
- [ ] 创建了 public-ec2 和 private-ec2
- [ ] 成功 SSH 进入 public-ec2
- [ ] 验证了 public-ec2 可以访问互联网
- [ ] 通过 jump host 进入 private-ec2
- [ ] 验证了 private-ec2 可以访问互联网（通过 NAT）
- [ ] 理解了 public/private subnet 的区别
- [ ] 理解了 security group 的作用

## 成本清理
- [ ] 删除 2 个 EC2 实例（或保留用于下一个 task）
- [ ] 删除 NAT Gateway（最优先！避免按小时计费）
- [ ] 释放 Elastic IP（如果 NAT 使用过）

## 笔记空间

### Public vs Private Subnet 的实际差异
（记录你观察到的差异...）

### NAT Gateway 的工作原理
（解释私有实例如何通过 NAT 出网...）

### Jump Host 的概念和用途
（记录为什么需要 jump host...）
