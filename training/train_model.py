
import os
import torch

from datasets import load_dataset
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


# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

MODEL_NAME = "google/gemma-3-1b-it"

PROJECT_DIR = "/content/AI_Resume_Analyser"

TRAIN_FILE = os.path.join(
    PROJECT_DIR, "dataset", "train.jsonl"
)

VALIDATION_FILE = os.path.join(
    PROJECT_DIR, "dataset", "validation.jsonl"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR, "models", "soura-resume-ai-lora"
)

MAX_LENGTH = 1024


# ==========================================
# 2. CHECK GPU
# ==========================================

if not torch.cuda.is_available():
    raise RuntimeError(
        "GPU not detected. Enable GPU in Google Colab."
    )

print("GPU detected:", torch.cuda.get_device_name(0))


# ==========================================
# 3. CHECK DATASET FILES
# ==========================================

if not os.path.exists(TRAIN_FILE):
    raise FileNotFoundError(TRAIN_FILE)

if not os.path.exists(VALIDATION_FILE):
    raise FileNotFoundError(VALIDATION_FILE)


# ==========================================
# 4. LOAD TOKENIZER
# ==========================================

print("Loading tokenizer...")

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

print(dataset)


# ==========================================
# 6. PREPARE TRAINING TEXT
# ==========================================

def format_example(example):

    messages = example["messages"]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

    return {"text": text}


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
# 7. 4-BIT QUANTIZATION
# ==========================================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)


# ==========================================
# 8. LOAD GEMMA BASE MODEL
# ==========================================

print("Loading Gemma 3:1b...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16
)

model.config.use_cache = False

model = prepare_model_for_kbit_training(
    model
)


# ==========================================
# 9. CONFIGURE LORA
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

training_args = TrainingArguments(

    output_dir=OUTPUT_DIR,

    num_train_epochs=3,

    per_device_train_batch_size=1,

    per_device_eval_batch_size=1,

    gradient_accumulation_steps=4,

    learning_rate=2e-4,

    fp16=True,

    logging_steps=5,

    save_strategy="epoch",

    save_total_limit=2,

    warmup_ratio=0.03,

    weight_decay=0.01,

    gradient_checkpointing=True,

    report_to="none",

    optim="paged_adamw_8bit"
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

print("\nStarting Soura Resume AI training...\n")

trainer.train()


# ==========================================
# 14. EVALUATE MODEL
# ==========================================

print("\nEvaluating trained model...")

evaluation = trainer.evaluate()

print("Evaluation results:", evaluation)


# ==========================================
# 15. SAVE TRAINED MODEL
# ==========================================

print("\nSaving trained LoRA adapter...")

model.save_pretrained(OUTPUT_DIR)

tokenizer.save_pretrained(OUTPUT_DIR)

print("\n================================")
print("SOURA RESUME AI TRAINING COMPLETE")
print("================================")

print("Saved model:", OUTPUT_DIR)
