import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from database import UserDatabase
from gacha_system import GachaSystem
from config import WELCOME_MESSAGE, HELP_MESSAGE, GACHA_SETTINGS

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 初始化数据库和抽卡系统
db = UserDatabase()
gacha = GachaSystem()

# 对话状态
WAITING_FOR_CODE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    # 直接显示抽卡菜单
    keyboard = [
        [
            InlineKeyboardButton("🎲 单抽 (120💎)", callback_data="single_pull"),
            InlineKeyboardButton("🎉 十连抽 (1200💎)", callback_data="ten_pull")
        ],
        [InlineKeyboardButton("💰 查看余额", callback_data="check_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 选择抽卡方式：",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助命令"""
    await update.message.reply_text(HELP_MESSAGE)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看钻石余额"""
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    message = f"""
💰 钻石余额：{stats['diamonds']:,} 💎

📊 抽卡统计：
• 总抽数：{stats['total_pulls']}
• 3星角色：{stats['stats']['3星']}个
• 2星角色：{stats['stats']['2星']}个
• 1星角色：{stats['stats']['1星']}个

🎯 保底进度：
• 距离3星保底：{stats['pulls_since_3star']}/200
• 距离2星保底：{stats['pulls_since_2star']}/10
"""
    await update.message.reply_text(message)

async def gacha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """单抽命令"""
    user_id = update.effective_user.id
    user_stats = db.get_user_stats(user_id)
    
    if user_stats['diamonds'] < GACHA_SETTINGS['单抽价格']:
        message = f"❌ 钻石不足！需要 {GACHA_SETTINGS['单抽价格']} 钻石，当前余额：{user_stats['diamonds']} 钻石"
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return
    
    # 执行抽卡
    rarity, character_name = gacha.single_pull(user_stats)
    
    # 扣除钻石
    db.spend_diamonds(user_id, GACHA_SETTINGS['单抽价格'])
    
    # 记录抽卡历史
    db.add_pull_history(user_id, rarity, character_name)
    
    # 格式化结果
    result = gacha.format_pull_result(rarity, character_name)
    
    # 获取角色图片
    image_url = gacha.get_character_image(rarity, character_name)
    
    # 根据稀有度选择不同的消息
    if rarity == "3星":
        message = f"🎉 恭喜！抽到了3星角色！\n\n{result}\n\n✨ 欧气满满！"
    elif rarity == "2星":
        message = f"🎊 不错哦！抽到了2星角色！\n\n{result}"
    else:
        message = f"📦 抽卡结果：\n\n{result}\n\n💪 继续加油！"
    
    # 添加返回按钮
    keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 如果有图片URL，尝试发送图片
    if image_url and image_url != "https://i.imgur.com/example1.jpg":
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=message,
                reply_markup=reply_markup
            )
        except:
            # 如果图片发送失败，只发送文字
            await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        # 没有图片或使用示例图片，只发送文字
        await update.message.reply_text(message, reply_markup=reply_markup)

async def tenpull(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """十连抽命令"""
    user_id = update.effective_user.id
    user_stats = db.get_user_stats(user_id)
    
    if user_stats['diamonds'] < GACHA_SETTINGS['十连价格']:
        message = f"❌ 钻石不足！需要 {GACHA_SETTINGS['十连价格']} 钻石，当前余额：{user_stats['diamonds']} 钻石"
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return
    
    # 执行十连抽
    results = gacha.ten_pull(user_stats)
    
    # 扣除钻石
    db.spend_diamonds(user_id, GACHA_SETTINGS['十连价格'])
    
    # 记录抽卡历史
    for rarity, character_name in results:
        db.add_pull_history(user_id, rarity, character_name)
    
    # 格式化结果
    result_message = gacha.format_ten_pull_results(results)
    
    # 检查是否有3星
    has_3star = any(rarity == "3星" for rarity, _ in results)
    if has_3star:
        result_message += "\n\n🎉 恭喜抽到3星角色！"
    
    # 添加返回按钮
    keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(result_message, reply_markup=reply_markup)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看统计信息"""
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    if stats['total_pulls'] == 0:
        await update.message.reply_text("📊 还没有抽卡记录哦！快去抽卡吧！")
        return
    
    # 计算概率
    total = stats['total_pulls']
    rate_3star = (stats['stats']['3星'] / total) * 100
    rate_2star = (stats['stats']['2星'] / total) * 100
    rate_1star = (stats['stats']['1星'] / total) * 100
    
    # 计算花费
    total_cost = total * GACHA_SETTINGS['单抽价格']
    
    message = f"""
📊 抽卡统计报告

🎯 总体统计：
• 总抽数：{total}
• 总花费：{total_cost:,} 💎

📈 获得统计：
• ⭐⭐⭐ 3星：{stats['stats']['3星']}个 ({rate_3star:.1f}%)
• ⭐⭐ 2星：{stats['stats']['2星']}个 ({rate_2star:.1f}%)
• ⭐ 1星：{stats['stats']['1星']}个 ({rate_1star:.1f}%)

🎁 保底进度：
• 距离3星保底：{stats['pulls_since_3star']}/200
• 距离2星保底：{stats['pulls_since_2star']}/10

💰 当前余额：{stats['diamonds']:,} 💎
"""
    await update.message.reply_text(message)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """按钮回调处理"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "single_pull":
        # 模拟单抽命令
        user_id = update.effective_user.id
        user_stats = db.get_user_stats(user_id)
        
        if user_stats['diamonds'] < GACHA_SETTINGS['单抽价格']:
            message = f"❌ 钻石不足！需要 {GACHA_SETTINGS['单抽价格']} 钻石，当前余额：{user_stats['diamonds']} 钻石"
            keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return
        
        # 执行抽卡
        rarity, character_name = gacha.single_pull(user_stats)
        
        # 扣除钻石
        db.spend_diamonds(user_id, GACHA_SETTINGS['单抽价格'])
        
        # 记录抽卡历史
        db.add_pull_history(user_id, rarity, character_name)
        
        # 格式化结果
        result = gacha.format_pull_result(rarity, character_name)
        
        if rarity == "3星":
            message = f"🎉 恭喜！抽到了3星角色！\n\n{result}\n\n✨ 欧气满满！"
        elif rarity == "2星":
            message = f"🎊 不错哦！抽到了2星角色！\n\n{result}"
        else:
            message = f"📦 抽卡结果：\n\n{result}\n\n💪 继续加油！"
        
        # 添加返回按钮
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    elif query.data == "ten_pull":
        # 模拟十连抽命令
        user_id = update.effective_user.id
        user_stats = db.get_user_stats(user_id)
        
        if user_stats['diamonds'] < GACHA_SETTINGS['十连价格']:
            message = f"❌ 钻石不足！需要 {GACHA_SETTINGS['十连价格']} 钻石，当前余额：{user_stats['diamonds']} 钻石"
            keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return
        
        # 执行十连抽
        results = gacha.ten_pull(user_stats)
        
        # 扣除钻石
        db.spend_diamonds(user_id, GACHA_SETTINGS['十连价格'])
        
        # 记录抽卡历史
        for rarity, character_name in results:
            db.add_pull_history(user_id, rarity, character_name)
        
        # 格式化结果
        result_message = gacha.format_ten_pull_results(results)
        
        # 检查是否有3星
        has_3star = any(rarity == "3星" for rarity, _ in results)
        if has_3star:
            result_message += "\n\n🎉 恭喜抽到3星角色！"
        
        # 添加返回按钮
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(result_message, reply_markup=reply_markup)
    
    elif query.data == "check_balance":
        # 查看余额
        user_id = update.effective_user.id
        stats = db.get_user_stats(user_id)
        
        message = f"💰 钻石余额：{stats['diamonds']:,} 💎"
        
        # 添加返回按钮
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    elif query.data == "back_to_menu":
        # 返回主菜单
        keyboard = [
            [
                InlineKeyboardButton("🎲 单抽 (120💎)", callback_data="single_pull"),
                InlineKeyboardButton("🎉 十连抽 (1200💎)", callback_data="ten_pull")
            ],
            [InlineKeyboardButton("💰 查看余额", callback_data="check_balance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎮 选择抽卡方式：",
            reply_markup=reply_markup
        )

async def sign_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """每日签到命令"""
    user_id = update.effective_user.id
    success, diamonds = db.daily_signin(user_id, reward=10000)
    if success:
        await update.message.reply_text(f"✅ 签到成功！获得10000钻石！\n💎 当前钻石余额：{diamonds}")
    else:
        await update.message.reply_text(f"❌ 今天已经签到过了！\n💎 当前钻石余额：{diamonds}")

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """兑换码命令"""
    await update.message.reply_text("🎁 请输入兑换码：")
    return WAITING_FOR_CODE

async def handle_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户输入的兑换码"""
    user_id = update.effective_user.id
    code = update.message.text.strip()
    
    success, message, diamonds = db.redeem_code(user_id, code)
    await update.message.reply_text(f"{message}\n💎 当前钻石余额：{diamonds}")
    
    return ConversationHandler.END

async def cancel_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消兑换码输入"""
    await update.message.reply_text("❌ 兑换码输入已取消")
    return ConversationHandler.END

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """测试图片发送功能"""
    test_image_url = "https://i.imgur.com/example1.jpg"
    message = "🖼️ 测试图片发送功能"
    
    keyboard = [[InlineKeyboardButton("🔙 返回", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_photo(
            photo=test_image_url,
            caption=message,
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 图片发送失败：{str(e)}\n\n当前只支持文字模式", reply_markup=reply_markup)

def main():
    """主函数"""
    # 直接使用Token
    token = "7674591472:AAEcXu0cDKQMHxkywt11g8NxEmXc8HWdqg8"
    
    # 创建应用
    application = Application.builder().token(token).build()
    
    # 兑换码对话处理器
    code_handler = ConversationHandler(
        entry_points=[CommandHandler("code", code_command)],
        states={
            WAITING_FOR_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel_code)]
    )
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("gacha", gacha_command))
    application.add_handler(CommandHandler("tenpull", tenpull))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("sign", sign_command))
    application.add_handler(CommandHandler("testimage", test_image))
    application.add_handler(code_handler)
    
    # 添加按钮回调处理器
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # 启动机器人
    logger.info("蔚蓝档案抽卡机器人启动中...")
    application.run_polling()

if __name__ == '__main__':
    main() 