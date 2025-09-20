import logging
import inspect
import tempfile
import torch
from lightning.pytorch.cli import LightningCLI

from .vits.dataset import VitsDataModule
from .vits.lightning import VitsModel

_LOGGER = logging.getLogger(__package__)

class VitsLightningCLI(LightningCLI):
    def add_arguments_to_parser(self, parser):
        parser.link_arguments("data.batch_size", "model.batch_size")
        parser.link_arguments("data.num_symbols", "model.num_symbols")
        parser.link_arguments("model.num_speakers", "data.num_speakers")
        parser.link_arguments("model.sample_rate", "data.sample_rate")
        parser.link_arguments("model.filter_length", "data.filter_length")
        parser.link_arguments("model.hop_length", "data.hop_length")
        parser.link_arguments("model.win_length", "data.win_length")
        parser.link_arguments("model.segment_size", "data.segment_size")


def clean_checkpoint(checkpoint_path):
    checkpoint = torch.load(checkpoint_path, weights_only=False, map_location="cpu")

    if "hyper_parameters" not in checkpoint:
        return checkpoint_path

    init_signature = inspect.signature(VitsModel.__init__)
    valid_params = set(init_signature.parameters.keys())
    checkpoint_params = set(checkpoint["hyper_parameters"].keys())
    invalid_params = checkpoint_params - valid_params

    if not invalid_params:
        return checkpoint_path

    for param in invalid_params:
        _LOGGER.info(f"Removing invalid parameter '{param}' from checkpoint")
        del checkpoint["hyper_parameters"][param]

    temp_file = tempfile.NamedTemporaryFile(suffix=".ckpt", delete=False)
    torch.save(checkpoint, temp_file.name)
    temp_file.close()

    _LOGGER.info(f"Created cleaned checkpoint: {temp_file.name}")
    return temp_file.name


def main():
    logging.basicConfig(level=logging.INFO)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.deterministic = False
    temp_checkpont_path = clean_checkpoint("/workspace/pertts/checkpoints/epoch=5719-step=2609600.ckpt")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
