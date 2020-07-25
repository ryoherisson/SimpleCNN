from tqdm import tqdm

from collections import OrderedDict

import torch


class Updater(object):
    def __init__(self, **kwargs):
        self.device = kwargs['device']
        self.network = kwargs['network']
        self.optimizer = kwargs['optimizer']
        self.criterion = kwargs['criterion']
        self.train_loader, self.test_loader = kwargs['data_loaders']
        self.metrics = kwargs['metrics']

    def train(self, n_epochs):

        for epoch in range(n_epochs):
            self.network.train()

            train_loss = 0
            n_correct = 0
            n_total = 0

            with tqdm(self.train_loader, ncols=100) as pbar:
                for idx, (inputs, targets) in enumerate(pbar):
                    inputs = inputs.to(self.device)
                    targets = targets.to(self.device)

                    outputs = self.network(inputs)

                    loss = self.criterion(outputs, targets)

                    loss.backward()

                    self.optimizer.step()
                    self.optimizer.zero_grad()

                    train_loss += loss.item()

                    pred = outputs.argmax(axis=1)
                    n_total += targets.size(0)
                    n_correct += (pred == targets).sum().item()

                    accuracy = 100.0 * n_correct / n_total

                    self.metrics.update(
                        preds=pred.cpu().detach().clone(),
                        targets=targets.cpu().detach().clone(),
                        loss=train_loss / (idx+1),
                        accuracy=accuracy,
                    )

                    ### logging train loss and accuracy
                    pbar.set_postfix(OrderedDict(
                        epoch="{:>10}".format(epoch),
                        loss="{:.4f}".format(train_loss / (idx+1)),
                        acc="{:.4f}".format(accuracy)))

            print(f'train loss: {train_loss}')
            print(f'train accuracy: {accuracy}')

            self.metrics.calc_metrics(epoch, mode='train')

            self.test(epoch)

    def test(self, epoch):
        self.network.eval()
    
        test_loss = 0
        n_correct = 0
        n_total = 0
        preds_t = torch.tensor([])

        with torch.no_grad():
            with tqdm(self.test_loader, ncols=100) as pbar:
                    for idx, (inputs, targets) in enumerate(pbar):

                        inputs = inputs.to(self.device)
                        targets = targets.to(self.device)

                        outputs = self.network(inputs)

                        loss = self.criterion(outputs, targets)

                        self.optimizer.zero_grad()

                        test_loss += loss.item()

                        pred = outputs.argmax(axis=1)
                        n_total += targets.size(0)
                        n_correct += (pred == targets).sum().item()

                        accuracy = 100.0 * n_correct / n_total

                        ### logging test loss and accuracy
                        pbar.set_postfix(OrderedDict(
                            epoch="{:>10}".format(epoch),
                            loss="{:.4f}".format(test_loss),
                            acc="{:.4f}".format(accuracy)))

            print(f'test loss: {test_loss}')
            print(f'test accuracy: {accuracy}\n')


    def _save_ckpt(self):
        pass