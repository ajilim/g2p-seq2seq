# Copyright 2016 AC Technologies LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""Default Parameters class.
"""

import os

class Params(object):
  """Class with training parameters."""
  def __init__(self, model_dir, decode_flag=True, flags=None):
    if decode_flag:
      self.batch_size = 1
      self.tasks = """
    - class: DecodeText"""
      self.input_pipeline = """
class: DictionaryInputPipeline
params:
  test_path:
    """
      if flags:
        if flags.decode:
          self.input_pipeline += flags.decode
      else:
          self.input_pipeline += "tests/data/toydict.test"
    else:
      # Set default parameters first. Then update the parameters that pointed out
      # in flags.
      self.batch_size = 16
      self.max_epochs = 1
      self.eval_every_n_steps = 1000
      self.save_checkpoints_secs = None
      self.save_checkpoints_steps = 1
      self.hooks = """
- class: PrintModelAnalysisHook
- class: MetadataCaptureHook
- class: SyncReplicasOptimizerHook
- class: TrainSampleHook
  params:
    every_n_steps: 430
"""
      self.model_params = """
  attention.class: seq2seq.decoders.attention.AttentionLayerDot
  attention.params:
    num_units: 128
  bridge.class: seq2seq.models.bridges.ZeroBridge
  embedding.dim: 128
  encoder.class: seq2seq.encoders.BidirectionalRNNEncoder
  encoder.params:
    rnn_cell:
      cell_class: GRUCell
      cell_params:
        num_units: 128
      dropout_input_keep_prob: 0.8
      dropout_output_keep_prob: 1.0
      num_layers: 1
  decoder.class: seq2seq.decoders.AttentionDecoder
  decoder.params:
    rnn_cell:
      cell_class: GRUCell
      cell_params:
        num_units: 128
      dropout_input_keep_prob: 0.8
      dropout_output_keep_prob: 1.0
      num_layers: 1
  optimizer.name: Adam
  optimizer.params:
    epsilon: 0.0000008
  optimizer.learning_rate: 0.0001
  source.max_seq_len: 50
  source.reverse: false
  target.max_seq_len: 50"""
      vocab_gr_path = os.path.abspath(os.path.join(model_dir, "vocab.grapheme"))
      vocab_ph_path = os.path.abspath(os.path.join(model_dir, "vocab.phoneme"))
      self.model_params += """
  vocab_source: {}
  vocab_target: {}""".format(vocab_gr_path, vocab_ph_path)
      self.metrics = """
- class: LogPerplexityMetricSpec
- class: BleuMetricSpec
  params:
    separator: ' '
    postproc_fn: seq2seq_lib.data.postproc.strip_bpe"""
      self.input_pipeline = """
class: DictionaryInputPipeline
params:
  train_path:
    """
      if flags:
        self.batch_size = flags.batch_size
        self.eval_every_n_steps = flags.eval_every_n_steps
        self.max_epochs = flags.max_epochs
        self.save_checkpoints_secs = flags.save_checkpoints_secs
        self.save_checkpoints_steps = flags.save_checkpoints_steps
        if flags.hooks:
          self.hooks = flags.hooks
        if flags.model_params:
          self.model_params = flags.model_param
        if flags.metrics:
          self.metrics = flags.metrics
        self.input_pipeline += flags.train + "\n"
        if flags.valid:
          self.input_pipeline += "  valid_path:\n    " + flags.valid
        if flags.test:
          self.input_pipeline += "  test_path:\n    " + flags.test
      else:
        self.input_pipeline += """
    tests/data/toydict.train
  valid_path:
    tests/data/toydict.test
  test_path:
    tests/data/toydict.test"""
