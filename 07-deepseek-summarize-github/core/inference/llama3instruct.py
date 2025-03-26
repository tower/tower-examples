from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Any
from core.actions import Action

class InferWithLlama3Instruct(Action):

    def __init__(
            self,
            hf_token: str,
            device: str,
            actionname: str = None,
            ):
        super().__init__(actionname)
        self.hf_token = hf_token
        self.model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.device = device

        if self.device == "mps":
            # mps devices don't support bfloat16
            torch_dtype = torch.float16
        else:
            torch_dtype = torch.bfloat16

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch_dtype,
            device_map=self.device,
            token=self.hf_token
        )



    def do(self, messages, *args:Any, **kwargs: Any):

        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        output_tensors = self.model.generate(
            input_ids,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        top_output_tensors = output_tensors[0][input_ids.shape[-1]:]
        out = self.tokenizer.decode(top_output_tensors, skip_special_tokens=True)

        return out





