# A4：创建 Aurora Serverless Cluster 并运行 SQL

## 学习目标
- 在 AWS RDS 创建 Aurora Serverless v2 集群（最省钱的方式）
- 使用 RDS Query Editor 连接和运行 SQL
- 对比 DynamoDB 的 NoSQL 体验与 Aurora 的 SQL 能力

## 费用提醒 ⚠️
- **成本**：$0-1.00（最容易超预算的部分）
- **计费方式**：按 ACU-hour 计费（最小 0.5 ACU ≈ $0.22/小时）
- **关键**：完成后**立即删除** cluster（不是暂停），避免持续扣费
- **删除时**：选 "Delete automated backups"

## 操作步骤

### 1. 创建 Aurora Serverless v2 Cluster
- [ ] 打开 AWS Console → RDS
- [ ] 点 "Create database"
- [ ] 配置：
  ```
  Engine: Aurora (PostgreSQL-compatible)
  DB cluster identifier: music-db
  Master username: admin
  Master password: (自己设置，至少 8 字符，记住！)
  
  Instance class: Serverless
  Capacity range:
    Min: 0.5 ACU
    Max: 1 ACU
  (保持最小，学习用)
  
  Connectivity:
    Public accessibility: Yes
    (便于用 Query Editor 连接)
  
  Storage: 默认即可（最小 20 GB）
  Backup: 可以关掉（这是学习，不需要恢复）
  ```
- [ ] 等待 cluster 启动（~10 分钟）

### 2. 用 RDS Query Editor 连接
- [ ] 进入刚创建的 cluster
- [ ] 点 "Query Editor" 标签页
- [ ] 连接参数自动填充，输入你的 master password
- [ ] 点 "Connect" 测试连接

### 3. 运行 SQL

#### 3.1 创建表
```sql
CREATE TABLE music_library (
    artist VARCHAR(100) NOT NULL,
    song_title VARCHAR(200) NOT NULL,
    rating INT,
    release_year INT,
    PRIMARY KEY (artist, song_title)
);

CREATE INDEX idx_year ON music_library(release_year);
```

#### 3.2 插入数据
```sql
INSERT INTO music_library (artist, song_title, rating, release_year) VALUES
('The Beatles', 'Hey Jude', 5, 1968),
('The Beatles', 'Let It Be', 4, 1970),
('Queen', 'Bohemian Rhapsody', 5, 1975),
('Queen', 'Don''t Stop Me Now', 4, 1978),
('David Bowie', 'Space Oddity', 5, 1969),
('Pink Floyd', 'Comfortably Numb', 5, 1979),
('Led Zeppelin', 'Stairway to Heaven', 5, 1971);
```

#### 3.3 简单查询
```sql
-- 查询所有
SELECT * FROM music_library;

-- 按艺术家查询
SELECT * FROM music_library WHERE artist = 'The Beatles';

-- 按年份范围查询
SELECT * FROM music_library WHERE release_year BETWEEN 1970 AND 1980;
```

#### 3.4 复杂查询（DynamoDB 做不到！）
```sql
-- JOIN 示例（虽然现在只有一张表，但演示语法）
SELECT artist, COUNT(*) as song_count, AVG(rating) as avg_rating
FROM music_library
GROUP BY artist
ORDER BY avg_rating DESC;

-- 排名查询
SELECT artist, song_title, rating,
       RANK() OVER (PARTITION BY artist ORDER BY rating DESC) as rank_by_artist
FROM music_library;

-- 查询高分歌曲
SELECT artist, song_title, rating
FROM music_library
WHERE rating >= 4
ORDER BY release_year DESC;
```

#### 3.5 更新和删除
```sql
-- 更新
UPDATE music_library 
SET rating = 5 
WHERE artist = 'Pink Floyd' AND song_title = 'Comfortably Numb';

-- 删除
DELETE FROM music_library 
WHERE artist = 'David Bowie';
```

## 观察和思考

### Aurora vs DynamoDB

| 特性 | DynamoDB | Aurora |
|------|----------|--------|
| 插入 5 条数据 | `put_item` × 5（需要代码） | `INSERT` × 1（SQL 语句） |
| 按年份范围查询 | 需要 Scan + FilterExpression | `WHERE release_year BETWEEN...` |
| 统计（如 COUNT） | 无原生支持 | `SELECT COUNT(*)` |
| GROUP BY | 无 | 完全支持 |
| 查询耗时 | 毫秒级（如果 key 设计好） | 毫秒级 |
| 可伸缩性 | 超大规模（无上限） | 中等（受实例大小限制） |
| 一致性 | 最终一致 | 强一致 |

### DynamoDB 不支持的操作
```
-- 这些在 Aurora 里 5 秒搞定，在 DynamoDB 里无法用原生 API 实现：

1. 统计
   SELECT COUNT(*) FROM music_library;

2. 聚合
   SELECT artist, AVG(rating) FROM music_library GROUP BY artist;

3. 复杂排序
   SELECT * FROM music_library ORDER BY rating DESC, release_year ASC;

4. 子查询
   SELECT * FROM music_library 
   WHERE rating > (SELECT AVG(rating) FROM music_library);
```

## 完成标志
- [ ] 成功创建 Aurora Serverless cluster
- [ ] 用 Query Editor 连接
- [ ] 运行了所有 5 个 SQL 示例
- [ ] 观察并记录了 Aurora 查询的结果
- [ ] **重要**：完成后删除 cluster（避免费用继续扣）

## 删除 Cluster（必做！）
```
RDS Console → Databases → music-db
→ Actions → Delete
→ 选 "I want to delete this DB instance"
→ 关掉 "Create final snapshot"
→ 关掉 "Retain automated backups"
→ Delete
```

## 笔记空间

### Aurora 相比 DynamoDB 的优势
（记录你在 3.4 复杂查询中看到的便利...）

### 如果用 DynamoDB，这些查询应该怎么做？
（思考 GROUP BY、统计、复杂排序的替代方案...）

### 性能和成本的感受
（这 1 小时的 Aurora 费用与 A2 Python 的费用对比...）
