from telethon import TelegramClient, events
import re
import asyncio
from datetime import datetime

# 配置频道和对应购买金额
CHANNEL_CONFIG = {
    -1002104899401: 1,  # 频道小楚 ID和对应购买金额
    -1002359314806: 0.4,  # 频道偷拍王 ID和对应购买金额
    -1002328941401: 1,  # 频道 麦总 ID和对应购买金额
    -1001963400792: 1,  # 频道 pepe ID和对应购买金额
    -1002130593420: 1,  # 频道 pepe ID和对应购买金额
    -4563086475: 0.1,  # 频道 pepe ID和对应购买金额
}

BOT_USERNAME = '@GMGN_sol_bot'  # 机器人的用户名

API_ID = '20648755'  # 替换为你的 API_ID
API_HASH = 'c49dc59dd9bba26ef0983e1995cefbe1'  # 替换为你的 API_HASH
PHONE_NUMBER = '+8618327079228'  # 替换为你的手机号码

client = TelegramClient('session_name', API_ID, API_HASH)

# 合约地址的正则表达式
eth_regex = r'0x[a-fA-F0-9]{40}'  # 以太坊合约地址
sol_regex = r'[1-9A-HJ-NP-Za-km-z]{44}|[1-9A-HJ-NP-Za-km-z]{43}|[1-9A-HJ-NP-Za-km-z]{32}'  # Solana合约地址
combined_regex = f"({eth_regex}|{sol_regex})"  # 合并正则表达式

# 用于确认交易是否完成的全局变量
awaiting_confirmation = asyncio.Event()

# 用于存储已经处理过的合约地址
processed_addresses = {}


# 定时器功能：每隔十分钟报时
async def time_reporter():
    while True:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[报时] 当前时间: {now}")
        await asyncio.sleep(600)  # 延时10分钟


# 发送交易命令到机器人
async def send_trade_command(contract_address, buy_amount):
    buy_command = f"/buy {contract_address} {buy_amount}"
    print(f"发送交易命令: {buy_command}")

    # 获取机器人的实体
    bot = await client.get_entity(BOT_USERNAME)

    # 重置事件，确保等待新的交易结果
    awaiting_confirmation.clear()

    # 发送命令到机器人
    await client.send_message(bot, buy_command)

    # 等待交易结果
    print("等待交易结果...")
    await awaiting_confirmation.wait()  # 等待机器人回复确认


# 处理接收来自机器人的回复
@client.on(events.NewMessage(from_users=BOT_USERNAME))
async def bot_response_handler(event):
    global awaiting_confirmation

    response = event.text

    # 检查交易成功的标志
    if "✅ 交易成功" in response:
        print("交易成功，准备处理下一条交易")
        awaiting_confirmation.set()  # 设置事件完成状态
    else:
        print("交易未成功或正在处理中，等待进一步消息")


# 处理每个频道的消息
async def handler(event, channel_id, buy_amount):
    message = event.text
    print(f"收到频道 {channel_id} 的消息: {message}")

    # 查找所有合约地址
    matches = re.findall(combined_regex, message)
    if matches:
        print(f"检测到合约地址: {matches}")
        for contract_address in matches:
            # 检查该地址是否已经处理过
            if channel_id not in processed_addresses:
                processed_addresses[channel_id] = set()

            if contract_address not in processed_addresses[channel_id]:
                # 如果合约地址没有被处理过，发送交易命令
                await send_trade_command(contract_address, buy_amount)
                # 记录该地址已处理
                processed_addresses[channel_id].add(contract_address)
            else:
                print(f"地址 {contract_address} 已经在频道 {channel_id} 中处理过，跳过购买")
    else:
        print(f"频道 {channel_id} 中没有找到合约地址")


# 动态注册每个频道的监听事件
for channel_id, buy_amount in CHANNEL_CONFIG.items():
    @client.on(events.NewMessage(chats=channel_id))
    async def dynamic_handler(event, channel_id=channel_id, buy_amount=buy_amount):
        await handler(event, channel_id, buy_amount)


async def main():
    print("正在登录...")
    await client.start(PHONE_NUMBER)  # 启动并登录
    print("用户账号已登录，正在监听多个频道消息...")

    # 并行运行报时器和消息监听器
    await asyncio.gather(
        time_reporter(),
        client.run_until_disconnected()  # 持续运行并等待新的消息
    )


# 启动客户端并进入事件循环
with client:
    client.loop.run_until_complete(main())
