# B4：Transit Gateway 概念理解

## 学习目标
- 理解多 VPC 场景下的网络设计问题
- 学习 Transit Gateway 如何解决这个问题
- 了解企业网络的 hub-spoke 架构

## 费用
- 本任务不涉及实际部署，仅理论学习
- 注：如果真的部署 TGW，需要 $0.05/小时 + 数据处理费

## 背景问题

### 情景 1：多个 VPC 需要通信
```
公司有 3 个 VPC：
  - Production VPC (应用服务)
  - Database VPC (RDS Aurora)
  - Development VPC (开发环境)

需求：
  - Production 需要访问 Database 的 RDS
  - Development 需要访问 Database 的测试 RDS
  - Production 和 Development 相互隔离（安全）
  
最坏方案（VPC Peering）：
  Production ←→ Database      (3 个连接)
  Production ←→ Development
  Development ←→ Database
  
  问题：O(n²) 连接数，每个 peering 都要手动配置 route table
```

### 情景 2：混合云（On-premise + AWS）
```
公司网络：
  办公网络（On-premise，10.0.0.0/8）
  AWS VPC-1 （10.10.0.0/16）
  AWS VPC-2 （10.20.0.0/16）
  
所有网络需要互通，但不希望办公网络能直接访问 VPC-2

VPC Peering 方案：
  ✗ VPC Peering 不支持 transitive（A-B, B-C 不意味着 A-C）
  ✗ 需要 3 条 VPN，每条都要单独管理
```

## Transit Gateway 解决方案

### 架构（Hub-Spoke）
```
          Office Network
          (10.0.0.0/8)
                ↑
                │ VPN/Direct Connect
                ↓
        ┌───────────────┐
        │ Transit       │
        │ Gateway       │  ← 中心枢纽
        │ (TGW)         │
        └───────────────┘
       ↙     ↓     ↘
    VPC-1  VPC-2  VPC-3
    (Prod) (DB)  (Dev)
```

**优势**：
- 中心化管理（O(n) 连接，而不是 O(n²)）
- Transitive routing（Office → TGW → VPC-2，自动支持）
- 更易于应用网络策略（TGW route tables）

### 关键特性

#### 1. Transit Gateway Attachment
```
每条附加线路（spoke）：
  - VPC-1 attachment（连接 VPC-1 的子网）
  - VPC-2 attachment
  - VPC-3 attachment
  - VPN attachment（连接 on-premise）
  
所有 attachment 共享同一个 TGW 资源
```

#### 2. Route Tables in TGW
```
TGW Route Table:
  Destination         Attachment
  10.10.0.0/16   →   VPC-1
  10.20.0.0/16   →   VPC-2
  10.30.0.0/16   →   VPC-3
  10.0.0.0/8     →   VPN
  
类似 VPC 的 route table，但管理多个 VPC 的流量
```

#### 3. Transitive Routing
```
示例：Office → VPC-2

1. Office 数据包到达 TGW
2. TGW 查 route table：10.20.0.0/16 → VPC-2 attachment
3. 转发给 VPC-2
4. VPC-2 回复 → TGW → Office

全程自动，不需要额外配置！
（传统 VPC Peering 需要在 VPC-1 也建立 peering）
```

## 对比

### VPC Peering vs Transit Gateway

| 特性 | VPC Peering | TGW |
|------|------------|-----|
| 连接数 | O(n²) | O(n) |
| Transitive | ✗ | ✓ |
| 混合云支持 | ✗（需要多条 VPN） | ✓（一条 VPN） |
| 跨区域 | 支持 | 支持 |
| 管理复杂度 | 高（每个 peering 独立） | 低（中央 TGW） |
| 成本（单连接） | 低 | 中 |
| 总成本（多 VPC） | 高（O(n²)） | 低（O(n)） |
| 应用场景 | 少数 VPC，简单拓扑 | 多 VPC，复杂拓扑，混合云 |

### 何时用 Transit Gateway

✓ **使用 TGW**
- 3 个以上 VPC
- 混合云（On-premise 接入）
- 需要中心化网络策略
- 企业环境（Big picture）

✓ **使用 VPC Peering**
- 只有 2 个 VPC
- 简单拓扑
- 成本敏感

## 现实案例

### 例子：SaaS 公司
```
Dev VPC           (开发，可以上网)
  ↓
TGW  ← 中心
  ↑
Prod VPC          (生产，严格隔离)
  ↑
Security VPC      (防火墙、日志、监控)
  ↑
On-prem Office    (通过 VPN)
```

**安全策略**：
- Office 只能访问 Security VPC（防火墙检查）
- Security VPC 可以访问 Prod（内部审计）
- Prod 不能访问 Dev（避免污染）
- Dev 可以访问互联网（自由开发）

## 思考题

### 问题 1：为什么不直接让所有 VPC 连接互联网？
```
原因：
  1. Security - 数据库不应该暴露
  2. Cost - NAT Gateway 很贵
  3. Compliance - 某些 VPC 可能无法出网
```

### 问题 2：如果 TGW 宕机会怎样？
```
影响范围：
  所有通过 TGW 的 VPC 间流量中断
  
解决方案：
  - 多个 TGW attachment（redundancy）
  - Cross-region TGW（灾备）
  - 或回退到 VPC Peering
```

### 问题 3：TGW 能限制流量吗？
```
可以：
  1. TGW route table 决定流向（L3 routing）
  2. Security groups in VPC 决定 inbound/outbound（L4）
  3. TGW 本身不做应用层过滤
  
细粒度控制：看 AWS Network Firewall（专门的防火墙）
```

## 与你的学习 Project 的关系

在这个 learning project 中：
- **B1, B2, B3**：单 VPC 的网络配置
- **B4（本）**：理解企业级网络设计
- **B5**：单 VPC 内的服务发现（Route 53）

在实际工作中（例如你的 intern）：
- 如果公司有多个 VPC，很可能用的就是 TGW
- 理解这个概念会帮助你更快上手

## 完成标志
- [ ] 理解 VPC Peering 的局限性
- [ ] 理解 TGW 的 hub-spoke 架构
- [ ] 理解 transitive routing 的概念
- [ ] 能比较 VPC Peering vs TGW
- [ ] 回答了 3 个思考题
- [ ] 知道什么场景用 TGW

## 笔记空间

### Hub-Spoke 架构的优势
（总结为什么这个设计更好...）

### Transitive Routing 如何工作
（用一个实例解释...）

### 为什么企业级网络多用 TGW 而不是 Peering
（从成本和管理复杂度分析...）
