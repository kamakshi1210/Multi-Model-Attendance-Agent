"""
Lightweight centroid-based multi-person tracker.

Drop-in replacement for deep-sort-realtime with the same API surface:
  - tracker.update_tracks(detections, frame=...)
  - tracker.delete_all_tracks()
  - track.is_confirmed()
  - track.time_since_update  (int, frames missed)
  - track.track_id           (int)
  - track.to_ltrb()          -> [x1, y1, x2, y2]

No torch / torchvision dependency. Uses only numpy (already installed).
"""

import numpy as np


class _Track:
    def __init__(self, track_id, bbox_ltrb, n_init=3):
        self.track_id = track_id
        self._ltrb = list(bbox_ltrb)
        self.time_since_update = 0
        self._hits = 1
        self._n_init = n_init

    def is_confirmed(self):
        return self._hits >= self._n_init

    def to_ltrb(self):
        return self._ltrb

    def _update(self, bbox_ltrb):
        alpha = 0.6
        self._ltrb = [alpha*n + (1-alpha)*o for n, o in zip(bbox_ltrb, self._ltrb)]
        self.time_since_update = 0
        self._hits += 1

    def _mark_missed(self):
        self.time_since_update += 1


class CentroidTracker:
    """
    Centroid-based multi-object tracker.
    Drop-in replacement for deep_sort_realtime.deepsort_tracker.DeepSort.
    """
    def __init__(self, max_age=60, n_init=3, **kwargs):
        self._max_age = max_age
        self._n_init = n_init
        self._tracks = {}
        self._next_id = 1

    def update_tracks(self, detections, frame=None):
        det_ltrbs = []
        for det in detections:
            bbox, conf, _ = det
            x, y, w, h = bbox
            det_ltrbs.append([x, y, x + w, y + h])

        unmatched_dets = set(range(len(det_ltrbs)))
        matched_track_ids = set()

        if self._tracks and det_ltrbs:
            track_ids = list(self._tracks.keys())
            tc = np.array([[(t._ltrb[0]+t._ltrb[2])/2, (t._ltrb[1]+t._ltrb[3])/2] for t in [self._tracks[i] for i in track_ids]])
            dc = np.array([[(l[0]+l[2])/2, (l[1]+l[3])/2] for l in det_ltrbs])
            dist = np.linalg.norm(tc[:, None] - dc[None, :], axis=2)
            THRESH = 120
            for _ in range(min(len(track_ids), len(det_ltrbs))):
                if dist.size == 0: break
                ti, di = np.unravel_index(dist.argmin(), dist.shape)
                if dist[ti, di] > THRESH: break
                tid = track_ids[ti]
                self._tracks[tid]._update(det_ltrbs[di])
                matched_track_ids.add(tid)
                unmatched_dets.discard(di)
                dist[ti, :] = np.inf
                dist[:, di] = np.inf

        for tid in list(self._tracks):
            if tid not in matched_track_ids:
                self._tracks[tid]._mark_missed()

        for d_idx in unmatched_dets:
            self._tracks[self._next_id] = _Track(self._next_id, det_ltrbs[d_idx], self._n_init)
            self._next_id += 1

        self._tracks = {tid: t for tid, t in self._tracks.items() if t.time_since_update <= self._max_age}
        return list(self._tracks.values())

    def delete_all_tracks(self):
        self._tracks.clear()
        self._next_id = 1
