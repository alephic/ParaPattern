cd "$(dirname $0)/.."
python3.8 -m torch.distributed.launch --nproc_per_node=1 \
	-m step_gen.finetune_trainer \
	--learning_rate=3e-5 \
	--fp16 \
	--save_total_limit 1 \
	--do_train \
	"$@"
