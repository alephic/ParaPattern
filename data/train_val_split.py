import sys
import argparse
import os.path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('input', type=str)
    p.add_argument('-v', '--num-val', type=int, default=0)
    p.add_argument('-t', '--num-test', type=int, default=0)
    args = p.parse_args()
    d = os.path.dirname(args.input)
    ext = os.path.splitext(args.input)[1]
    with open(args.input) as f:
        it = iter(f)
        if args.num_val > 0:
            with open(os.path.join(d, 'val'+ext), mode='w') as val_file:
                for i, ex in zip(range(args.num_val), it):
                    val_file.write(ex)
        if args.num_test > 0:
            with open(os.path.join(d, 'test'+ext), mode='w') as test_file:
                for i, ex in zip(range(args.num_test), it):
                    test_file.write(ex)
        with open(os.path.join(d, 'train'+ext), mode='w') as train_file:
            for ex in it:
                train_file.write(ex)

