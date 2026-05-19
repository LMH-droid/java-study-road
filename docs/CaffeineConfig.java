package com.seckill.config;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Caffeine 本地缓存配置（L1 缓存）
 * 用于热点数据缓存，减少 Redis 压力
 */
@Configuration
public class CaffeineConfig {

    /**
     * 商品信息本地缓存
     */
    @Bean("productCache")
    public Cache<Long, Object> productCache() {
        return Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(30, TimeUnit.SECONDS)
                .recordStats()
                .build();
    }

    /**
     * 库存本地缓存
     */
    @Bean("stockCache")
    public Cache<String, Integer> stockCache() {
        return Caffeine.newBuilder()
                .maximumSize(500)
                .expireAfterWrite(10, TimeUnit.SECONDS)
                .recordStats()
                .build();
    }
}
