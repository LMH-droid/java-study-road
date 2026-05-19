# Java 学习之路

> 刘名豪 · 重庆移通学院 · 计算机科学与技术

Java 后端学习记录，包含日常练习、项目实践、性能压测等内容。

## 📁 目录结构

```
├── src/                  # 日常练习代码
│   ├── day01 - day14     # 每日学习内容
│   └── 项目              # 课程项目
├── seckill-benchmark/    # 秒杀系统压测工具与报告
│   ├── benchmark.py      # Python 并发压测脚本
│   └── seckill-benchmark-report.json  # 实测压测数据
├── docs/                 # 技术参考文档
│   ├── SentinelConfig.java    # Sentinel 限流降级配置
│   ├── CaffeineConfig.java    # Caffeine 本地缓存配置
│   ├── BloomFilterService.java # 布隆过滤器实现
│   └── deductStock.lua        # Redis Lua 原子扣库存脚本
└── README.md
```

## ⚡ 最新：秒杀系统压测

对自研秒杀系统使用 Python 多线程进行了真实压测。

**实测数据：**

| 指标 | 数值 |
|------|------|
| 总请求数 | 5000 |
| 成功数 | 5000 (100%) |
| 并发线程 | 100 |
| 实测 QPS | ~271 |
| P50 延迟 | 139ms |
| P99 延迟 | 1522ms |
| 超卖率 | **0%**（Lua 原子操作保证） |

**测试方法：**
- 工具：Python ThreadPoolExecutor 100 并发
- 预热 500 请求 → 主压 5000 请求
- 使用独立 userId，模拟真实秒杀场景
- 环境：本机 Windows + Redis + MySQL
- 改用 wrk/JMeter 直压 Tomcat 预期可达 1000+ QPS

## 🛠 技术栈

- Java 21 · Spring Boot 3.2 · Redis · MySQL
- Sentinel 限流 · Caffeine 缓存 · Kafka（待接）
- MyBatis Plus · Redisson · Hutool

## 📬 联系

- GitHub: [LMH-droid](https://github.com/LMH-droid)
- 博客: [yexiao.online](https://yexiao.online)
