import unittest
import numpy as np
import os
import sys
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.video_processing.frame_sampler import FrameSampler
from ai_engine.video_processing.temporal_buffer import TemporalBuffer
from ai_engine.video_inference.aggregation import TemporalPredictionAggregator

class TestVideoProcessingPipeline(unittest.TestCase):
    """
    Validates temporal index slicing, sliding buffer queues, and prediction fusion math.
    """
    def setUp(self):
        self.sampler = FrameSampler(sequence_length=8)
        self.buffer = TemporalBuffer(buffer_size=4)

    def test_uniform_indices_slicing(self):
        """
        Sampler should correctly slice uniform indexes map.
        """
        indices = self.sampler.get_uniform_indices(total_frames=100)
        self.assertEqual(len(indices), 8)
        self.assertEqual(indices[0], 0)
        self.assertEqual(indices[-1], 99)

    def test_uniform_indices_padding(self):
        """
        Sampler should apply border zero-padding index repeats if total frames < sequence length.
        """
        indices = self.sampler.get_uniform_indices(total_frames=5)
        self.assertEqual(len(indices), 8)
        self.assertEqual(indices[-1], 4)

    def test_temporal_sliding_window_buffer(self):
        """
        Buffer queue should slide and keep exact length threshold.
        """
        for i in range(10):
            mock_frame = np.ones((100, 100, 3), dtype=np.uint8) * i
            self.buffer.push(mock_frame)
            
        self.assertTrue(self.buffer.is_full())
        seq = self.buffer.get_sequence()
        self.assertEqual(len(seq), 4)
        
        # Check that sliding removed older elements (should contain index values 6, 7, 8, 9)
        self.assertEqual(np.mean(seq[0]), 6)

    def test_prediction_fusion_math(self):
        """
        Aggregator should fuse scores accurately.
        """
        scores = [0.1, 0.2, 0.9, 0.8]
        res_mean = TemporalPredictionAggregator.aggregate_mean(scores, threshold=0.5)
        res_vote = TemporalPredictionAggregator.aggregate_majority_vote(scores, threshold=0.5)
        
        # Mean = 0.5 -> Classified FAKE since >= 0.5
        self.assertEqual(res_mean["prediction"], "FAKE")
        self.assertEqual(res_vote["prediction"], "FAKE") # 2/4 = 50% flagged, flags FAKE if > 40%

if __name__ == "__main__":
    unittest.main()
