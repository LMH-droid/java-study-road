-- 扣减库存的Lua脚本
-- KEYS[1]: 库存key (seckill:stock:商品ID)
-- KEYS[2]: 用户集合key (seckill:users:商品ID)
-- ARGV[1]: 用户ID
-- ARGV[2]: 购买数量（默认1）

local stockKey = KEYS[1]
local userKey = KEYS[2]
local userId = ARGV[1]
local quantity = tonumber(ARGV[2]) or 1

-- 1. 检查用户是否已经购买过
local hasPurchased = redis.call('sismember', userKey, userId)
if hasPurchased == 1 then
    return -2  -- -2表示重复购买
end

-- 2. 获取当前库存
local stock = redis.call('get', stockKey)
if not stock then
    return -3  -- -3表示商品不存在
end

stock = tonumber(stock)
if stock < quantity then
    return -1  -- -1表示库存不足
end

-- 3. 扣减库存
redis.call('decrby', stockKey, quantity)

-- 4. 记录购买用户
redis.call('sadd', userKey, userId)

return stock - quantity  -- 返回剩余库存