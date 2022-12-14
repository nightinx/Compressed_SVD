import argparse
from datetime import datetime
from pathlib import Path

import metrics
import numpy as np
from dataset import mnist
from mlp import MLP
from utils import hash_model, save_model

DATASET = "mnist"


@metrics.timing
def main(args):
    epochs = args.epochs
    batch_size = args.batch_size
    train_set, valid_set, test_set = mnist(args.data_path, one_hot=True)
    X_train = train_set[0]
    Y_train = train_set[1]

    model = MLP(
        args.model_shape,
        batch_size=batch_size,
        lr=args.learning_rate,
        l2_lambda=args.l2_lambda,
    )

    metric = metrics.Metric()

    metric.add("time", datetime.now())
    metric.add("dataset", DATASET)
    metric.add("shape", args.model_shape)
    metric.add("batch_size", args.batch_size)
    metric.add("lr", args.learning_rate)
    metric.add("epochs", args.epochs)
    metric.add("l2_lambda", args.l2_lambda)

    if not Path(f"./saved/model-{DATASET}-{hash_model(args)}.pkl").exists():
        with metrics.Timer("Training") as t:
            for epoch in range(epochs):
                indexes = np.arange(len(X_train))
                steps = len(X_train) // batch_size
                np.random.shuffle(indexes)
                for i in range(steps):
                    ind = indexes[i * batch_size : (i + 1) * batch_size]
                    x = X_train[ind]
                    y = Y_train[ind]
                    loss = model(x, y)
                    model.backward()

                    if (i + 1) % 100 == 0:
                        accuracy = model.validate(valid_set[0], valid_set[1])
                        print(
                            "Epoch[{}/{}] \t Step[{}/{}] \t Loss = {:.6f} \t Acc = {:.3f}".format(
                                epoch + 1,
                                epochs,
                                i + 1,
                                steps,
                                loss,
                                accuracy,
                            )
                        )
                model.lr_step()

        metric.add("train_time", t.get(), "s")
        save_model(model=model, args=args, dataset=DATASET, base_path="./saved")
        metrics.run_metrics_original_model(metric, model)
        metric.save_to_csv("mnist_original.csv")
    else:
        print("Model already exists, skipping training")


parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", default=32, type=int)
parser.add_argument("--epochs", default=60, type=int)
parser.add_argument("--data_path", default="./data/mnist.pkl.gz")
parser.add_argument("--model_shape", default=[784, 20, 20, 10], type=list)
parser.add_argument("--learning_rate", default=0.01, type=float)
parser.add_argument("--l2_lambda", default=0.0, type=float)
args = parser.parse_args()

# trainable arguments:shape=[784, 300, 150, 75, 10], lr=0.01
# trainable arguments:shape=[784, 20, 20, 20, 10], lr=0.01
# trainable arguments:shape=[784, 20, 20, 10], lr=0.01, l2_lambda=0.01
main(args)
