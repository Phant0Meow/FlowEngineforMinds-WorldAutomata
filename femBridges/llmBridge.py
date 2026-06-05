"""
femBridge/llmBridge.py —— FEM 通用 LLM 桥接器
================================================
自动加载 .env，通过 llm_providers 统一调用多家大模型。
支持浏览器传入 API Key / URL，或自动检测 .env 中已有的密钥。
代码原则：所有代码不许写try静默兜底不报错，有错必须报错。
"""

import os
import threading
import sys
from femBridges.llmProviders import stream_chat, detect_provider, get_provider_config


# 供应商列表（名称与 llm_providers 保持一致）
PROVIDER_LIST = {
    "deepseek": {"env_prefix": "DEEPSEEK"},
    "glm": {"env_prefix": "GLM"},
    "kimi": {"env_prefix": "KIMI"},
    "minimax": {"env_prefix": "MINIMAX"},
    "claude": {"env_prefix": "CLAUDE"},
    "gemini": {"env_prefix": "GEMINI"},
    "mimo": {"env_prefix": "MIMO"},
    "baidu": {"env_prefix": "BAIDU"},
    "qianwen": {"env_prefix": "QIANWEN"},
    "hunyuan": {"env_prefix": "HUNYUAN"},
    "spark": {"env_prefix": "SPARK"},
    "openai": {"env_prefix": "OPENAI"},
}


# ── 0. 加载根目录的 .env ──
def _load_dotenv():
    """自动从项目根目录加载 .env（带简单降级）"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    dotenv_path = os.path.join(root_dir, ".env")

    if not os.path.exists(dotenv_path):
        print(f"[llmBridge] ⚠️ 未找到 .env 文件: {dotenv_path}")
        return

    # 简易解析器（兼容等号前后空格、引号）
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key not in os.environ:
                os.environ[key] = value

    # 打印已加载的提供商（部分隐藏）
    loaded = [p for p, cfg in PROVIDER_LIST.items()
              if os.getenv(f"{cfg['env_prefix']}_API_KEY")]
    if loaded:
        print(f"[llmBridge] 🏠 已从 .env 加载提供商: {', '.join(loaded)}")

_load_dotenv()




def call_ai_with_blocks(
    blocks: dict,
    model: str = "default",
    stream_callback=None,
    user_api_key: str = None,
    user_api_provider: str = None,
    user_api_url: str = None,
    stop_event: threading.Event = None,
) -> str:
    """
    输入：blocks 字典
    输出：AI 完整回复文本，同时可通过 stream_callback 实现流式输出
    """

    # ── 0.5 确保当前线程有事件循环（线程池内需要）──
    import asyncio as _asyncio
    try:
        _asyncio.get_running_loop()
    except RuntimeError:
        _asyncio.set_event_loop(_asyncio.new_event_loop())

    # ── 1. 组装 prompt ──
    try:
        from prompt_assembler import assemble
        system_prompt, user_prompt = assemble(blocks)
    except ImportError:
        system_prompt = "\n\n".join(filter(None, [
            blocks.get('basic_safety', ''),
            blocks.get('basic_output', ''),
            blocks.get('soul', ''),
            blocks.get('user_info', ''),
        ]))
        context = blocks.get('context', '')
        prompt = blocks.get('prompt', '')
        memory = blocks.get('memory', '')

        parts = [context, prompt]
        if memory:
            parts.append("---\n[回忆]\n根据以上情况，你偶然回忆起了以下记忆，可能有用也可能无用：")
            parts.append(memory)
            parts.append(prompt)  # 提醒当前任务

        user_prompt = "\n\n".join(filter(None, parts))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # ── 2. 确定 API 密钥与提供者 ──
    # 如果用户指定了 provider，用指定的；否则自动检测 .env 中第一个可用的
    if user_api_provider and user_api_provider in PROVIDER_LIST:
        provider = user_api_provider
    else:
        provider = detect_provider()
        if not provider:
            print("[llmBridge] ❌ 未检测到任何 API Key，请设置 .env 文件或在浏览器中填写")
            return None

    # 是否使用浏览器传入的 Key / URL（两者都可选）
    if user_api_key:
        print(f"[llmBridge] 🌐 使用浏览器传入的 API Key (provider={provider})")
    else:
        print(f"[llmBridge] 🏠 使用本地 .env 中的 {PROVIDER_LIST[provider]['env_prefix']}_API_KEY")

    # ── 3. 调用统一流式生成器 ──
    try:
        generator = stream_chat(
            provider=provider,
            messages=messages,
            system_prompt=system_prompt,
            deep_think=(model != "default"),   # 保留原逻辑：非 default 则开启深度思考
            sampling_params={},
            stop_event=stop_event,
            api_key=user_api_key,       # 可选，浏览器传入
            api_url=user_api_url,       # 可选，浏览器传入
        )
    except Exception as e:
        print(f"[llmBridge] ❌ 启动流式请求失败: {e}")
        return None

    # ── 4. 流式接收并处理 ──
    answer = ""
    thinking = ""
    response_started = False

    try:
        for chunk in generator:
            # 检查停止信号
            if stop_event and stop_event.is_set():
                print("[llmBridge] 收到停止信号，中断流式输出")
                break

            if isinstance(chunk, dict):
                if chunk.get("type") == "response_start":
                    response_started = True
                continue

            if isinstance(chunk, str):
                if not response_started and chunk.strip():
                    response_started = True
                if response_started:
                    answer += chunk
                    if stream_callback:
                        stream_callback(chunk)
                else:
                    thinking += chunk

        # ── 5. 日志输出（可注释掉） ──
        soul_name = ""
        actor_info = blocks.get('_actor_info', {})
        if actor_info and 'soul' in actor_info:
            try:
                from femCompiler.db_utils import get_soul_by_id
                soul = get_soul_by_id(str(actor_info['soul']))
                if soul:
                    soul_name = soul.get('soul_name', '')
            except Exception:
                pass
        if not soul_name:
            soul_block = blocks.get('soul', '')
            import re
            match = re.search(r'名字[：:]\s*(\S+)', soul_block)
            if match:
                soul_name = match.group(1)
        tag = soul_name if soul_name else "AI"

        #print(f"[{tag}]:")
        #if thinking:
        #    print("-思考-:")
        #    print(thinking)
        #    print("-回答-:")
        #print(answer)

        return answer

    except Exception as e:
        print(f"[llmBridge] ❌ 流式请求失败: {e}")
        return None
