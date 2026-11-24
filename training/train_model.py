import os
import sys
from pathlib import Path
import torch

# ==========================================
# 0. RESOLVE IMPORT SHADOWING
# ==========================================
# Prevent local 'training/datasets' folder from shadowing HuggingFace 'datasets' library
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir in sys.path:
    sys.path.remove(_script_dir)

# Ensure project root is in sys.path for internal modules
_project_root = os.path.abspath(os.path.join(_script_dir, ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from datasets import load_dataset
except ImportError as err:
    raise ImportError(
        f"Failed to load HuggingFace 'datasets' library: {err}\n"
        "Please run: pip install datasets"
    )

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training
    )
except ImportError as err:
    raise ImportError(
        f"Failed to import transformers/peft: {err}\n"
        "Please run: pip install transformers peft accelerate"
    )


# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

MODEL_NAME = "google/gemma-3-1b-it"

# Auto-detect project directory (Google Colab vs Local Windows/Linux)
if os.path.exists("/content/AI_Resume_Analyser"):
    PROJECT_DIR = "/content/AI_Resume_Analyser"
else:
    PROJECT_DIR = _project_root

TRAIN_FILE = os.path.join(
    PROJECT_DIR, "dataset", "train.jsonl"
)

VALIDATION_FILE = os.path.join(
    PROJECT_DIR, "dataset", "validation.jsonl"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR, "models", "resumind-ai-lora"
)

MAX_LENGTH = 1024


# ==========================================
# 2. CHECK HARDWARE & ACCELERATION
# ==========================================

has_cuda = torch.cuda.is_available()

if has_cuda:
    device_name = torch.cuda.get_device_name(0)
    print(f"GPU detected: {device_name}")
else:
    print("Notice: CUDA GPU not detected. Training will run on CPU or in Google Colab with GPU runtime.")


# ==========================================
# 3. VERIFY DATASET FILES
# ==========================================

if not os.path.exists(TRAIN_FILE):
    raise FileNotFoundError(
        f"Training dataset not found at: {TRAIN_FILE}\n"
        "Please ensure dataset/train.jsonl exists."
    )

if not os.path.exists(VALIDATION_FILE):
    raise FileNotFoundError(
        f"Validation dataset not found at: {VALIDATION_FILE}\n"
        "Please ensure dataset/validation.jsonl exists."
    )

print("Dataset paths verified:")
print(f" - Train: {TRAIN_FILE}")
print(f" - Validation: {VALIDATION_FILE}")


# ==========================================
# 4. LOAD TOKENIZER
# ==========================================

print(f"\nLoading tokenizer for {MODEL_NAME}...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.padding_side = "right"


# ==========================================
# 5. LOAD DATASET
# ==========================================

print("Loading resume datasets...")

dataset = load_dataset(
    "json",
    data_files={
        "train": TRAIN_FILE,
        "validation": VALIDATION_FILE
    }
)

print("Dataset summary:", dataset)


# ==========================================
# 6. PREPARE TRAINING TEXT & CHAT TEMPLATE
# ==========================================

def format_example(example):
    messages = example["messages"]

    # Use tokenizer's chat template or format messages as plain conversational text
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        try:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
            return {"text": text}
        except Exception:
            pass

    # Fallback message formatter
    formatted = []
    for msg in messages:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        formatted.append(f"<|start_header_id|>{role}<|end_header_id|>\n{content}<|eot_id|>")
    return {"text": "\n".join(formatted)}


dataset = dataset.map(format_example)


def tokenize_example(example):
    return tokenizer(
        example["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        add_special_tokens=False
    )


tokenized_dataset = dataset.map(
    tokenize_example,
    remove_columns=dataset["train"].column_names
)

print("Dataset preprocessing completed!")


# ==========================================
# 7. QUANTIZATION & MODEL CONFIGURATION
# ==========================================

use_4bit = False
bnb_config = None

if has_cuda:
    try:
        import bitsandbytes as bnb
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        use_4bit = True
        print("BitsAndBytes 4-bit NF4 quantization enabled.")
    except Exception as bnb_err:
        print(f"Notice: bitsandbytes not loaded ({bnb_err}). Using FP16.")


# ==========================================
# 8. LOAD GEMMA BASE MODEL
# ==========================================

print(f"\nLoading base model: {MODEL_NAME}...")

model_load_args = {
    "device_map": "auto" if has_cuda else "cpu"
}

if has_cuda:
    model_load_args["torch_dtype"] = torch.float16
    if use_4bit and bnb_config is not None:
        model_load_args["quantization_config"] = bnb_config

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    **model_load_args
)

model.config.use_cache = False

if use_4bit:
    model = prepare_model_for_kbit_training(model)


# ==========================================
# 9. CONFIGURE LORA ADAPTER
# ==========================================

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ]
)

model = get_peft_model(
    model,
    lora_config
)

print("\nLoRA trainable parameters:")
model.print_trainable_parameters()


# ==========================================
# 10. DATA COLLATOR
# ==========================================

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)


# ==========================================
# 11. TRAINING CONFIGURATION
# ==========================================

training_optimizer = "paged_adamw_8bit" if use_4bit else "adamw_torch"

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=has_cuda,
    logging_steps=5,
    save_strategy="epoch",
    save_total_limit=2,
    warmup_ratio=0.03,
    weight_decay=0.01,
    gradient_checkpointing=has_cuda,
    report_to="none",
    optim=training_optimizer
)


# ==========================================
# 12. CREATE TRAINER
# ==========================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator
)


# ==========================================
# 13. START TRAINING
# ==========================================

print("\nStarting Resumind AI model fine-tuning...\n")

trainer.train()


# ==========================================
# 14. EVALUATE MODEL
# ==========================================

print("\nEvaluating fine-tuned model...")

evaluation = trainer.evaluate()

print("Evaluation results:", evaluation)


# ==========================================
# 15. SAVE TRAINED MODEL
# ==========================================

print(f"\nSaving trained LoRA adapter to: {OUTPUT_DIR}...")

os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n=================================")
print("RESUMIND AI MODEL TRAINING COMPLETE")
print("=================================")
print(f"Saved LoRA adapter at: {OUTPUT_DIR}")
