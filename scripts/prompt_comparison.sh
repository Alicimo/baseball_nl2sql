dvc exp run --queue -S 'generate.prompt=prompts/prompt_1s.txt'
dvc exp run --queue -S 'generate.prompt=prompts/prompt_3s.txt'
dvc exp run --queue -S 'generate.prompt=prompts/prompt_CoT.txt'
