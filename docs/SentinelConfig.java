package com.seckill.config;

import com.alibaba.csp.sentinel.annotation.aspectj.SentinelResourceAspect;
import com.alibaba.csp.sentinel.slots.block.RuleConstant;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRule;
import com.alibaba.csp.sentinel.slots.block.flow.FlowRuleManager;
import jakarta.annotation.PostConstruct;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.ArrayList;
import java.util.List;

/**
 * Sentinel 限流降级配置
 */
@Configuration
public class SentinelConfig {

    @Bean
    public SentinelResourceAspect sentinelResourceAspect() {
        return new SentinelResourceAspect();
    }

    @PostConstruct
    public void initFlowRules() {
        List<FlowRule> rules = new ArrayList<>();

        // 秒杀接口限流：单机 QPS 阈值 5000
        FlowRule seckillRule = new FlowRule();
        seckillRule.setResource("seckill");
        seckillRule.setGrade(RuleConstant.FLOW_GRADE_QPS);
        seckillRule.setCount(5000);
        seckillRule.setLimitApp("default");
        rules.add(seckillRule);

        // 查询接口限流
        FlowRule queryRule = new FlowRule();
        queryRule.setResource("seckill:result");
        queryRule.setGrade(RuleConstant.FLOW_GRADE_QPS);
        queryRule.setCount(10000);
        queryRule.setLimitApp("default");
        rules.add(queryRule);

        FlowRuleManager.loadRules(rules);
        System.out.println("【Sentinel】限流规则已加载：秒杀QPS=5000，查询QPS=10000");
    }
}
