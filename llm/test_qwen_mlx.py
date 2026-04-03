from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler, make_logits_processors


MODEL_PATH = "./models/Qwen3.5-4B-MLX-4bit"

model, tokenizer = load(MODEL_PATH)

print("输入 exit 退出。")

sampler = make_sampler(temp=0.75, top_p=0.92, top_k=40)
logits_processors = make_logits_processors(repetition_penalty=1.12)

messages = [
    {
        "role": "system",
        "content": (
            "你是名为Zyra的个人助理，运行在用户电脑环境内。"
            "你的任务是帮助用户解决他们的问题。优先直接回答，不要过度展开。最好使用一两句话回答用户。"
            "请保持你的语言简洁、准确、自然。"
        )
    }
]

while True:
    prompt = input("\n> ").strip()
    if prompt.lower() in ["exit", "quit"]:
        break
    
    messages.append({"role": "user", "content": prompt})

    full_prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
        enable_thinking=False
    )

    print("🤖 ", end="", flush=True)
    for response in stream_generate(
        model,
        tokenizer,
        full_prompt,
        max_tokens=1024,
        sampler=sampler,
        logits_processors=logits_processors,
    ):
        print(response.text, end="", flush=True)
        
    messages.append({"role": "assistant", "content": response.text})

    print("\n")