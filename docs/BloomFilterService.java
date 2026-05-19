package com.seckill.service;

import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

/**
 * 布隆过滤器
 * 用于拦截非法请求，解决缓存穿透问题
 */
@Service
public class BloomFilterService {

    /**
     * 预计插入数据量：100万
     * 误判率：1%
     */
    private static final int EXPECTED_INSERTIONS = 1_000_000;
    private static final double FPP = 0.01;

    private BloomFilter<String> bloomFilter;

    @PostConstruct
    public void init() {
        bloomFilter = BloomFilter.create(
                Funnels.stringFunnel(StandardCharsets.UTF_8),
                EXPECTED_INSERTIONS,
                FPP
        );
        // 预加载商品ID
        bloomFilter.put("1001");
        bloomFilter.put("1002");
        bloomFilter.put("1003");
        System.out.println("【布隆过滤器】初始化完成，预计容量: " + EXPECTED_INSERTIONS + "，误判率: " + FPP);
    }

    /**
     * 判断商品ID是否可能存在
     */
    public boolean mightContain(String productId) {
        return bloomFilter.mightContain(productId);
    }

    /**
     * 添加商品ID
     */
    public void put(String productId) {
        bloomFilter.put(productId);
    }
}
