"""# Fine-tunning #1"""

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer
from transformers import pipeline
from google.colab import files
from peft import PeftModel


# Modelo base mistrall
model_name = "mistralai/Mistral-7B-v0.1"
# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Import BitsAndBytesConfig
from transformers import BitsAndBytesConfig

# Configuración de cuantificación (QLoRA)
fq_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

# Cargar modelo en 4-bit (QLoRA)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=fq_config,
    device_map="auto"
)

dataset = load_dataset(
    "json",
    data_files={
        "train": "train.jsonl",
        "validation": "validation.jsonl",
        "test": "test.jsonl"
    }
)

# Formatear dataset a texto continuo
def format_example(example):
    return {
        "text": f"""{example['instruction']}

Pregunta:
{example['input']}

Respuesta:
{example['output']}"""
    }

dataset_train = dataset["train"].map(format_example)
dataset_validation = dataset["validation"].map(format_example)

peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=[
        "q_proj","k_proj","v_proj","o_proj"],
    lora_dropout=0.05,bias="none",task_type="CAUSAL_LM",init_lora_weights="gaussian"
)
training_args = TrainingArguments(
    output_dir="./mistral-sql-test",
    # batch
    per_device_train_batch_size=2,per_device_eval_batch_size=2,gradient_accumulation_steps=2,
    # entrenamiento
    num_train_epochs=3,learning_rate=1e-4,warmup_steps=1,
    # regularización
    weight_decay=0.01,max_grad_norm=1.0,
    # estabilidad
    logging_steps=5,seed=42
)

# Trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset_train,
    eval_dataset=dataset_validation,
    peft_config=peft_config,
    args=training_args
)

# Entrenar
trainer.train()

# Guardar modelo
trainer.save_model("./mistral-sql-test")
print(trainer.eval_dataset)

# Re-initialize tokenizer
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer.pad_token = tokenizer.eos_token

# Re-define BitsAndBytesConfig for quantization
fq_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

# 1. Load the base model with quantization config
base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=fq_config,
    device_map="auto",
    offload_buffers=True # Added to mitigate OOM during loading
)

# 2. Load the fine-tuned adapter and attach it to the base model
model_for_inference = PeftModel.from_pretrained(base_model, "./mistral-sql-test")

# Ensure the model is in evaluation mode
model_for_inference.eval()

print("Model loaded successfully for inference!")

"""Now, you can create the text-generation pipeline using this `model_for_inference`."""

def generar_sql(question):

    prompt = f"""
Genera la consulta SQL correcta para la siguiente pregunta.

Question:
{question}

SQL:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    outputs = model_for_inference.generate(
        **inputs,
        max_new_tokens=200
    )

    sql = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return sql.split("SQL:")[-1].strip()

def exact_match(pred, gold):
    return int(pred.strip().lower() == gold.strip().lower())

import sqlite3

conn = sqlite3.connect("mi_base.db")
cursor = conn.cursor()

def execution_accuracy(pred_sql, gold_sql):

    try:
        pred = cursor.execute(pred_sql).fetchall()
        gold = cursor.execute(gold_sql).fetchall()

        return int(pred == gold)

    except:
        return 0

def error_rate(pred_sql):

    try:
        cursor.execute(pred_sql)
        return 0
    except:
        return 1
exact = 0
exec_acc = 0
errors = 0

test_data = dataset["test"]

for example in test_data:

    question = example["input"]
    gold_sql = example["output"]

    pred_sql = generar_sql(question)

    exact += exact_match(pred_sql, gold_sql)
    exec_acc += execution_accuracy(pred_sql, gold_sql)
    errors += error_rate(pred_sql)

n = len(test_data)

print("Total:", n)
print("Exact Match:", exact/n)
print("Execution Accuracy:", exec_acc/n)
print("Error Rate:", errors/n)



pipe = pipeline(
    "text-generation",
    model=model_for_inference, # Use the explicitly loaded model
    tokenizer=tokenizer,
    device=0 # Specify device if not handled by device_map automatically
)

prompt = """Genera la consulta SQL correcta para la siguiente pregunta.

Pregunta:
quiero saber cual es la actividad economica mas comun en bogota

Respuesta:
"""

result = pipe(prompt, max_new_tokens=200, do_sample=False)

print(result[0]["generated_text"])

import shutil

shutil.make_archive("mistral-sql-test", 'zip', "mistral-sql-test")


files.download("mistral-sql-test.zip")



base_model = "mistralai/Mistral-7B-v0.1"

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="cpu"
)

model = PeftModel.from_pretrained(
    model,
    "/content/mistral-sql-test"
)

model = model.merge_and_unload()

model.save_pretrained("/content/mistral_sql_merged")