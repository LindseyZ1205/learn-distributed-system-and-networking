# 费用预算和前置准备

## AWS 费用估计

> ⚠️ **关键提示**：AWS 有 **12 个月免费额度** (EC2, DynamoDB, RDS, VPC 等都包括)。如果你还在免费期内，实际费用可能为 0。但以下是假设超出免费额度后的成本。

| 任务 | 服务 | 预期费用 | 说明 |
|------|------|---------|------|
| A1 | DynamoDB | $0-0.25 | Console 操作很快，read/write 很少 |
| A2 | DynamoDB | $0-0.50 | Python 脚本会跑多次查询，但量很小 |
| A3 | 无 | $0 | 仅理论学习，不创建资源 |
| A4 | Aurora Serverless v2 | $0-1.00 | **最贵的部分**。按 ACU-hour 计费，最小 0.5 ACU。1 小时 = ~$0.22-0.35 |
| A5 | 无 | $0 | 仅理论学习 |
| A6 | 无 | $0 | 仅写笔记 |
| **A 合计** | | **$0-2.00** | |
| B1 | VPC | $0 | VPC 本身免费；Internet Gateway 免费；NAT Gateway **$0.045/小时** ⚠️ |
| B2 | EC2 + NAT | $0-0.10 | t2.micro free tier；NAT Gateway 如果跑 1 小时 ~$0.045 |
| B3 | 无 | $0 | 仅配置，不创建新资源 |
| B4 | 无 | $0 | 理论学习 |
| B5 | Route 53 | $0-0.50 | Private hosted zone $0.50/month；A record 操作免费 |
| B6 | 无 | $0 | 仅删除资源 |
| **B 合计** | | **$0-1.00** | |
| **总计** | | **< $3.00** | 如果按时清理资源 |

---

## ⚠️ 关键费用陷阱

### 1. **NAT Gateway** ($0.045/小时 ≈ $1/天)
- 在 B1 中创建后，**一定要记得删除**
- 即使你不用它，它也在按时间计费
- **清理顺序**：删除依赖它的 EC2 → 删除 NAT Gateway → 释放 Elastic IP

### 2. **Aurora Serverless v2** (按 ACU-hour 计费)
- 最小 0.5 ACU
- 不用时 **一定要删除整个 cluster**（不是暂停）
- 删除后数据会丢失，但在这个学习项目中无所谓

### 3. **Route 53 Hosted Zone** ($0.50/月)
- 创建后立即开始计费
- 删除 records 不会停止费用，**必须删除 hosted zone 本身**

### 4. **RDS Backup** (可能产生额外费用)
- 删除 Aurora cluster 时选 "Delete automated backups"，否则备份会继续计费

---

## 前置准备

### 1. **AWS 账户和凭证** ✅ (你说已配置)
```bash
# 验证凭证是否正确配置
aws sts get-caller-identity
```

### 2. **Python 环境**
```bash
python3 --version  # 需要 3.8+
pip3 install boto3  # DynamoDB 和 EC2 SDK
```

### 3. **AWS Console 收藏**
- DynamoDB: https://console.aws.amazon.com/dynamodbv2/
- RDS (Aurora): https://console.aws.amazon.com/rds/
- VPC: https://console.aws.amazon.com/vpc/
- EC2: https://console.aws.amazon.com/ec2/
- Route 53: https://console.aws.amazon.com/route53/
- Billing: https://console.aws.amazon.com/billing/

### 4. **成本追踪**
在开始前，建议：
1. 在 AWS Billing Dashboard 中启用 **Cost Anomaly Detection**
2. 每天早上检查一下 "Estimated charges"
3. 完成每个 Track 后 **立即清理资源**

---

## 推荐顺序

**Day 1（4-5 小时）**：Track A（DynamoDB + Aurora）
- A1 完成后立即删除 DynamoDB table（或留着，费用很便宜）
- A4 的 Aurora 用完后**立即删除**（避免按小时扣费）

**Day 2（3-4 小时）**：Track B（VPC + Networking）
- B1-B5 之间**尽快完成**，减少 NAT Gateway 计费时间
- B6 清理：**NAT Gateway 最优先删除**

---

## 成本优化技巧

1. **使用 free tier**：EC2 t2.micro、DynamoDB 按需计费、RDS free tier 等
2. **合并操作**：不要边做边停，一次性完成一个 task
3. **及时删除**：
   - NAT Gateway：删除后 ~1 分钟立即停止计费
   - Aurora：删除后立即停止计费
   - Route 53：删除 hosted zone 立即停止计费
4. **监控**：打开 AWS Billing Dashboard，实时看费用

---

## 费用检查清单

在执行每个 hands-on task 前，打钩：

- [ ] 已验证 AWS credentials：`aws sts get-caller-identity`
- [ ] 已安装 boto3：`pip3 install boto3`
- [ ] 已在 AWS Billing Dashboard 设置支付方式
- [ ] 了解了 NAT Gateway / Aurora / Route 53 的计费
- [ ] 准备了一个"资源清理"的检查清单

---

## 下一步

→ 准备好了？开始 **Track A - A2_DynamoDB_Boto3** 的 Python 实操！
