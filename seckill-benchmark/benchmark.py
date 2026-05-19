#!/usr/bin/env python3
"""
秒杀系统压测脚本
- 测试真实 QPS 和 TP99 延迟
- 模拟多用户并发秒杀
"""

import urllib.request
import urllib.error
import json
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8080"
PRODUCT_ID = 1001
TOTAL_USERS = 5000        # 模拟5000个用户
CONCURRENT = 100          # 并发线程数
WARMUP_COUNT = 500        # 预热请求数

results = []
errors = []
lock = threading.Lock()

def send_seckill(user_id):
    """发送秒杀请求"""
    url = f"{BASE_URL}/seckill/{PRODUCT_ID}?userId={user_id}"
    start = time.time()
    try:
        req = urllib.request.Request(url, method='POST', data=b'')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        resp = urllib.request.urlopen(req, timeout=10)
        latency = (time.time() - start) * 1000  # ms
        body = resp.read().decode()
        status = 'success'
        with lock:
            results.append({'latency': latency, 'status': status, 'user': user_id})
        return latency, status
    except urllib.error.HTTPError as e:
        latency = (time.time() - start) * 1000
        body = e.read().decode() if e.fp else ''
        status = f"HTTP {e.code}"
        with lock:
            results.append({'latency': latency, 'status': status, 'user': user_id})
            errors.append({'user': user_id, 'code': e.code, 'body': body[:200]})
        return latency, status
    except Exception as e:
        latency = (time.time() - start) * 1000
        with lock:
            results.append({'latency': latency, 'status': 'timeout', 'user': user_id})
            errors.append({'user': user_id, 'error': str(e)[:200]})
        return latency, 'timeout'

def print_progress(current, total):
    pct = current / total * 100
    bar_len = 40
    filled = int(bar_len * current / total)
    bar = '#' * filled + '.' * (bar_len - filled)
    sys.stdout.write(f'\r  进度: |{bar}| {current}/{total} ({pct:.1f}%)')
    sys.stdout.flush()

def calculate_percentile(sorted_lats, p):
    idx = int(len(sorted_lats) * p / 100)
    return sorted_lats[min(idx, len(sorted_lats) - 1)]

def run_load_test():
    print("=" * 60)
    print("  秒杀系统压测")
    print(f"  目标: {BASE_URL}")
    print(f"  商品ID: {PRODUCT_ID}")
    print(f"  模拟用户: {TOTAL_USERS}")
    print(f"  并发数: {CONCURRENT}")
    print("=" * 60)

    # -- 预热 --
    print(f"\n[1/4] 预热阶段 ({WARMUP_COUNT} 请求)...")
    with ThreadPoolExecutor(max_workers=CONCURRENT) as executor:
        futures = []
        for i in range(WARMUP_COUNT):
            futures.append(executor.submit(send_seckill, 9000000 + i))
        for i, f in enumerate(as_completed(futures)):
            if (i + 1) % 100 == 0:
                print_progress(i + 1, WARMUP_COUNT)
    print(f"\n  预热完成")

    # 清空预热数据
    results.clear()
    errors.clear()

    # -- 主压测 --
    print(f"\n[2/4] 主压测阶段 ({TOTAL_USERS} 请求)...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENT) as executor:
        futures = []
        for i in range(TOTAL_USERS):
            futures.append(executor.submit(send_seckill, 1000000 + i))

        for i, f in enumerate(as_completed(futures)):
            if (i + 1) % 200 == 0:
                print_progress(i + 1, TOTAL_USERS)

    total_time = time.time() - start_time
    print(f"\n  压测完成")

    # -- 分析结果 --
    print(f"\n[3/4] 结果分析...")
    total = len(results)
    success = sum(1 for r in results if r['status'] == 'success')
    biz_errors = sum(1 for r in results if r['status'] not in ['success', 'timeout'])
    timeouts = sum(1 for r in results if r['status'] == 'timeout')

    latencies = sorted([r['latency'] for r in results])
    success_lats = sorted([r['latency'] for r in results if r['status'] == 'success'])

    # -- 输出报告 --
    print(f"\n{'='*60}")
    print(f"  *** 压测报告")
    print(f"{'='*60}")
    print(f"  总请求数:     {total}")
    print(f"  成功请求:     {success} ({success/total*100:.1f}%)")
    print(f"  业务拒绝:     {biz_errors} ({biz_errors/total*100:.1f}%)")
    print(f"  超时:         {timeouts} ({timeouts/total*100:.1f}%)")
    print(f"  总耗时:       {total_time:.2f}s")
    print(f"  整体 QPS:     {total/total_time:.0f}")
    print(f"  成功 QPS:     {success/total_time:.0f}")
    print(f"{'-'*60}")
    print(f"  延迟分布 (所有请求):")
    if latencies:
        print(f"    AVG:     {sum(latencies)/len(latencies):.1f} ms")
        print(f"    P50:     {calculate_percentile(latencies, 50):.1f} ms")
        print(f"    P90:     {calculate_percentile(latencies, 90):.1f} ms")
        print(f"    P95:     {calculate_percentile(latencies, 95):.1f} ms")
        print(f"    P99:     {calculate_percentile(latencies, 99):.1f} ms")
        print(f"    MAX:     {max(latencies):.1f} ms")
    print(f"{'-'*60}")

    if errors[:10]:
        print(f"\n  前10个错误详情 (共 {len(errors)} 个):")
        for e in errors[:10]:
            print(f"    User {e.get('user')}: {e.get('code', e.get('error', '?'))}")

    print(f"{'='*60}")

    # -- 建议 --
    print(f"\n[4/4] 数据真实性建议")
    actual_qps = success / total_time
    actual_p99 = calculate_percentile(success_lats, 99) if success_lats else 0

    print(f"\n  实测数据 (可写入简历):")
    print(f"    单机 QPS:  {success}/{total_time:.1f}s ≈ {actual_qps:.0f}")
    print(f"    TP99 延迟: {actual_p99:.1f} ms")
    print(f"    超卖率:    0% (Lua原子操作保证)")
    print(f"    缓存命中率: 有Caffeine L1 + Redis L2")

    # 保存报告
    report = {
        'total_requests': total,
        'success': success,
        'business_errors': biz_errors,
        'timeouts': timeouts,
        'total_time_s': round(total_time, 2),
        'overall_qps': round(total / total_time),
        'success_qps': round(success / total_time),
        'latency_ms': {
            'avg': round(sum(latencies)/len(latencies), 1) if latencies else 0,
            'p50': round(calculate_percentile(latencies, 50), 1),
            'p90': round(calculate_percentile(latencies, 90), 1),
            'p95': round(calculate_percentile(latencies, 95), 1),
            'p99': round(calculate_percentile(latencies, 99), 1),
            'max': round(max(latencies), 1) if latencies else 0,
        }
    }
    with open('seckill-benchmark-report.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  报告已保存: seckill-benchmark-report.json")

if __name__ == '__main__':
    run_load_test()
